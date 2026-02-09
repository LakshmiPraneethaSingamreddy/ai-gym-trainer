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

        if back_angle > 30:
            self.feedback.append("Keep your back straighter")

        # ---- Form Rules ----

        # Depth check
        if knee_angle > 100:
            self.feedback.append("Go deeper into the squat")

        # Hip hinge
        if hip_angle > 160:
            self.feedback.append("Sit back more — hinge at the hips")

        if not self.feedback:
            self.feedback.append("Good form ✅")

        return self.feedback
