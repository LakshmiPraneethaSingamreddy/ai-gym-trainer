
# from src.ai.angles import AngleCalculator

# class JumpingJackFormValidator:
#     def __init__(self):
#         self.feedback = []

#     def validate(self, landmarks):
#         self.feedback.clear()

#         if not landmarks:
#             return ["No pose detected"]

#         # --- Key landmarks ---
#         left_shoulder = landmarks[11]
#         right_shoulder = landmarks[12]
#         left_wrist = landmarks[15]
#         right_wrist = landmarks[16]
#         left_ankle = landmarks[27]
#         right_ankle = landmarks[28]

#         # --- Arm height check ---
#         avg_shoulder_y = (left_shoulder["y"] + right_shoulder["y"]) / 2
#         avg_wrist_y = (left_wrist["y"] + right_wrist["y"]) / 2

#         if avg_wrist_y > avg_shoulder_y:
#             self.feedback.append("Raise your arms fully overhead")

#         # --- Leg spread check ---
#         ankle_distance = abs(left_ankle["x"] - right_ankle["x"])

#         if ankle_distance < 0.35:
#             self.feedback.append("Jump wider with your legs")

#         if not self.feedback:
#             self.feedback.append("Good jumping jack form ✅")

#         return self.feedback


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

