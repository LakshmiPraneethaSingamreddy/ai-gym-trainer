import math

class AngleCalculator:
    @staticmethod
    def calculate_angle(a, b, c):
        """
        Calculates angle ABC (in degrees)
        a, b, c are landmarks with x,y
        """
        ax, ay = a["x"], a["y"]
        bx, by = b["x"], b["y"]
        cx, cy = c["x"], c["y"]

        radians = math.atan2(cy - by, cx - bx) - math.atan2(ay - by, ax - bx)
        angle = abs(radians * 180.0 / math.pi)

        if angle > 180:
            angle = 360 - angle

        return angle

    @staticmethod
    def knee_angle(landmarks, side="left"):
        if side == "left":
            hip = landmarks[23]   # LEFT_HIP
            knee = landmarks[25]  # LEFT_KNEE
            ankle = landmarks[27] # LEFT_ANKLE
        else:
            hip = landmarks[24]
            knee = landmarks[26]
            ankle = landmarks[28]

        return AngleCalculator.calculate_angle(hip, knee, ankle)

    @staticmethod
    def hip_angle(landmarks, side="left"):
        if side == "left":
            shoulder = landmarks[11] # LEFT_SHOULDER
            hip = landmarks[23]      # LEFT_HIP
            knee = landmarks[25]     # LEFT_KNEE
        else:
            shoulder = landmarks[12]
            hip = landmarks[24]
            knee = landmarks[26]

        return AngleCalculator.calculate_angle(shoulder, hip, knee)
