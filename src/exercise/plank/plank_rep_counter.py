# plank_rep_counter.py
import time

class PlankTimer:
    def __init__(self):
        self.start = None
        self.total = 0

    def reset(self):
        """Reset timer for a new workout session"""
        self.start = None
        self.total = 0

    def update(self, state):
        if state == "HOLDING":
            if not self.start:
                self.start = time.time()
        else:
            if self.start:
                self.total += time.time() - self.start
                self.start = None

        return round(self.total, 1)
