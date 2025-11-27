# src/starter.py
import cv2
import sys

def check_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera not available.")
        return 1
    ret, frame = cap.read()
    if not ret:
        print("Couldn't read frame from camera.")
        cap.release()
        return 1
    print("Camera OK. Frame shape:", frame.shape)
    cap.release()
    return 0

if __name__ == "__main__":
    sys.exit(check_camera())
