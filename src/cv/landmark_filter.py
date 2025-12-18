# src/cv/landmark_filter.py

from typing import List, Optional
import copy

class LandmarkFilter:
    def __init__(self, visibility_threshold: float = 0.5):
        """
        Filters MediaPipe landmarks based on visibility confidence.
        Low-confidence landmarks are replaced with the last valid value.
        """
        self.visibility_threshold = visibility_threshold
        self.prev_landmarks: Optional[List] = None

    def filter(self, landmarks: List):
        """
        Args:
            landmarks: List of MediaPipe landmarks for the current frame
        Returns:
            filtered_landmarks: List of stable landmarks
        """
        if landmarks is None:
            return self.prev_landmarks

        filtered = []

        for i, lm in enumerate(landmarks):
            if lm.visibility >= self.visibility_threshold:
                filtered.append(lm)
            else:
                # fallback to previous landmark if available
                if self.prev_landmarks is not None:
                    filtered.append(self.prev_landmarks[i])
                else:
                    filtered.append(lm)

        # store a deep copy to avoid mutation issues
        self.prev_landmarks = copy.deepcopy(filtered)
        return filtered
