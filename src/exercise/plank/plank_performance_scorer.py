# plank_performance_scorer.py
class PlankPerformanceScorer:
    def update(self, landmarks, state, timer):
        if state.name == "BROKEN":
            total_time = timer.total
            return {
                "hold_time_sec": round(total_time, 1),
                "final_score": min(100, int(total_time * 5)),
            }

        return None
