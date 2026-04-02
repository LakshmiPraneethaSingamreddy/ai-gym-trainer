from src.ai.angles import AngleCalculator


class LungeFormValidator:
    def __init__(self):
        self.feedback = []

    def validate(self, landmarks):
        self.feedback.clear()

        if not landmarks:
            return ["No pose detected"]

        knee = landmarks[25]  # LEFT_KNEE
        ankle = landmarks[27]  # LEFT_ANKLE

        # --- Angles ---
        knee_angle = AngleCalculator.knee_angle(landmarks, side="left")
        torso_angle = AngleCalculator.hip_angle(landmarks, side="left")

        # --- Rules ---

        # Depth
        if knee_angle > 118:
            self.feedback.append("Lunge lower for better form 🦵")

        # Knee alignment (rough inward collapse check)
        # Loosened threshold to 0.12 to allow natural knee position variance
        if knee["x"] < ankle["x"] - 0.12:
            self.feedback.append("Front knee tracking over your toes ✨")

        # Upright torso
        if torso_angle < 145:
            self.feedback.append("Keep your torso more upright 🏋️")

        if not self.feedback:
            self.feedback.append("Beautiful lunge technique! ⭐")

        return self.feedback
