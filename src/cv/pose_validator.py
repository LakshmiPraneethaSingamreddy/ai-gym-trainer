from typing import List

import mediapipe as mp

if not hasattr(mp, "solutions") or not hasattr(mp.solutions, "pose"):
    raise RuntimeError(
        "MediaPipe pose solutions module is unavailable in this environment."
    )

PoseLandmark = mp.solutions.pose.PoseLandmark

# Old layout fallback remains commented while deployment behavior is isolated.
# try:
#     from mediapipe.python.solutions.pose import PoseLandmark
# except ImportError:
#     class PoseLandmark(IntEnum):
#         LEFT_SHOULDER = 11
#         RIGHT_SHOULDER = 12
#         LEFT_HIP = 23
#         RIGHT_HIP = 24


class PoseValidator:
    def __init__(
        self, visibility_threshold: float = 0.25, max_invalid_frames: int = 10
    ):
        self.visibility_threshold = visibility_threshold  # Balanced
        self.max_invalid_frames = max_invalid_frames  # Reasonable tolerance
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
