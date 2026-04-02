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
        now = time.time()

        if state == "HOLDING":
            if self.start is None:
                self.start = now
        else:
            if self.start is not None:
                self.total += now - self.start
                self.start = None

        active_total = self.total
        if self.start is not None:
            active_total += now - self.start

        return round(active_total, 1)
