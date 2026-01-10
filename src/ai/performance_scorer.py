from src.ai.angles import AngleCalculator

class PerformanceScorer:
    """
    Computes a performance score for each rep based on:
    - squat depth (knee angle)
    - hip hinge quality (hip angle)
    - consistency
    """

    def __init__(self):
        self.rep_scores = []
        self.current_rep_frames = []

    def update(self, landmarks, squat_state, rep_count):
        """
        Called every frame.
        Collects frame data during a rep and scores it when rep completes.
        """

        knee_angle = AngleCalculator.knee_angle(landmarks, side="left")
        hip_angle = AngleCalculator.hip_angle(landmarks, side="left")

        # Collect frame data during movement
        if squat_state in ["DESCENDING", "BOTTOM", "ASCENDING"]:
            self.current_rep_frames.append({
                "knee_angle": knee_angle,
                "hip_angle": hip_angle
            })

        # When rep finishes → score it
        if squat_state == "STANDING" and len(self.current_rep_frames) > 0:
            score = self._score_rep(self.current_rep_frames)
            self.rep_scores.append(score)
            self.current_rep_frames = []

            return score  # return latest rep score

        return None

    def _score_rep(self, frames):
        """
        Scores a single rep based on depth and form
        """

        knee_angles = [f["knee_angle"] for f in frames]
        hip_angles = [f["hip_angle"] for f in frames]

        min_knee = min(knee_angles)   # deepest squat
        avg_hip = sum(hip_angles) / len(hip_angles)

        # --- Scoring Logic ---
        depth_score = max(0, min(100, int((120 - min_knee) * 2)))
        hip_score = max(0, min(100, int((180 - avg_hip) * 1.5)))

        final_score = int((depth_score * 0.6) + (hip_score * 0.4))

        return {
            "depth_score": depth_score,
            "hip_score": hip_score,
            "final_score": final_score
        }

    def get_average_score(self):
        if not self.rep_scores:
            return 0
        return int(sum(r["final_score"] for r in self.rep_scores) / len(self.rep_scores))
