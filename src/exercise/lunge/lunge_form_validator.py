from src.ai.angles import AngleCalculator


class LungeFormValidator:
    def __init__(self):
        self.feedback = []

    def validate(self, landmarks):
        self.feedback.clear()

        if not landmarks:
            return ["No pose detected"]

        # Detect which leg is bending more (active leg)
        left_knee_angle = AngleCalculator.knee_angle(landmarks, side="left")
        right_knee_angle = AngleCalculator.knee_angle(landmarks, side="right")
        
        # Use the leg that is bending more (smaller angle = more bent)
        side = "left" if left_knee_angle < right_knee_angle else "right"
        
        if side == "left":
            knee = landmarks[25]  # LEFT_KNEE
            ankle = landmarks[27]  # LEFT_ANKLE
        else:
            knee = landmarks[26]  # RIGHT_KNEE
            ankle = landmarks[28]  # RIGHT_ANKLE

        # --- Angles ---
        knee_angle = AngleCalculator.knee_angle(landmarks, side=side)
        torso_angle = AngleCalculator.hip_angle(landmarks, side=side)

        # --- Rules ---

        # Depth (very lenient - almost any lunge depth is accepted)
        if knee_angle > 145:
            self.feedback.append("Lunge lower for better form 🦵")

        # Knee alignment (extra-loose tolerance)
        if knee["x"] < ankle["x"] - 0.40:
            self.feedback.append("Keep your front knee aligned over your toes ✨")

        # Upright torso (only trigger if extremely forward leaned)
        if torso_angle < 80:
            self.feedback.append("Keep your torso more upright 🏋️")

        if not self.feedback:
            self.feedback.append("Beautiful lunge technique! ⭐")

        return self.feedback
