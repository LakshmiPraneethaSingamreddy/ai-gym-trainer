class ExerciseRegistry:
    """Registry for managing available exercise implementations."""
    def __init__(self):
        """Initialize empty registry."""
        self.exercises = {}

    def register(self, exercise):
        """Register an exercise implementation.

        Args:
            exercise: Exercise instance with name property.
        """
        self.exercises[exercise.name] = exercise

    def get(self, name):
        """Get registered exercise by name.

        Args:
            name: Exercise name.

        Returns:
            Exercise implementation or None.
        """
        return self.exercises.get(name)
