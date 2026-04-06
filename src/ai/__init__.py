import math


class AngleCalculator:
    """Calculate body angles from landmarks for exercise form validation."""
    @staticmethod
    def calculate_angle(a, b, c):
        """Calculate angle ABC between three points in degrees.

        Args:
            a, b, c: Landmarks with x, y coordinates.

        Returns:
            float: Angle in degrees (0-180).
        """
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
    def back_angle(landmarks, side="left"):
        """Calculate torso lean angle relative to vertical.

        Args:
            landmarks: Pose landmarks.
            side: "left" or "right" side.

        Returns:
            float: Angle in degrees (0 = upright, higher = forward lean).
        """
        """
        Calculates torso lean angle relative to vertical.
        0Â° = perfectly upright
        Higher = more forward lean
        """
        if side == "left":
            shoulder = landmarks[11]  # LEFT_SHOULDER
            hip = landmarks[23]  # LEFT_HIP
        else:
            shoulder = landmarks[12]
            hip = landmarks[24]

        dx = shoulder["x"] - hip["x"]
        dy = hip["y"] - shoulder["y"]  # inverted because y grows downward

        angle = math.degrees(math.atan2(abs(dx), abs(dy)))
        return angle

    @staticmethod
    def knee_angle(landmarks, side="left"):
        """Calculate knee joint angle.

        Args:
            landmarks: Pose landmarks.
            side: "left" or "right" leg.

        Returns:
            float: Knee angle in degrees (0-180).
        """
        if side == "left":
            hip = landmarks[23]  # LEFT_HIP
            knee = landmarks[25]  # LEFT_KNEE
            ankle = landmarks[27]  # LEFT_ANKLE
        else:
            hip = landmarks[24]
            knee = landmarks[26]
            ankle = landmarks[28]

        return AngleCalculator.calculate_angle(hip, knee, ankle)

    @staticmethod
    def hip_angle(landmarks, side="left"):
        """Calculate hip joint angle.

        Args:
            landmarks: Pose landmarks.
            side: "left" or "right" leg.

        Returns:
            float: Hip angle in degrees.
        """
        if side == "left":
            shoulder = landmarks[11]  # LEFT_SHOULDER
            hip = landmarks[23]  # LEFT_HIP
            knee = landmarks[25]  # LEFT_KNEE
        else:
            shoulder = landmarks[12]
            hip = landmarks[24]
            knee = landmarks[26]

        return AngleCalculator.calculate_angle(shoulder, hip, knee)

    @staticmethod
    def elbow_angle(landmarks, side="left"):
        """Calculate elbow joint angle.

        Args:
            landmarks: Pose landmarks.
            side: "left" or "right" arm.

        Returns:
            float: Elbow angle in degrees (0-180).
        """
        if side == "left":
            shoulder = landmarks[11]  # LEFT_SHOULDER
            elbow = landmarks[13]  # LEFT_ELBOW
            wrist = landmarks[15]  # LEFT_WRIST
        else:
            shoulder = landmarks[12]
            elbow = landmarks[14]
            wrist = landmarks[16]

        return AngleCalculator.calculate_angle(shoulder, elbow, wrist)
