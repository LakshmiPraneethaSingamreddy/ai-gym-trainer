from src.ai.angles import AngleCalculator

class PushupFormValidator:
    def validate(self, landmarks):
        feedback = []

        elbow = AngleCalculator.elbow_angle(landmarks)
        hip = AngleCalculator.hip_angle(landmarks)

        if elbow > 120:
            feedback.append("Go lower in your pushup")

        if hip < 150:
            feedback.append("Keep your hips straight")

        if not feedback:
            feedback.append("Good form ✅")

        return feedback