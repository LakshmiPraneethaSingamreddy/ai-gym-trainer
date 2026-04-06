import cv2
import mediapipe as mp
from src.cv.landmark_filter import LandmarkFilter
from src.cv.temporal_smoother import TemporalSmoother
from src.cv.pose_validator import PoseValidator
from src.cv.coordinate_normalizer import CoordinateNormalizer


class PoseDetector:
    """Detect pose from RGB images using MediaPipe with filtering and smoothing."""
    def __init__(
        self,
        static_image_mode=False,
        model_complexity=0,
        smooth_landmarks=True,
        detection_confidence=0.5,
        tracking_confidence=0.5,
    ):
        self.mp_pose, self.mp_draw = self._resolve_mediapipe_modules()
        self.pose = self.mp_pose.Pose(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            smooth_landmarks=smooth_landmarks,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )
        # Slightly lower visibility threshold avoids dropping usable landmarks.
        self.landmark_filter = LandmarkFilter(visibility_threshold=0.25)
        # Higher alpha tracks motion faster, reducing rep transition lag.
        self.temporal_smoother = TemporalSmoother(alpha=0.5)
        self.results = None
        self.pose_validator = PoseValidator()
        self.coordinate_normalizer = CoordinateNormalizer()

    @staticmethod
    def _resolve_mediapipe_modules():
        """Resolve MediaPipe pose+drawing modules across package variants."""
        solutions_module = getattr(mp, "solutions", None)
        if solutions_module is not None:
            return solutions_module.pose, solutions_module.drawing_utils

        # Older MediaPipe layout fallback kept commented out while deployment behavior is isolated.
        # import_candidates = [
        #     (
        #         "mediapipe.python.solutions.pose",
        #         "mediapipe.python.solutions.drawing_utils",
        #     ),
        #     ("mediapipe.solutions.pose", "mediapipe.solutions.drawing_utils"),
        # ]
        #
        # for pose_module_path, drawing_module_path in import_candidates:
        #     try:
        #         pose_module = importlib.import_module(pose_module_path)
        #         drawing_module = importlib.import_module(drawing_module_path)
        #         return pose_module, drawing_module
        #     except Exception:
        #         continue

        raise RuntimeError(
            "MediaPipe solutions module is unavailable in this environment."
        )

    def process(self, frame):
        """Process frame and detect pose landmarks.

        Args:
            frame: BGR image frame.

        Returns:
            MediaPipe pose detection results.
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(rgb)
        return self.results

    def draw_landmarks(self, frame):
        if self.results and self.results.pose_landmarks:
            self.mp_draw.draw_landmarks(
                frame, self.results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS
            )
        return frame

    def extract_landmarks(self, frame):
        """Extract normalized landmarks from frame.

        Args:
            frame: BGR image frame.

        Returns:
            list: Normalized 3D landmark coordinates.
        """
        landmarks = []

        if not self.results or not self.results.pose_landmarks:
            return landmarks

        h, w, _ = frame.shape
        raw_landmarks = self.results.pose_landmarks.landmark
        filtered_landmarks = self.landmark_filter.filter(raw_landmarks)
        smoothed_landmarks = self.temporal_smoother.smooth(filtered_landmarks)
        is_valid_pose = self.pose_validator.is_pose_valid(smoothed_landmarks)
        # pose_landmarks = self.results.pose_landmarks.landmark
        if not is_valid_pose:
            return []
        normalized_landmarks = self.coordinate_normalizer.normalize(smoothed_landmarks)
        for idx, lm in enumerate(normalized_landmarks):
            landmarks.append(
                {
                    "id": idx,
                    "x": lm.x,
                    "y": lm.y,
                    "z": lm.z,
                    "visibility": lm.visibility,
                    "x_px": int(lm.x * w),
                    "y_px": int(lm.y * h),
                }
            )
        return landmarks
