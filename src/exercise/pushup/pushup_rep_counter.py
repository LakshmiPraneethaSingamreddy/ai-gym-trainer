class PushupRepCounter:
    def __init__(self):
        self.count = 0
        self.last_state = None
        self.valid_rep = False

    def reset(self):
        """Reset counter for a new workout session"""
        self.count = 0
        self.last_state = None
        self.valid_rep = False

    def update(self, state_name, reached_bottom):
        if reached_bottom:
            self.valid_rep = True

        if self.last_state == "DOWN" and state_name == "UP" and self.valid_rep:
            self.count += 1
            print(" Pushup completed! Total reps:", self.count)
            self.valid_rep = False  # reset for next rep

        self.last_state = state_name
        return self.count
