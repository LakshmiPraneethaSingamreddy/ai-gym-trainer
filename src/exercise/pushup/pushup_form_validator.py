from src.ai.angles import AngleCalculator

class PushupFormValidator:
    def _side_visibility(self, landmarks, side):
        if side == "left":
            ids = [11, 13, 15]
        else:
            ids = [12, 14, 16]

        vals = [landmarks[i].get("visibility", 0) for i in ids]
        return sum(vals) / len(vals)

    def validate(self, landmarks):
        feedback = []

        side = "left" if self._side_visibility(landmarks, "left") >= self._side_visibility(landmarks, "right") else "right"
        elbow = AngleCalculator.elbow_angle(landmarks, side)
        hip = AngleCalculator.hip_angle(landmarks, side)

        if elbow > 130:
            feedback.append("Go lower in your pushup")

        if hip < 150:
            feedback.append("Keep your hips straight")

        if not feedback:
            feedback.append("Good form ✅")

        return feedback