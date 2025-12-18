from typing import List, Optional
import copy

class TemporalSmoother:
    def __init__(self, alpha: float = 0.3):
        """
        Applies temporal smoothing to landmarks using EMA.
        """
        self.alpha = alpha
        self.prev_landmarks: Optional[List] = None

    def smooth(self, landmarks: List):
        if landmarks is None:
            return self.prev_landmarks

        if self.prev_landmarks is None:
            self.prev_landmarks = copy.deepcopy(landmarks)
            return landmarks

        smoothed = []

        for curr, prev in zip(landmarks, self.prev_landmarks):
            lm = copy.deepcopy(curr)

            lm.x = self.alpha * curr.x + (1 - self.alpha) * prev.x
            lm.y = self.alpha * curr.y + (1 - self.alpha) * prev.y
            lm.z = self.alpha * curr.z + (1 - self.alpha) * prev.z

            smoothed.append(lm)

        self.prev_landmarks = copy.deepcopy(smoothed)
        return smoothed
