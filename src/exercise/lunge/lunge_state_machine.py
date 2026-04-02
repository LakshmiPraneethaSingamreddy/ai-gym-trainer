# lunge_state_machine.py
from enum import Enum
from src.ai.angles import AngleCalculator


class LungeState(Enum):
    STANDING = 1
    DESCENDING = 2
    BOTTOM = 3
    ASCENDING = 4


class LungeStateMachine:
    def __init__(self):
        self.state = LungeState.STANDING

    def update(self, landmarks):
        left_knee = AngleCalculator.knee_angle(landmarks, "left")
        right_knee = AngleCalculator.knee_angle(landmarks, "right")

        # Pick the leg that is bending more (front leg)
        if left_knee < right_knee:
            # active_leg = "left"
            knee = left_knee
        else:
            # active_leg = "right"
            knee = right_knee

        if self.state == LungeState.STANDING and knee < 155:
            self.state = LungeState.DESCENDING
        elif self.state == LungeState.DESCENDING and knee < 96:
            self.state = LungeState.BOTTOM
        elif self.state == LungeState.BOTTOM and knee > 104:
            self.state = LungeState.ASCENDING
        elif self.state == LungeState.ASCENDING and knee > 158:
            self.state = LungeState.STANDING

        return self.state
