class RepCounter:
    def __init__(self):
        self.count = 0
        self.last_state = None

    def update(self, current_state):
        # Count a rep when user comes back to standing from bottom
        if self.last_state == "ASCENDING" and current_state == "STANDING":
            self.count += 1
            print(" Rep completed! Total reps:", self.count)

        self.last_state = current_state
        return self.count
