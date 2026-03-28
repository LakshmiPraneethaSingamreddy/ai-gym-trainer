import json
import os
from src.gamification.leaderboard_entry import LeaderboardEntry


class LeaderboardStorage:

    FILE_PATH = "leaderboard.json"

    @classmethod
    def load(cls):
        if not os.path.exists(cls.FILE_PATH):
            return []

        with open(cls.FILE_PATH, "r") as f:
            data = json.load(f)

        return [LeaderboardEntry.from_dict(d) for d in data]

    @classmethod
    def save(cls, entries):
        with open(cls.FILE_PATH, "w") as f:
            json.dump([e.to_dict() for e in entries], f, indent=4)