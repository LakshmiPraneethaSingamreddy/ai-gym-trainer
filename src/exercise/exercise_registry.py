class ExerciseRegistry:
    def __init__(self):
        self.exercises = {}

    def register(self, exercise):
        self.exercises[exercise.name] = exercise

    def get(self, name):
        return self.exercises.get(name)
