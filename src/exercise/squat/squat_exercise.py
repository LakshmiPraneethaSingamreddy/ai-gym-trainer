from  src.exercise.base_exercise import BaseExercise
from .squat_state_machine import SquatStateMachine
from .squat_rep_counter import RepCounter
from .squat_form_validator import SquatFormValidator
from .squat_performance_scorer import PerformanceScorer

class SquatExercise(BaseExercise):
    def __init__(self):
        super().__init__("Squat")
        self.state_machine = SquatStateMachine()
        self.rep_counter = RepCounter()
        self.validator = SquatFormValidator()
        self.scorer = PerformanceScorer()

    def update(self, landmarks):
        return self.state_machine.update(landmarks)

    def count_rep(self, state):
        return self.rep_counter.update(state)

    def validate_form(self, landmarks):
        return self.validator.validate(landmarks)

    def score_rep(self, landmarks, state):
        return self.scorer.update(landmarks, state, self.reps)
