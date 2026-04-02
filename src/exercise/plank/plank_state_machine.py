# plank_state_machine.py
from enum import Enum
from src.ai.angles import AngleCalculator


class PlankState(Enum):
    NOT_READY = 1
    HOLDING = 2
    BROKEN = 3


class PlankStateMachine:
    def __init__(self):
        self.min_body_angle = 156
        self.min_torso_lean = 30
        self.min_elbow_angle = 55
        self.max_elbow_angle = 138
        self.min_shoulder_lift = 0.02
        self.min_knee_lift = 0.015
        self.max_shoulder_hip_diff = 0.16

    def _side_visibility(self, landmarks, side):
        if side == "left":
            ids = [11, 13, 15, 25, 27]  # shoulder, elbow, wrist, knee, ankle
        else:
            ids = [12, 14, 16, 26, 28]

        vals = [landmarks[i].get("visibility", 0) for i in ids]
        return sum(vals) / len(vals)

    def update(self, landmarks):
        if not landmarks:
            return PlankState.NOT_READY

        left_vis = self._side_visibility(landmarks, "left")
        right_vis = self._side_visibility(landmarks, "right")
        side = "left" if left_vis >= right_vis else "right"

        if max(left_vis, right_vis) < 0.35:
            return PlankState.NOT_READY

        if side == "left":
            shoulder = landmarks[11]
            elbow = landmarks[13]
            wrist = landmarks[15]
            hip = landmarks[23]
            knee = landmarks[25]
            ankle = landmarks[27]
        else:
            shoulder = landmarks[12]
            elbow = landmarks[14]
            wrist = landmarks[16]
            hip = landmarks[24]
            knee = landmarks[26]
            ankle = landmarks[28]

        body_angle = AngleCalculator.calculate_angle(shoulder, hip, ankle)
        torso_lean = AngleCalculator.back_angle(landmarks, side)
        elbow_angle = AngleCalculator.calculate_angle(shoulder, elbow, wrist)

        elbow_supported = self.min_elbow_angle <= elbow_angle <= self.max_elbow_angle
        elbow_below_shoulder = elbow["y"] >= shoulder["y"] - 0.03
        shoulder_lifted = (elbow["y"] - shoulder["y"]) >= self.min_shoulder_lift
        knee_lifted = (elbow["y"] - knee["y"]) >= self.min_knee_lift
        shoulder_hip_aligned = (
            abs(shoulder["y"] - hip["y"]) <= self.max_shoulder_hip_diff
        )

        # HOLDING requires both:
        # 1) a near-straight shoulder-hip-ankle line
        # 2) a plank-like (horizontal-ish) torso orientation
        # 3) low-plank arm support posture (bent elbow under shoulder)
        if (
            body_angle >= self.min_body_angle
            and torso_lean >= self.min_torso_lean
            and elbow_supported
            and elbow_below_shoulder
            and shoulder_lifted
            and knee_lifted
            and shoulder_hip_aligned
        ):
            return PlankState.HOLDING

        return PlankState.BROKEN
