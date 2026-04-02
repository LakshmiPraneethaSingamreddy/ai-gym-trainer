import json
import os
from datetime import datetime, date


class PlayerProfile:
    """
    Stores long-term user progress.
    Persists across sessions.
    """

    SAVE_PATH = "player_profile.json"

    def __init__(self):
        self.name = "Player1"
        self.level = 1
        self.xp = 0
        self.total_workouts = 0
        self.total_reps = 0
        self.best_score = 0
        self.streak_days = 0
        self.last_workout_date = None
        self.badges = []

        self.load()

    # ----------------------------------
    # Persistence
    # ----------------------------------
    def load(self):
        if os.path.exists(self.SAVE_PATH):
            with open(self.SAVE_PATH, "r") as f:
                data = json.load(f)
                self.__dict__.update(data)

    def save(self):
        with open(self.SAVE_PATH, "w") as f:
            json.dump(self.__dict__, f, indent=4)

    # ----------------------------------
    # XP Handling
    # ----------------------------------
    def add_xp(self, amount):
        self.xp += amount

    def level_up(self):
        self.level += 1
        print(f"LEVEL UP! You are now level {self.level}")

    # ----------------------------------
    # Daily Streak System
    # ----------------------------------
    def update_streak(self):

        today = date.today()

        # First workout ever
        if self.last_workout_date is None:
            self.streak_days = 1

        else:
            last_date = datetime.strptime(self.last_workout_date, "%Y-%m-%d").date()

            diff = (today - last_date).days

            if diff == 0:
                # already worked out today
                return

            elif diff == 1:
                # consecutive day
                self.streak_days += 1

            else:
                # missed days → reset
                self.streak_days = 1

        self.last_workout_date = today.strftime("%Y-%m-%d")

    # ----------------------------------
    # Update After Workout
    # ----------------------------------
    def update_from_session(self, summary):

        self.total_workouts += 1
        self.total_reps += summary["total_reps"]

        if summary["best_score"] > self.best_score:
            self.best_score = summary["best_score"]

        self.update_streak()
        self.save()
