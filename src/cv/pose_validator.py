from typing import List
from mediapipe.python.solutions.pose import PoseLandmark

class PoseValidator:
    def __init__(self, visibility_threshold: float = 0.5, max_invalid_frames: int = 5):
        self.visibility_threshold = visibility_threshold
        self.max_invalid_frames = max_invalid_frames
        self.invalid_frame_count = 0

        # Critical joints for full-body validation
        self.required_landmarks = [
            PoseLandmark.LEFT_HIP,
            PoseLandmark.RIGHT_HIP,
            PoseLandmark.LEFT_SHOULDER,
            PoseLandmark.RIGHT_SHOULDER,
        ]

    def is_pose_valid(self, landmarks: List) -> bool:
        if landmarks is None:
            return self._invalidate()

        for lm_id in self.required_landmarks:
            lm = landmarks[lm_id.value]
            if lm.visibility < self.visibility_threshold:
                return self._invalidate()

        # Pose is valid
        self.invalid_frame_count = 0
        return True

    def _invalidate(self) -> bool:
        self.invalid_frame_count += 1
        if self.invalid_frame_count >= self.max_invalid_frames:
            return False
        return True
