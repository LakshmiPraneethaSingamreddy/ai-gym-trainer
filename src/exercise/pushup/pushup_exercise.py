from src.exercise.base_exercise import BaseExercise
from .pushup_state_machine import PushupStateMachine
from .pushup_rep_counter import PushupRepCounter
from .pushup_performance_scorer import PushupPerformanceScorer
from .pushup_form_validator import PushupFormValidator


class PushupExercise(BaseExercise):
    FEEDBACK_STATES = ["DOWN"]

    def __init__(self):
        super().__init__("Knee/Regular Pushups")
        self.state_machine = PushupStateMachine()
        self.rep_counter = PushupRepCounter()
        self.validator = PushupFormValidator()
        self.scorer = PushupPerformanceScorer()

    def update(self, landmarks):
        self.state = self.state_machine.update(landmarks)
        self.reached_bottom = self.state_machine.reached_bottom
        return self.state

    def count_rep(self, state_name):
        return self.rep_counter.update(state_name, self.reached_bottom)

    def validate_form(self, landmarks):
        return self.validator.validate(landmarks)

    def score_rep(self, landmarks, state):
        return self.scorer.update(landmarks, state)
