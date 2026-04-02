from datetime import datetime
from src.gamification.leaderboard_entry import LeaderboardEntry
from src.gamification.leaderboard_storage import LeaderboardStorage


class LeaderboardSystem:

    def __init__(self):
        self.entries = LeaderboardStorage.load()

    @staticmethod
    def _current_week_id():
        return datetime.now().strftime("%Y-W%U")

    # ---------------------------------
    # Add workout result
    # ---------------------------------
    def submit_workout(self, player_name, summary, xp_gained):

        current_week = self._current_week_id()

        # Check if player already has an entry this week
        existing_entry = next(
            (
                entry
                for entry in self.entries
                if entry.player_name == player_name and entry.week_id() == current_week
            ),
            None,
        )

        # Create new entry with current workout stats
        new_entry = LeaderboardEntry(
            player_name=player_name,
            reps=summary["total_reps"],
            score=summary["avg_score"],
            xp=xp_gained,
        )

        if existing_entry:
            # Update only if new score is better
            if new_entry.ranking_score() > existing_entry.ranking_score():
                self.entries.remove(existing_entry)
                self.entries.append(new_entry)
        else:
            # First entry this week for this player
            self.entries.append(new_entry)

        LeaderboardStorage.save(self.entries)

    # ---------------------------------
    # Current week leaderboard
    # ---------------------------------
    def get_weekly_leaderboard(self, top_n=5):

        current_week = self._current_week_id()

        weekly = [e for e in self.entries if e.week_id() == current_week]

        ranked = sorted(weekly, key=lambda e: e.ranking_score(), reverse=True)

        return ranked[:top_n]
