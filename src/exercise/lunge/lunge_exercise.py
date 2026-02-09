from src.exercise.lunge.lunge_state_machine import LungeStateMachine
from src.exercise.lunge.lunge_rep_counter import LungeRepCounter
from src.exercise.lunge.lunge_form_validator import LungeFormValidator
from src.exercise.lunge.lunge_performance_scorer import LungePerformanceScorer

class LungeExercise:
    def __init__(self):
        self.name = "Lunge"
        self.state_machine = LungeStateMachine()
        self.rep_counter = LungeRepCounter()
        self.validator = LungeFormValidator()
        self.scorer = LungePerformanceScorer()

        self.current_rep_knees = []

    def update(self, landmarks):
        return self.state_machine.update(landmarks)

    def count_rep(self, state_name):
        return self.rep_counter.update(state_name)

    def validate_form(self, landmarks):
        return self.validator.validate(landmarks)

    def score_rep(self, landmarks, state):
        return self.scorer.update(landmarks,state)
        

        
