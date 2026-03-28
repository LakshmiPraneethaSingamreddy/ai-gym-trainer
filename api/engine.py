import threading
import time
import cv2
import numpy as np
import traceback

from src.cv.camera import Camera
from src.cv.pose_detector import PoseDetector

from src.exercise.exercise_registry import ExerciseRegistry
from src.exercise.squat.squat_exercise import SquatExercise
from src.exercise.pushup.pushup_exercise import PushupExercise
from src.exercise.lunge.lunge_exercise import LungeExercise
from src.exercise.plank.plank_exercise import PlankExercise
from src.exercise.jumping_jack.jumping_jack_exercise import JumpingJackExercise
from src.exercise.feedback_controller import FeedbackController

from src.session.workout_session import WorkoutSession

from src.gamification.player_profile import PlayerProfile
from src.gamification.xp_system import XPSystem
from src.gamification.level_system import LevelSystem
from src.gamification.badge_system import BadgeSystem


class WorkoutEngine:
    def __init__(self):
        self.running = False
        self.thread = None
        self._state_lock = threading.Lock()
        self._exercise_lock = threading.Lock()

        self.current_frame = None
        self.raw_frame = None           # Latest camera frame, no processing applied
        self.display_landmarks = []     # Screen-space landmarks (0-1) for canvas overlay
        self._frame_event = threading.Event()  # Signals WebSocket when a new frame is ready
        self.cam = None
        self.detector = None

        # Shared state for frontend
        self.state = {
            "reps": 0,
            "xp": 0,
            "xp_required": 100,
            "level": 1,
            "feedback": "",
            "exercise": "None",
            "badges": []
        }

        # Systems
        self.player = PlayerProfile()
        self.xp_system = XPSystem()
        self.level_system = LevelSystem()
        self.session = WorkoutSession()
        self.badge_system = BadgeSystem(self.player)
        self.feedback_controller = FeedbackController()

        self.unlocked_badges = set()
        self.recent_badges = []
        self.last_processing_error = ""

        # Prevent XP spam
        self.last_rep_count = 0

        # ✅ Single registry (no duplication)
        self.registry = ExerciseRegistry()
        self.registry.register(SquatExercise())
        self.registry.register(PushupExercise())
        self.registry.register(LungeExercise())
        self.registry.register(PlankExercise())
        self.registry.register(JumpingJackExercise())

        self.exercise = self.registry.get("Squat")

    def _reset_exercise_counter(self):
        if self.exercise and hasattr(self.exercise, "rep_counter") and hasattr(self.exercise.rep_counter, "reset"):
            self.exercise.rep_counter.reset()

    def _reset_session_state(self):
        self.last_rep_count = 0
        self.session = WorkoutSession()
        self.recent_badges = []
        self.unlocked_badges = set()

        # Reset exercise counters
        self._reset_exercise_counter()

    def set_exercise(self, exercise_name):
        selected_exercise = self.registry.get(exercise_name)
        if selected_exercise is None:
            selected_exercise = self.registry.get("Squat")

        with self._exercise_lock:
            self.exercise = selected_exercise
            selected_name = self.exercise.name

        # Always reset when start is requested to avoid stale progression.
        self._reset_session_state()

        with self._state_lock:
            self.state["exercise"] = selected_name
            self.state["reps"] = 0
            self.state["feedback"] = ""
            self.state["badges"] = []

        return selected_name

    def start(self):
        if not self.running:
            self.running = True

            self.cam = Camera()
            self.detector = PoseDetector()

            self.thread = threading.Thread(target=self.run_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False

        # Release camera early to unblock any pending frame read.
        if self.cam:
            self.cam.release()

        if self.thread is not None:
            self.thread.join(timeout=1)

        self.cam = None
        self.detector = None
        self.thread = None

        self.current_frame = None   # prevents freeze frame
        self.raw_frame = None
        self.display_landmarks = []
        self._frame_event.set()     # unblock any waiting WebSocket handler

    def run_loop(self):
        while self.running:
            cam = self.cam
            detector = self.detector
            if cam is None or detector is None:
                time.sleep(0.001)  # Reduce sleep
                continue

            try:
                frame = cam.read()
            except Exception:
                time.sleep(0.001)  # Reduce sleep
                continue

            if frame is None:
                continue

            # Store the raw frame immediately — WebSocket streams this with zero processing delay
            self.raw_frame = frame.copy()
            self._frame_event.set()

            try:
                detector.process(frame)

                # Capture screen-space landmarks (0-1 range) BEFORE coordinate normalization
                # These are used by the frontend canvas to draw the skeleton overlay
                if detector.results and detector.results.pose_landmarks:
                    self.display_landmarks = [
                        {"x": lm.x, "y": lm.y, "visibility": lm.visibility}
                        for lm in detector.results.pose_landmarks.landmark
                    ]
                else:
                    self.display_landmarks = []

                landmarks = detector.extract_landmarks(frame)

                frame = detector.draw_landmarks(frame)
                self.current_frame = frame

                if landmarks:
                    with self._exercise_lock:
                        exercise = self.exercise

                    state = exercise.update(landmarks)
                    state_name = state.name if hasattr(state, "name") else str(state)

                    reps = exercise.count_rep(state_name)
                    score = exercise.score_rep(landmarks, state)

                    feedback = None
                    if exercise.allow_feedback(state_name):
                        feedback = self.feedback_controller.update(
                            exercise,
                            state_name,
                            exercise.validate_form(landmarks)
                        )

                    # Update session
                    self.session.update(reps=reps, score=score, feedback=feedback)

                    # ✅ XP only on new rep
                    if reps > self.last_rep_count:
                        final_score = score.get("final_score", 0) if isinstance(score, dict) else 0
                        xp_gain = self.xp_system.calculate_xp({
                            "avg_score": final_score,
                            "total_reps": reps
                        })

                        self.player.add_xp(xp_gain)
                        self.level_system.check_level_up(self.player)

                        self.last_rep_count = reps

                    # ✅ Badges
                    new_badges = self.badge_system.evaluate({
                        "reps": reps,
                        "score": score
                    })

                    if new_badges:
                        with self._state_lock:
                            for badge in new_badges:
                                if badge.name not in self.unlocked_badges:
                                    self.unlocked_badges.add(badge.name)
                                    self.recent_badges.append(badge.name)

                    # ✅ Update shared state - lock only when needed
                    with self._state_lock:
                        self.state.update({
                            "reps": reps,
                            "xp": self.player.xp,
                            "level": self.player.level,
                            "xp_required": self.level_system.xp_needed(self.player.level),
                            "feedback": feedback[-1] if isinstance(feedback, list) else (feedback or ""),
                            "exercise": exercise.name,
                            "badges": list(self.recent_badges)
                        })
                else:
                    # No landmarks detected, still update state frequently
                    with self._state_lock:
                        # Keep existing state but update exercise name
                        if self.exercise:
                            self.state["exercise"] = self.exercise.name
                            
            except Exception as e:
                error_msg = traceback.format_exc(limit=2)
                print(f"❌ ERROR in run_loop: {error_msg}")
                self.last_processing_error = error_msg
                with self._state_lock:
                    self.state["feedback"] = f"Error: {str(e)}"
                # No sleep here - let loop continue fast

    def get_state(self):
        with self._state_lock:
            state_copy = self.state.copy()
            self.recent_badges = []  # clear after sending
            self.state["badges"] = []
            return state_copy

    def generate_frames(self):
        encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
        target_interval = 1.0 / 30  # cap stream at 30fps
        last_frame_time = 0

        while True:
            now = time.time()
            if now - last_frame_time < target_interval:
                time.sleep(0.005)
                continue
            last_frame_time = now

            if not self.running:
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(
                    frame,
                    "Camera Stopped",
                    (150, 240),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2
                )
            elif self.current_frame is not None:
                frame = self.current_frame.copy()
            else:
                continue

            _, buffer = cv2.imencode('.jpg', frame, encode_params)
            frame_bytes = buffer.tobytes()

            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
            )