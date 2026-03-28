# jumping_jack_rep_counter.py
class JumpingJackRepCounter:
    def __init__(self):
        self.count = 0
        self.last_state = None

    def reset(self):
        """Reset counter for a new workout session"""
        self.count = 0
        self.last_state = None

    def update(self, state):
        if self.last_state == "OPEN" and state == "CLOSED":
            self.count += 1
        self.last_state = state
        return self.count
