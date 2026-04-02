from datetime import datetime


class LeaderboardEntry:
    """
    Represents one leaderboard submission.
    """

    def __init__(self, player_name, reps, score, xp):
        self.player_name = player_name
        self.reps = reps
        self.score = score
        self.xp = xp
        self.timestamp = datetime.now()

    # -----------------------------
    # Weekly grouping
    # -----------------------------
    def week_id(self):
        return self.timestamp.strftime("%Y-W%U")

    # -----------------------------
    # Ranking score
    # -----------------------------
    def ranking_score(self):
        return self.reps * 0.4 + self.score * 0.4 + self.xp * 0.2

    def to_dict(self):
        return {
            "player_name": self.player_name,
            "reps": self.reps,
            "score": self.score,
            "xp": self.xp,
            "timestamp": self.timestamp.isoformat(),
        }

    @staticmethod
    def from_dict(data):
        obj = LeaderboardEntry(
            data["player_name"], data["reps"], data["score"], data["xp"]
        )
        obj.timestamp = datetime.fromisoformat(data["timestamp"])
        return obj
