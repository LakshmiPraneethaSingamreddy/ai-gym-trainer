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

        # Tuned thresholds for real-time webcam noise.
        self.bottom_threshold = 95
        self.top_threshold = 150
        self.direction_delta = 2

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

        # Use the more visible arm to reduce occlusion noise.
        elbow_angle = left_elbow_angle if left_vis >= right_vis else right_elbow_angle

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
            if self.min_elbow_angle < self.bottom_threshold:
                self.reached_bottom = True

            if moving_up and elbow_angle > self.top_threshold:
                self.state = PushupState.UP
                self.min_elbow_angle = 180

        self.last_elbow_angle = elbow_angle
        return self.state
