class JumpingJackPerformanceScorer:
    def update(self, state, rep_duration):
        # if hasattr(self, "rep_duration") and state.name == "CLOSED":
        #     score = self.score(rep_duration)
        #     return score
        if state.name == "CLOSED" and rep_duration is not None:
            return self.score(rep_duration)
        return None

    def score(self, rep_duration):
        if rep_duration < 0.8:
            return {"final_score": 100}
        elif rep_duration < 1.3:
            return {"final_score": 85}
        else:
            return {"final_score": 70}
