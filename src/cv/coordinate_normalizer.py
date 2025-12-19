import math
import mediapipe as mp

class CoordinateNormalizer:
    def __init__(self, epsilon=1e-6):
        """
        epsilon: small value to avoid division by zero
        """
        self.epsilon = epsilon
        self.mp_pose = mp.solutions.pose

    def _distance(self, p1, p2):
        return math.sqrt(
            (p1.x - p2.x) ** 2 +
            (p1.y - p2.y) ** 2 +
            (p1.z - p2.z) ** 2
        )

    def normalize(self, landmarks):
        """
        landmarks: list of MediaPipe landmarks (after smoothing & validation)
        returns: list of normalized landmarks
        """

        if not landmarks:
            return landmarks

        # ---- Step 1: Hip center (origin) ----
        left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP]
        right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP]

        hip_center_x = (left_hip.x + right_hip.x) / 2
        hip_center_y = (left_hip.y + right_hip.y) / 2
        hip_center_z = (left_hip.z + right_hip.z) / 2

        # ---- Step 2: Shoulder center ----
        left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]

        shoulder_center_x = (left_shoulder.x + right_shoulder.x) / 2
        shoulder_center_y = (left_shoulder.y + right_shoulder.y) / 2
        shoulder_center_z = (left_shoulder.z + right_shoulder.z) / 2

        # ---- Step 3: Torso length (scale) ----
        torso_length = math.sqrt(
            (shoulder_center_x - hip_center_x) ** 2 +
            (shoulder_center_y - hip_center_y) ** 2 +
            (shoulder_center_z - hip_center_z) ** 2
        )

        torso_length = max(torso_length, self.epsilon)

        # ---- Step 4: Normalize all landmarks ----
        normalized_landmarks = []

        for lm in landmarks:
            lm.x = (lm.x - hip_center_x) / torso_length
            lm.y = (lm.y - hip_center_y) / torso_length
            lm.z = (lm.z - hip_center_z) / torso_length
            normalized_landmarks.append(lm)

        return normalized_landmarks
