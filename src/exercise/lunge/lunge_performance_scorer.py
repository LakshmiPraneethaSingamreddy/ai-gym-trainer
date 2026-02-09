# lunge_performance_scorer.py
from src.ai.angles import AngleCalculator
class LungePerformanceScorer:
    def __init__(self):
        self.frames = []

    def update(self, landmarks, state):
        knee = AngleCalculator.knee_angle(landmarks)

        if state.name in ["DESCENDING", "BOTTOM", "ASCENDING"]:
            self.frames.append(knee)

        if state.name == "STANDING" and self.frames:
            min_knee = min(self.frames)
            self.frames.clear()
            return self.score(min_knee)
        
        return None

    def score(self, min_knee_angle):
        depth_score = max(0, min(100, (120 - min_knee_angle) * 2))
        return {"final_score": depth_score}
