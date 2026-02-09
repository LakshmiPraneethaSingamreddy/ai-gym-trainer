# plank_state_machine.py
from enum import Enum
from src.ai.angles import AngleCalculator

class PlankState(Enum):
    NOT_READY = 1
    HOLDING = 2
    BROKEN = 3

class PlankStateMachine:
    def update(self, landmarks):
        if not landmarks:
            return PlankState.NOT_READY

        shoulder = landmarks[11]  # LEFT_SHOULDER
        hip = landmarks[23]       # LEFT_HIP
        ankle = landmarks[27]    # LEFT_ANKLE

        body_angle = AngleCalculator.calculate_angle(
            shoulder, hip, ankle
        )

        # Straight body ≈ 170–180
        if body_angle >= 160:
            return PlankState.HOLDING

        return PlankState.BROKEN
