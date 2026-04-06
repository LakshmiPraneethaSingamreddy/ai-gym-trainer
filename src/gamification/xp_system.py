class XPSystem:
    """Manages XP calculation based on rep performance and effort."""

    def calculate_rep_xp(self, score):
        """Calculate XP for a single rep based on quality score.

        Args:
            score: Rep quality score (0-100).

        Returns:
            int: XP awarded (0-10 per rep).
        """
        if score is None:
            return 0

        if isinstance(score, dict):
            final_score = score.get("final_score", 0)
        else:
            final_score = score

        # Map score range 0-100 into a lightweight per-rep XP bonus.
        rep_xp = int(final_score * 0.05)
        return max(0, rep_xp)

    def calculate_xp(self, summary):
        """Calculate total XP for a workout session.

        Args:
            summary: Workout summary with total_reps and avg_score.

        Returns:
            int: Total XP for session (capped at 30).
        """
        avg_score = summary.get("avg_score", 0)
        total_reps = summary.get("total_reps", 1)

        # Effort drives most XP; form quality adds a smaller bonus.
        # 1 rep with score 0 = 3 XP
        # 3 reps with score 50 = ~12 XP
        # 5 reps with score 100 = ~20 XP
        xp = int(total_reps * 3 + avg_score * 0.1)
        total_xp = min(xp, 30)  # Cap at 30 XP per action
        return total_xp
