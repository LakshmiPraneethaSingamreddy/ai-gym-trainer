class JumpingJackFormValidator:
    def validate(self, landmarks):
        feedback = []

        lh = landmarks[15]
        rh = landmarks[16]
        la = landmarks[27]
        ra = landmarks[28]

        hand_dist = abs(lh["x"] - rh["x"])
        foot_dist = abs(la["x"] - ra["x"])

        if hand_dist < 0.4:
            feedback.append("Raise your arms fully")

        if foot_dist < 0.25:
            feedback.append("Jump wider with your legs")

        if not feedback:
            feedback.append("Good jumping jack form 👍")

        return feedback
