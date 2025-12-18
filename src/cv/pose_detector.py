import cv2
import mediapipe as mp
from src.cv.landmark_filter import LandmarkFilter
class PoseDetector:
    def __init__(self,
                 static_image_mode=False,
                 model_complexity=1,
                 smooth_landmarks=True,
                 detection_confidence=0.5,
                 tracking_confidence=0.5):

        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            smooth_landmarks=smooth_landmarks,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.landmark_filter = LandmarkFilter(visibility_threshold=0.5)
        self.results = None

    def process(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(rgb)
        return self.results

    def draw_landmarks(self, frame):
        if self.results and self.results.pose_landmarks:
            self.mp_draw.draw_landmarks(
                frame,
                self.results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS
            )
        return frame
    def extract_landmarks(self, frame):
        landmarks = []

        if not self.results or not self.results.pose_landmarks:
            return landmarks

        h, w, _ = frame.shape
        pose_landmarks = self.landmark_filter.filter(self.results.pose_landmarks.landmark)
        # pose_landmarks = self.results.pose_landmarks.landmark
        for idx, lm in enumerate(pose_landmarks):
            landmarks.append({
                "id": idx,
                "x": lm.x,
                "y": lm.y,
                "z": lm.z,
                "visibility": lm.visibility,
                "x_px": int(lm.x * w),
                "y_px": int(lm.y * h)
            })
        return landmarks
