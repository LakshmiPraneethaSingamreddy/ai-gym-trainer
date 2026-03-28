import cv2
from src.ui.hud import HUD
from src.exercise.jumping_jack.jumping_jack_exercise import JumpingJackExercise
from src.exercise.lunge.lunge_exercise import LungeExercise
from src.exercise.plank.plank_exercise import PlankExercise
from src.cv.camera import Camera
from src.cv.pose_detector import PoseDetector
from src.data.logger import LandmarkLogger
from src.exercise.squat.squat_exercise import SquatExercise
from src.exercise.pushup.pushup_exercise import PushupExercise
from src.exercise.exercise_registry import ExerciseRegistry
from src.exercise.feedback_controller import FeedbackController
from src.session.workout_session import WorkoutSession
from src.ui.workout_summary import WorkoutSummaryUI

from src.gamification.player_profile import PlayerProfile
from src.gamification.xp_system import XPSystem
from src.gamification.level_system import LevelSystem
from src.gamification.badge_system import BadgeSystem
from src.gamification.leaderboard_system import LeaderboardSystem

# choose exercise
ACTIVE_EXERCISE = "Squat"  # Options: "Squat", "Pushup", "Lunge", "Plank", "JumpingJack"

def main():
    cam = None
    logger = None
    
    try:
        cam = Camera()
        detector = PoseDetector()
        logger = LandmarkLogger()

        feedback_controller = FeedbackController()

        registry = ExerciseRegistry()
        registry.register(SquatExercise())
        registry.register(PushupExercise())
        registry.register(LungeExercise())
        registry.register(PlankExercise())
        registry.register(JumpingJackExercise())

        exercise = registry.get(ACTIVE_EXERCISE)

        session = WorkoutSession()
        summary_ui = WorkoutSummaryUI()

        player = PlayerProfile()
        xp_system = XPSystem()
        level_system = LevelSystem()
        badge_system = BadgeSystem(player)
        leaderboard = LeaderboardSystem()

        hud = HUD()

        previous_reps = 0  # Used to detect new rep
        live_xp_awarded = 0  # Track XP awarded during workout

        while True:
            try:
                frame = cam.read()
                if frame is None:
                    break

                detector.process(frame)
                landmarks = detector.extract_landmarks(frame)
                
                if landmarks:
                    state = exercise.update(landmarks)
                    reps = exercise.count_rep(state.name)
                    score = exercise.score_rep(landmarks, state)

                    print("Exercise:", exercise.name)
                    print("State:", state.name)
                    print("Reps:", reps)
                    
                    feedback = None
                    if exercise.allow_feedback(state.name):
                        feedback = feedback_controller.update(
                            exercise,
                            state.name,
                            exercise.validate_form(landmarks)
                        )

                    if feedback:
                        print("Feedback:", feedback)

                    if score:
                        print("Score:", score)
                    
                    # Update session ONLY during workout
                    session.update(reps=reps, score=score, feedback=feedback)

                    # 🔥 REAL-TIME XP UPDATE (only when a new rep is completed)
                    if reps > previous_reps:
                        rep_xp = xp_system.calculate_rep_xp(score)
                        player.add_xp(rep_xp)
                        level_system.check_level_up(player)
                        live_xp_awarded += rep_xp
                        previous_reps = reps

                    frame = hud.draw(
                        frame=frame,
                        exercise_name=exercise.name,
                        reps=reps,
                        state=state.name,
                        feedback=feedback,
                        score=score,
                        level=player.level,
                        xp=player.xp,
                        xp_required=level_system.xp_needed(player.level)
                    )

                logger.log(landmarks)
                frame = detector.draw_landmarks(frame)

                cv2.imshow("AI Gym Trainer", frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break

            except Exception as e:
                print(f"Error processing frame: {e}")
                continue

        # Finalizing workout and displaying the summary
        cv2.destroyWindow("AI Gym Trainer")
        
        summary = session.get_summary(exercise.name)

        # Updating stats after workout
        player.update_from_session(summary)

        # XP was already awarded live during workout
        print("Total XP Gained:", live_xp_awarded)
        print("Player Level:", player.level)
        print("Current XP:", player.xp)

        new_badges = badge_system.evaluate(summary)
        if new_badges:
            for badge in new_badges:
                print(f"🏆 Badge Unlocked: {badge.name}")
            hud.show_badges(new_badges)

        leaderboard.submit_workout(
            player_name=player.name,
            summary=summary,
            xp_gained=live_xp_awarded
        )

        final_leaderboard = leaderboard.get_weekly_leaderboard()

        # Save player progress
        player.save()

        # Displaying summary
        summary_frame = None
        while True:
            frame = cam.read()
            if frame is not None:
                summary_frame = frame
            
            if summary_frame is not None:
                display_frame = summary_ui.draw(
                    summary_frame,
                    summary,
                    final_leaderboard
                )
                cv2.imshow("Workout Summary", display_frame)
            
            key = cv2.waitKey(30) & 0xFF
            if key == ord('q') or key == 27:  # 'q' or ESC
                break

    except Exception as e:
        print(f"Critical error: {e}")
    
    finally:
        # Ensure cleanup always happens
        if logger:
            logger.close()
        if cam:
            cam.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()