from src.ai.angles import AngleCalculator


class SquatFormValidator:
    def __init__(self):
        self.feedback = []

    def validate(self, landmarks):
        """
        Returns list of feedback messages based on squat posture
        """
        self.feedback.clear()

        if not landmarks:
            return ["No pose detected"]

        # Calculate angles using your existing AngleCalculator
        knee_angle = AngleCalculator.knee_angle(landmarks, side="left")
        hip_angle = AngleCalculator.hip_angle(landmarks, side="left")

        # Back angle (shoulder-hip-knee)
        back_angle = AngleCalculator.back_angle(landmarks)

        if back_angle > 34:
            self.feedback.append("Straighten that back a bit more 💪")

        # ---- Form Rules ----

        # Depth check
        if knee_angle > 108:
            self.feedback.append("Lower down further for a deeper squat ⬇️")

        # Hip hinge
        if hip_angle > 165:
            self.feedback.append("Push those hips back more 🔙")

        if not self.feedback:
            self.feedback.append("Excellent squat form! 🎯")

        return self.feedback
