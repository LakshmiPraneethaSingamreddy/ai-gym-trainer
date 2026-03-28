import cv2
import time

class HUD:
    def __init__(self):
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.active_badges = []

    def draw(
        self,
        frame,
        exercise_name,
        reps,
        state,
        feedback,
        score,
        level=None,
        xp=None,
        xp_required=None
    ):
        try:
            y = 30
            line_gap = 30

            cv2.putText(frame, f"Exercise: {exercise_name}",
                        (10, y), self.font, 0.8, (255, 255, 255), 2)
            y += line_gap

            cv2.putText(frame, f"Reps / Time: {reps}",
                        (10, y), self.font, 0.8, (0, 255, 255), 2)
            y += line_gap

            if level is not None:
                cv2.putText(frame, f"Level: {level}",
                            (10, y), self.font, 0.7, (0, 255, 255), 2)
                y += line_gap

            if xp is not None and xp_required is not None:
                cv2.putText(frame, f"XP: {xp}/{xp_required}",
                            (10, y), self.font, 0.6, (0, 200, 255), 2)
                y += line_gap

            cv2.putText(frame, f"State: {state}",
                        (10, y), self.font, 0.8, (255, 255, 0), 2)
            y += line_gap

            if feedback is not None:
                feedback_text = feedback[-1] if isinstance(feedback, list) else feedback
                cv2.putText(frame, f"Feedback: {feedback_text}",
                            (10, y), self.font, 0.7, (0, 0, 255), 2)
                y += line_gap

            if score is not None and isinstance(score, dict):
                score_value = score.get('final_score', 'N/A')
                cv2.putText(frame, f"Score: {score_value}",
                            (10, y), self.font, 0.8, (0, 255, 0), 2)

            self.draw_badge_popups(frame)

            return frame

        except Exception as e:
            print(f"Error drawing HUD: {e}")
            return frame

    def show_badges(self, badges):
        now = time.time()
        for badge in badges:
            self.active_badges.append({
                "badge": badge,
                "start_time": now
            })

    def draw_badge_popups(self, frame):
        now = time.time()
        y = 180
        remaining = []

        for entry in self.active_badges:
            if now - entry["start_time"] < 3.0:
                badge = entry["badge"]
                text = f"Badge Unlocked: {badge.name}"

                cv2.rectangle(frame, (20, y-30), (500, y+10),
                              (0, 140, 255), -1)

                cv2.putText(frame, text,
                            (30, y),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (255, 255, 255),
                            2)

                y += 50
                remaining.append(entry)

        self.active_badges = remaining