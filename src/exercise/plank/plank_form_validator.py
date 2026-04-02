from src.ai.angles import AngleCalculator


class PlankFormValidator:
    def __init__(self):
        self.feedback = []

    def validate(self, landmarks):
        self.feedback.clear()

        if not landmarks:
            return ["No pose detected"]

        # Use LEFT side for consistency
        shoulder = landmarks[11]  # LEFT_SHOULDER
        hip = landmarks[23]  # LEFT_HIP
        ankle = landmarks[27]  # LEFT_ANKLE

        # --- Body alignment angle ---
        body_angle = AngleCalculator.calculate_angle(shoulder, hip, ankle)

        # Ideal plank ≈ 170–180 degrees
        if body_angle < 155:
            self.feedback.append("Keep your body in a straight line")

        # Hip position check (avoid sagging)
        if hip["y"] > shoulder["y"] + 0.06:
            self.feedback.append("Don't let your hips sag")

        # Avoid piking
        if hip["y"] < shoulder["y"] - 0.06:
            self.feedback.append("Lower your hips slightly")

        if not self.feedback:
            self.feedback.append("Strong plank posture 💪")

        return self.feedback
