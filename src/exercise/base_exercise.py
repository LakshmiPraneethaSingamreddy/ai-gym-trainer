from abc import ABC, abstractmethod


class BaseExercise(ABC):
    """Abstract base class for exercise implementations.

    Defines the interface for state management, rep counting,
    form validation, and scoring.
    """

    FEEDBACK_STATES = []

    def __init__(self, name):
        """Initialize exercise with name and state trackers."""
        self.name = name
        self.reps = 0
        self.prev_state = None

    @abstractmethod
    def update(self, landmarks):
        """Update state machine based on pose landmarks."""
        pass

    @abstractmethod
    def count_rep(self, state):
        """Count completed reps based on current state."""
        pass

    @abstractmethod
    def validate_form(self, landmarks):
        """Validate exercise form and return feedback messages."""
        pass

    @abstractmethod
    def score_rep(self, landmarks, state):
        """Calculate quality score for the rep."""
        pass

    def allow_feedback(self, state_name):
        """Check if feedback should be shown in this state."""
        return state_name in self.FEEDBACK_STATES
