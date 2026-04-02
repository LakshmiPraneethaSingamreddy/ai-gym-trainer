class XPSystem:

    def calculate_rep_xp(self, score):
        """
        Calculate XP for a single rep based on its score.
        """
        if score is None:
            return 0

        if isinstance(score, dict):
            final_score = score.get("final_score", 0)
        else:
            final_score = score

        # Award XP based on rep quality: higher score = more XP
        # Range: 0-10 XP per rep (for scores 0-100)
        rep_xp = int(final_score * 0.05)
        return max(0, rep_xp)

    def calculate_xp(self, summary):
        """
        XP rules:
        - reps reward effort (majority)
        - score rewards quality (bonus)

        Max ~30 XP per workout to ensure reasonable progression.
        """

        avg_score = summary.get("avg_score", 0)
        total_reps = summary.get("total_reps", 1)

        # Balanced formula: effort-focused with quality bonus
        # 1 rep with score 0 = 3 XP
        # 3 reps with score 50 = ~12 XP
        # 5 reps with score 100 = ~20 XP
        xp = int(total_reps * 3 + avg_score * 0.1)
        total_xp = min(xp, 30)  # Cap at 30 XP per action
        return total_xp
