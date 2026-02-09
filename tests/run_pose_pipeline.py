import cv2
from src.exercise.jumping_jack.jumping_jack_exercise import JumpingJackExercise
from src.exercise.lunge.lunge_exercise import LungeExercise
from src.exercise.plank.plank_exercise import PlankExercise
from src.cv.camera import Camera
from src.cv.pose_detector import PoseDetector
from src.data.logger import LandmarkLogger
from src.exercise.squat.squat_exercise import SquatExercise
from src.exercise.pushup.pushup_exercise import PushupExercise
from src.exercise.exercise_registry import ExerciseRegistry


# choose exercise
ACTIVE_EXERCISE = "Pushup"  # Options: "Squat", "Pushup", "Lunge", "Plank", "JumpingJack"

def main():
    cam = Camera()
    detector = PoseDetector()
    logger = LandmarkLogger() 


    registry = ExerciseRegistry()
    registry.register(SquatExercise())
    registry.register(PushupExercise())
    registry.register(LungeExercise())
    registry.register(PlankExercise())
    registry.register(JumpingJackExercise())


    exercise = registry.get(ACTIVE_EXERCISE)


    while True:
        frame = cam.read()
        if frame is None:
            break

        detector.process(frame)
        landmarks = detector.extract_landmarks(frame)
        
        if landmarks:
            state = exercise.update(landmarks)
            reps = exercise.count_rep(state.name)
            feedback = exercise.validate_form(landmarks)
            score = exercise.score_rep(landmarks, state)

            print("Exercise:", exercise.name)
            print("State:", state.name)
            print("Reps:", reps)

            if feedback:
                print("Form Feedback:", feedback)

            if score:
                print("Score:", score)

            

        logger.log(landmarks)
        frame = detector.draw_landmarks(frame)

        cv2.imshow("AI Gym Trainer", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    logger.close()
    cam.release()

if __name__ == "__main__":
    main()
