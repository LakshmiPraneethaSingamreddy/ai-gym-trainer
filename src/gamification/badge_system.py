from src.gamification.badge_registry import BadgeRegistry


class BadgeSystem:
    """Manages badge (achievement) unlocking and tracking."""

    DISPLAY_DURATION = 3.0  # seconds

    def __init__(self, player_profile):
        """Initialize badge system with available badges from registry.

        Args:
            player_profile: Player instance to track badges for.
        """
        self.player = player_profile
        self.badges = BadgeRegistry.get_all_badges()

        if not hasattr(self.player, "badges"):
            self.player.badges = []

    # ----------------------------------
    # Evaluate badges after workout
    # ----------------------------------
    def evaluate(self, summary):
        """Evaluate if any new badges are earned based on workout summary.

        Args:
            summary: Workout summary with stats.

        Returns:
            list: Newly unlocked Badge objects.
        """
        unlocked = []
        owned = set(self.player.badges)

        for badge in self.badges:
            if badge.id in owned:
                continue

            if self._check_condition(badge.id, summary):
                self.player.badges.append(badge.id)
                unlocked.append(badge)

        return unlocked

    # ----------------------------------
    # Conditions
    # ----------------------------------
    def _check_condition(self, badge_id, summary):
        """Check if badge unlock condition is met.

        Args:
            badge_id: Badge identifier.
            summary: Workout summary.

        Returns:
            bool: Whether condition is satisfied.
        """
        if badge_id == "first_workout":
            return self.player.total_workouts >= 1

        if badge_id == "rep_100":
            return self.player.total_reps >= 100

        if badge_id == "rep_500":
            return self.player.total_reps >= 500

        if badge_id == "score_90":
            return summary["best_score"] >= 90

        if badge_id == "streak_3":
            return self.player.streak_days >= 3

        return False
