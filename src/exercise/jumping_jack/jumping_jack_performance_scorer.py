# # jumping_jack_performance_scorer.py
# class JumpingJackPerformanceScorer:
#     def update(self, landmarks, state,rep_duration):
#         # score = self.score(rep_duration)
#         # del rep_duration
#         # return score
#         if hasattr(self, "rep_duration") and state.name == "CLOSED":
#             score = self.score(rep_duration)
#             del rep_duration
#             return score
#         return None
#     def score(self, rep_time):
#         return {"final_score": 100 if rep_time < 1.2 else 70}


class JumpingJackPerformanceScorer:
    def update(self, state, rep_duration):
        if hasattr(self, "rep_duration") and state.name == "CLOSED":
            score = self.score(rep_duration)
            return score
        return None
    def score(self, rep_duration):
        if rep_duration < 0.8:
            return {"final_score": 100}
        elif rep_duration < 1.3:
            return {"final_score": 85}
        else:
            return {"final_score": 70}
