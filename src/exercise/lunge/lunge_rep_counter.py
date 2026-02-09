# lunge_rep_counter.py
class LungeRepCounter:
    def __init__(self):
        self.count = 0
        self.last_state = None

    def update(self, state):
        if self.last_state == "ASCENDING" and state == "STANDING":
            self.count += 1
        self.last_state = state
        return self.count
