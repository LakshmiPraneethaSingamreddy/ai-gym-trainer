from enum import Enum
from src.ai.angles import AngleCalculator

class SquatState(Enum):
    STANDING = 1
    DESCENDING = 2
    BOTTOM = 3
    ASCENDING = 4

class SquatStateMachine:
    def __init__(self):
        self.state = SquatState.STANDING
        self.prev_knee_angle = None

    def update(self, landmarks):
        knee_angle = AngleCalculator.knee_angle(landmarks, "left")

        if self.prev_knee_angle is None:
            self.prev_knee_angle = knee_angle
            return self.state

        # Detect movement direction
        moving_down = knee_angle < self.prev_knee_angle
        moving_up = knee_angle > self.prev_knee_angle

        # State transitions
        if self.state == SquatState.STANDING:
            if moving_down:
                self.state = SquatState.DESCENDING

        elif self.state == SquatState.DESCENDING:
            if knee_angle < 90:
                self.state = SquatState.BOTTOM

        elif self.state == SquatState.BOTTOM:
            if moving_up:
                self.state = SquatState.ASCENDING

        elif self.state == SquatState.ASCENDING:
            if knee_angle > 160:
                self.state = SquatState.STANDING

        self.prev_knee_angle = knee_angle
        return self.state
