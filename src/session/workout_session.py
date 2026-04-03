import time
from collections import Counter


class WorkoutSession:
    """Tracks full workout statistics independent from exercise."""
    """
    Tracks full workout statistics.
    Independent from exercises.
    """

    def __init__(self):
        """Initialize new workout session tracker."""
        self.start_time = time.time()

        self.total_reps = 0
        self.rep_scores = []
        self.feedback_log = []

        self.last_rep_count = 0

    # --------------------------------------------------
    # Update per frame
    # --------------------------------------------------
    def update(self, reps, score, feedback):
        """Update session with rep and feedback data.
        
        Args:
            reps: Current rep count.
            score: Quality score for current rep.
            feedback: Form feedback message or None.
        """
        """
        Called every frame from pipeline.
        """

        # Detect NEW rep
        if reps > self.last_rep_count:
            self.total_reps = reps
            self.last_rep_count = reps

            if isinstance(score, dict) and "final_score" in score:
                self.rep_scores.append(score["final_score"])

        # Log meaningful feedback only and skip None or empty feedback.
        if feedback is not None:
            if isinstance(feedback, list):
                self.feedback_log.extend([fb for fb in feedback if fb is not None])
            else:
                self.feedback_log.append(feedback)

    # --------------------------------------------------
    # Build summary
    # --------------------------------------------------
    def get_summary(self, exercise_name):
        """Generate workout summary with statistics.
        
        Args:
            exercise_name: Name of exercise performed.
        
        Returns:
            dict: Summary with reps, duration, average score, feedback log.
        """

        duration = int(time.time() - self.start_time)
        minutes = duration // 60
        seconds = duration % 60

        avg_score = (
            sum(self.rep_scores) / len(self.rep_scores) if self.rep_scores else 0
        )

        best_score = max(self.rep_scores) if self.rep_scores else 0

        common_feedback = []
        valid_feedback = [fb for fb in self.feedback_log if fb is not None]
        if valid_feedback:
            counts = Counter(valid_feedback)
            common_feedback = [fb for fb, _ in counts.most_common(2)]

        return {
            "exercise": exercise_name,
            "total_reps": self.total_reps,
            "avg_score": round(avg_score, 1),
            "best_score": best_score,
            "common_feedback": common_feedback,
            "duration": f"{minutes:02}:{seconds:02}",
        }
