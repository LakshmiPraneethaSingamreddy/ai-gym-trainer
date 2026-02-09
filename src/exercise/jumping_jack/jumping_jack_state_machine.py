# jumping_jack_state_machine.py
from enum import Enum
import math
import time

class JackState(Enum):
    CLOSED = 1
    OPEN = 2


# class JumpingJackStateMachine:
#     def __init__(self):
#         self.state = JackState.CLOSED
#         self.open_frames = 0
#         self.closed_frames = 0

#     def update(self, landmarks):
#         lh = landmarks[15]  # LEFT_WRIST
#         rh = landmarks[16]  # RIGHT_WRIST

#         la = landmarks[27] # LEFT_ANKLE
#         ra = landmarks[28] # RIGHT_ANKLE

#         hand_dist = abs(lh["x"] - rh["x"])
#         foot_dist = abs(la["x"] - ra["x"])

#         is_open = hand_dist > 0.50 and foot_dist > 0.4
#         is_closed = hand_dist < 0.45 and foot_dist < 0.30

#         if is_open:
#             self.open_frames += 1
#             self.closed_frames = 0
#         elif is_closed:
#             self.closed_frames += 1
#             self.open_frames = 0

#         # if hand_dist > 0.65 and foot_dist > 0.4:
#         #     self.open_frames += 1
#         #     self.closed_frames = 0
#         # elif hand_dist < 0.35 and foot_dist < 0.25:
#         #     self.closed_frames += 1
#         #     self.open_frames = 0
#         # else:
#         #     self.open_frames = 0
#         #     self.closed_frames = 0

#         # Require stability (2–3 frames)
#         # if self.open_frames >= 2:
#         #     self.state = JackState.OPEN
#         # elif self.closed_frames >= 2:
#         #     self.state = JackState.CLOSED

#         if self.state == JackState.CLOSED and self.open_frames >= 2:
#             self.state = JackState.OPEN

#         elif self.state == JackState.OPEN and self.closed_frames >= 2:
#             self.state = JackState.CLOSED

#         return self.state


class JumpingJackStateMachine:
    def __init__(self):
        self.state = JackState.CLOSED
        self.max_hand_dist = 0.0
        self.max_foot_dist = 0.0

    def update(self, landmarks):
        lh = landmarks[15]   # LEFT_WRIST
        rh = landmarks[16]   # RIGHT_WRIST
        la = landmarks[27]   # LEFT_ANKLE
        ra = landmarks[28]   # RIGHT_ANKLE

        # Visibility check
        if (
            lh["visibility"] < 0.6 or rh["visibility"] < 0.6 or
            la["visibility"] < 0.6 or ra["visibility"] < 0.6
        ):
            return self.state

        hand_dist = abs(lh["x"] - rh["x"])
        foot_dist = abs(la["x"] - ra["x"])

        # Track peak opening
        self.max_hand_dist = max(self.max_hand_dist, hand_dist)
        self.max_foot_dist = max(self.max_foot_dist, foot_dist)

        # OPEN detection (peak reached)
        if self.state == JackState.CLOSED:
            if self.max_hand_dist > 0.55 and self.max_foot_dist > 0.35:
                self.state = JackState.OPEN

        # CLOSED detection (return)
        elif self.state == JackState.OPEN:
            if hand_dist < 0.35 and foot_dist < 0.25:
                self.state = JackState.CLOSED
                self.max_hand_dist = 0.0
                self.max_foot_dist = 0.0

        return self.state