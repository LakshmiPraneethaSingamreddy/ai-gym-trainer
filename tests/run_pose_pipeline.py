import cv2
from src.cv.camera import Camera
from src.cv.pose_detector import PoseDetector
from src.data.logger import LandmarkLogger
from src.exercise.squat_state_machine import SquatStateMachine
from src.ai.rep_counter import RepCounter
from src.ai.form_validator import SquatFormValidator
from src.ai.performance_scorer import PerformanceScorer


def main():
    cam = Camera()
    detector = PoseDetector()
    logger = LandmarkLogger() 
    squat_machine = SquatStateMachine() 
    rep_counter = RepCounter() 
    validator = SquatFormValidator()
    scorer = PerformanceScorer()


    while True:
        frame = cam.read()
        if frame is None:
            break

        detector.process(frame)
        landmarks = detector.extract_landmarks(frame)
        
        # print(type(landmarks), landmarks) to check if it is rejevting the bad poses or not


        if landmarks:
            squat_state = squat_machine.update(landmarks)
            print("Squat State:", squat_state.name)

            reps = rep_counter.update(squat_state.name)
            print("Reps:", reps)
            
            feedback = validator.validate(landmarks)
            print("Form Feedback:", feedback)

            rep_score = scorer.update(landmarks,squat_state.name,reps)
            if rep_score:
                print("Rep Completed!")
                print("Depth Score:", rep_score["depth_score"])
                print("Hip Score:", rep_score["hip_score"])
                print("Final Score:", rep_score["final_score"])
                print("Average Score:", scorer.get_average_score())
                print("-" * 40)
            

            logger.log(landmarks)
        frame = detector.draw_landmarks(frame)

        cv2.imshow("Phase 1 - Pose Pipeline", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    logger.close()
    cam.release()

if __name__ == "__main__":
    main()
