
class AchievementAlreadyExists(Exception):
    def __init__(self, message="An achievement with this name already exists"):
        self.message = message
        super().__init__(self.message)
