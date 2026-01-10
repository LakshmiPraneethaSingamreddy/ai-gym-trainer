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
        shoulder = landmarks[11]  # LEFT_SHOULDER
        hip = landmarks[23]       # LEFT_HIP
        knee = landmarks[25]      # LEFT_KNEE
        back_angle = AngleCalculator.calculate_angle(shoulder, hip, knee)

        # ---- Form Rules ----

        # Depth check
        if knee_angle > 100:
            self.feedback.append("Go deeper into the squat")

        # Hip hinge
        if hip_angle > 160:
            self.feedback.append("Sit back more — hinge at the hips")

        # Back posture
        if back_angle < 150:
            self.feedback.append("Keep your back straighter")

        if not self.feedback:
            self.feedback.append("Good form ✅")

        return self.feedback
