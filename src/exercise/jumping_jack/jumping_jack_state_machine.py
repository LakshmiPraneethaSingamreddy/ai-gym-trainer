# jumping_jack_state_machine.py
from enum import Enum
import math
import time

class JackState(Enum):
    CLOSED = 1
    OPEN = 2

class JumpingJackStateMachine:
    def __init__(self):
        self.state = JackState.CLOSED
        self.max_hand_dist = 0.0
        self.max_foot_dist = 0.0

        self.min_hand_dist = 1.0 
        self.min_foot_dist = 1.0

    def update(self, landmarks):
        lh = landmarks[15]   # LEFT_WRIST
        rh = landmarks[16]   # RIGHT_WRIST
        la = landmarks[27]   # LEFT_ANKLE
        ra = landmarks[28]   # RIGHT_ANKLE

        # Visibility check
        if (
            lh["visibility"] < 0.4 or rh["visibility"] < 0.4 or
            la["visibility"] < 0.4 or ra["visibility"] < 0.4
        ):
            return self.state

        hand_dist = abs(lh["x"] - rh["x"])
        foot_dist = abs(la["x"] - ra["x"])

        # Track peak opening
        self.max_hand_dist = max(self.max_hand_dist, hand_dist)
        self.max_foot_dist = max(self.max_foot_dist, foot_dist)

        # OPEN detection (peak reached)
        if self.state == JackState.CLOSED:
            if self.max_hand_dist > 0.45 and self.max_foot_dist > 0.25:
                self.state = JackState.OPEN
                self.min_hand_dist = 1.0 
                self.min_foot_dist = 1.0

        # CLOSED detection (return)
        elif self.state == JackState.OPEN:
            self.min_hand_dist = min(self.min_hand_dist, hand_dist)
            self.min_foot_dist = min(self.min_foot_dist, foot_dist)
            if self.min_hand_dist < 0.45 and self.min_foot_dist < 0.25:
                self.state = JackState.CLOSED
                self.max_hand_dist = 0.0
                self.max_foot_dist = 0.0

        return self.state