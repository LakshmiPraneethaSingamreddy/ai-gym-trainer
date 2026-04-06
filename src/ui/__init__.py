import cv2


class WorkoutSummaryUI:

    def draw(self, frame, summary, leaderboard=None):

        y = 80
        line_gap = 40

        def put(text, size=1, color=(0, 255, 255)):
            nonlocal y
            cv2.putText(
                frame,
                text,
                (60, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                size,
                color,
                2,
                cv2.LINE_AA,
            )
            y += line_gap

        put("WORKOUT SUMMARY", 1.2)
        y += 20

        put(f"Exercise: {summary['exercise']}")
        put(f"Total Reps: {summary['total_reps']}")
        put(f"Average Score: {summary['avg_score']}")
        put(f"Best Rep Score: {summary['best_score']}")
        put(f"Duration: {summary['duration']}")

        y += 30
        put("Common Feedback:", 1)

        for fb in summary["common_feedback"]:
            put(f"- {fb}", 0.8)

        # ðŸ”¥ Leaderboard Section
        if leaderboard:
            y += 40
            put("WEEKLY LEADERBOARD", 1.1, (255, 200, 0))
            y += 10

            for i, entry in enumerate(leaderboard[:5]):
                if isinstance(entry, dict):
                    name = entry.get("player_name")
                    score_val = entry.get("ranking_score")
                else:
                    name = getattr(entry, "player_name", None)
                    score_val = getattr(entry, "ranking_score", None)
                    if callable(score_val):
                        score_val = score_val()

                if name and score_val is not None:
                    put(f"{i+1}. {name} - {int(score_val)}", 0.9, (255, 255, 255))

        return frame
