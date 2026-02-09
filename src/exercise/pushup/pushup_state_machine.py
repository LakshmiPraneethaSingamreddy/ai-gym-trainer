from enum import Enum
from src.ai.angles import AngleCalculator

class PushupState(Enum):
    UP = 1
    DOWN = 2

class PushupStateMachine:
    def __init__(self):
        self.state = PushupState.UP
        self.reached_bottom = False

    def update(self, landmarks):
        # elbow_angle = AngleCalculator.elbow_angle(landmarks)
        left_elbow_angle = AngleCalculator.elbow_angle(landmarks, "left")
        right_elbow_angle = AngleCalculator.elbow_angle(landmarks, "right")

        # Pick the elbow that is bending more (visible lebow)
        if left_elbow_angle < right_elbow_angle:
            elbow_angle = left_elbow_angle
        else:
            elbow_angle = right_elbow_angle



        if elbow_angle < 80:
            self.state = PushupState.DOWN
            self.reached_bottom = True
        elif elbow_angle > 160:
            self.state = PushupState.UP

        return self.state
    