import cv2
from src.cv.camera import Camera
from src.cv.pose_detector import PoseDetector
from src.data.logger import LandmarkLogger

def main():
    cam = Camera()
    detector = PoseDetector()
    logger = LandmarkLogger()   

    while True:
        frame = cam.read()
        if frame is None:
            break

        detector.process(frame)
        landmarks = detector.extract_landmarks(frame)

        logger.log(landmarks)
        frame = detector.draw_landmarks(frame)

        cv2.imshow("Phase 1 - Pose Pipeline", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    logger.close()
    cam.release()

if __name__ == "__main__":
    main()
