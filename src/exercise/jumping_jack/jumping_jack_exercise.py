import time
from src.exercise.base_exercise import BaseExercise
from src.exercise.jumping_jack.jumping_jack_state_machine import JumpingJackStateMachine
from src.exercise.jumping_jack.jumping_jack_rep_counter import JumpingJackRepCounter
from src.exercise.jumping_jack.jumping_jack_form_validator import (
    JumpingJackFormValidator,
)
from src.exercise.jumping_jack.jumping_jack_performance_scorer import (
    JumpingJackPerformanceScorer,
)


class JumpingJackExercise(BaseExercise):
    FEEDBACK_STATES = ["OPEN"]

    def __init__(self):
        super().__init__("JumpingJack")
        self.state_machine = JumpingJackStateMachine()
        self.rep_counter = JumpingJackRepCounter()
        self.validator = JumpingJackFormValidator()
        self.scorer = JumpingJackPerformanceScorer()

        self.rep_start_time = None
        self.rep_duration = None

    def update(self, landmarks):
        state = self.state_machine.update(landmarks)

        if state.name == "OPEN" and self.rep_start_time is None:
            self.rep_start_time = time.time()

        if state.name == "CLOSED" and self.rep_start_time:
            self.rep_duration = time.time() - self.rep_start_time
            self.rep_start_time = None

        return state

    def count_rep(self, state_name):
        return self.rep_counter.update(state_name)

    def validate_form(self, landmarks):
        return self.validator.validate(landmarks)

    def score_rep(self, landmarks, state):
        return self.scorer.update(state, self.rep_duration)
