from src.gamification.badge import Badge


class BadgeRegistry:

    @staticmethod
    def get_all_badges():
        return [

            Badge(
                "first_workout",
                "First Steps",
                "Complete your first workout"
            ),

            Badge(
                "rep_100",
                "Century",
                "Complete 100 total reps"
            ),

            Badge(
                "rep_500",
                "Warrior",
                "Complete 500 total reps"
            ),

            Badge(
                "score_90",
                "Perfect Form",
                "Achieve score above 90"
            ),

            Badge(
                "streak_3",
                "Consistency I",
                "Maintain 3-day streak"
            ),
        ]