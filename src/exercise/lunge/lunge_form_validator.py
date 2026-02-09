from src.ai.angles import AngleCalculator

class LungeFormValidator:
    def __init__(self):
        self.feedback = []

    def validate(self, landmarks):
        self.feedback.clear()

        if not landmarks:
            return ["No pose detected"]

        knee = landmarks[25]    # LEFT_KNEE
        ankle = landmarks[27]  # LEFT_ANKLE

        # --- Angles ---
        knee_angle = AngleCalculator.knee_angle(landmarks, side="left")
        torso_angle = AngleCalculator.hip_angle(landmarks, side="left")

        # --- Rules ---

        # Depth
        if knee_angle > 110:
            self.feedback.append("Go deeper into the lunge")

        # Knee alignment (rough inward collapse check)
        if knee["x"] < ankle["x"] - 0.05:
            self.feedback.append("Keep your front knee aligned over your foot")

        # Upright torso
        if torso_angle < 150:
            self.feedback.append("Keep your torso more upright")

        if not self.feedback:
            self.feedback.append("Good lunge form ✅")

        return self.feedback

