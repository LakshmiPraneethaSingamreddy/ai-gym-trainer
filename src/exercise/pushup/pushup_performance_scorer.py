from src.ai.angles import AngleCalculator

class PushupPerformanceScorer:
    def __init__(self):
        self.rep_scores = []
        self.frames = []

    def update(self, landmarks, state):
        state_name = state.name if hasattr(state, "name") else state
        elbow = AngleCalculator.elbow_angle(landmarks)
        self.frames.append(elbow)

        if state_name == "UP" and len(self.frames) > 10:
            min_elbow = min(self.frames)
            score = max(0, min(100, int((120 - min_elbow) * 2)))

            result = {"final_score": score}
            self.rep_scores.append(result)
            self.frames = []

            # return score
            return result

        return None
