from src.ai.angles import AngleCalculator


class PlankFormValidator:
    def __init__(self):
        self.feedback = []
        self.min_body_angle = 150
        self.hip_vertical_tolerance = 0.09

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

        # Allow a wider body-angle band so minor camera jitter does not spam feedback.
        if body_angle < self.min_body_angle:
            self.feedback.append("Keep your whole body in a strong line 💪")

        # Hip position check (avoid sagging)
        if hip["y"] > shoulder["y"] + self.hip_vertical_tolerance:
            self.feedback.append("Hips up! No sagging 📍")

        # Avoid piking
        if hip["y"] < shoulder["y"] - self.hip_vertical_tolerance:
            self.feedback.append("Lower those hips just a bit ⬇️")

        if not self.feedback:
            self.feedback.append("Rock-solid plank hold! 🔥")

        return self.feedback
