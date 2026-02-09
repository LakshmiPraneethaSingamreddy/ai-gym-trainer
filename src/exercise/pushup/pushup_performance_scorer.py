from src.ai.angles import AngleCalculator

class PushupPerformanceScorer:
    def __init__(self):
        self.rep_scores = []
        self.frames = []

    def update(self, landmarks, state):
        elbow = AngleCalculator.elbow_angle(landmarks)
        self.frames.append(elbow)

        if state == "UP" and len(self.frames) > 10:
            min_elbow = min(self.frames)
            score = max(0, min(100, int((120 - min_elbow) * 2)))

            self.rep_scores.append(score)
            self.frames = []

            return score

        return None
