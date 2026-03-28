# src/exercise/plank/plank_exercise.py
from src.exercise.base_exercise import BaseExercise
from src.exercise.plank.plank_state_machine import PlankStateMachine
from src.exercise.plank.plank_rep_counter import PlankTimer
from src.exercise.plank.plank_form_validator import PlankFormValidator
from src.exercise.plank.plank_performance_scorer import PlankPerformanceScorer


class PlankExercise(BaseExercise):
    FEEDBACK_STATES = ["HOLD"]

    def __init__(self):
        super().__init__("Plank")
        self.state_machine = PlankStateMachine()
        self.timer = PlankTimer()
        self.validator = PlankFormValidator()
        self.scorer = PlankPerformanceScorer()

    def update(self, landmarks):
        return self.state_machine.update(landmarks)

    def count_rep(self, state_name):
        # For plank, this returns total hold time
        return self.timer.update(state_name)

    def validate_form(self, landmarks):
        return self.validator.validate(landmarks)

    def score_rep(self, landmarks, state):
        return self.scorer.update(landmarks, state, self.timer)
