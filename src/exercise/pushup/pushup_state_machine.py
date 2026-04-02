from enum import Enum
from src.ai.angles import AngleCalculator


class PushupState(Enum):
    UP = 1
    DOWN = 2


class PushupStateMachine:
    def __init__(self):
        self.state = PushupState.UP
        self.reached_bottom = False
        self.last_elbow_angle = None
        self.min_elbow_angle = 180
        self.is_knee_pushup = False
        self.min_torso_angle = 18

        # Tuned thresholds for real-time webcam noise.
        # Regular pushups usually read a little shallower than knee pushups,
        # so we keep two depth gates to avoid missing valid reps.
        self.regular_bottom_threshold = 120
        self.knee_bottom_threshold = 96
        self.top_threshold = 160
        self.knee_mode_knee_angle = 160
        self.direction_delta = 3

    def _side_visibility(self, landmarks, side):
        if side == "left":
            ids = [11, 13, 15]  # shoulder, elbow, wrist
        else:
            ids = [12, 14, 16]

        vals = [landmarks[i].get("visibility", 0) for i in ids]
        return sum(vals) / len(vals)

    def update(self, landmarks):
        left_elbow_angle = AngleCalculator.elbow_angle(landmarks, "left")
        right_elbow_angle = AngleCalculator.elbow_angle(landmarks, "right")
        left_vis = self._side_visibility(landmarks, "left")
        right_vis = self._side_visibility(landmarks, "right")
        left_knee_angle = AngleCalculator.knee_angle(landmarks, "left")
        right_knee_angle = AngleCalculator.knee_angle(landmarks, "right")

        # Use the more visible arm to reduce occlusion noise.
        side = "left" if left_vis >= right_vis else "right"
        elbow_angle = left_elbow_angle if side == "left" else right_elbow_angle
        knee_angle = left_knee_angle if side == "left" else right_knee_angle
        torso_angle = AngleCalculator.back_angle(landmarks, side)

        # Keep the knee-pushup signal available without making it part of rep counting.
        self.is_knee_pushup = knee_angle < self.knee_mode_knee_angle

        if torso_angle < self.min_torso_angle:
            self.state = PushupState.UP
            self.reached_bottom = False
            self.min_elbow_angle = 180
            self.last_elbow_angle = elbow_angle
            return self.state

        if self.last_elbow_angle is None:
            self.last_elbow_angle = elbow_angle
            return self.state

        moving_down = elbow_angle < (self.last_elbow_angle - self.direction_delta)
        moving_up = elbow_angle > (self.last_elbow_angle + self.direction_delta)

        if self.state == PushupState.UP:
            if moving_down and elbow_angle < (self.top_threshold - 5):
                self.state = PushupState.DOWN
                self.reached_bottom = False
                self.min_elbow_angle = elbow_angle
        else:
            self.min_elbow_angle = min(self.min_elbow_angle, elbow_angle)
            bottom_threshold = (
                self.knee_bottom_threshold
                if self.is_knee_pushup
                else self.regular_bottom_threshold
            )
            if self.min_elbow_angle <= bottom_threshold:
                self.reached_bottom = True

            if moving_up and elbow_angle > self.top_threshold:
                self.state = PushupState.UP
                self.min_elbow_angle = 180

        self.last_elbow_angle = elbow_angle
        return self.state
