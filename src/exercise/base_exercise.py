from abc import ABC, abstractmethod

class BaseExercise(ABC):
    def __init__(self, name):
        self.name = name
        self.reps = 0
        self.prev_state = None

    @abstractmethod
    def update(self, landmarks):
        """Update state machine"""
        pass

    @abstractmethod
    def count_rep(self, state):
        """Update rep counter"""
        pass

    @abstractmethod
    def validate_form(self, landmarks):
        """Return form feedback"""
        pass

    @abstractmethod
    def score_rep(self, landmarks, state):
        """Return rep score"""
        pass
