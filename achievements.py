class Achievement:
    def __init__(self, name, description, condition):
        self.name = name
        self.description = description
        self.condition = condition
        self.unlocked = False

    def check(self, game_state):
        if not self.unlocked and self.condition(game_state):
            self.unlocked = True
            return True
        return False

class AchievementManager:
    def __init__(self):
        self.achievements = [
            Achievement("Beginner", "Score 10 points", lambda state: state.score >= 10),
            Achievement("Intermediate", "Score 50 points", lambda state: state.score >= 50),
            Achievement("Expert", "Score 100 points", lambda state: state.score >= 100),
            Achievement("Combo Master", "Get a 10x combo", lambda state: state.player.combo >= 10),
            Achievement("Survivor", "Play for 2 minutes", lambda state: state.time >= 120),
        ]

    def update(self, game_state):
        unlocked = []
        for achievement in self.achievements:
            if achievement.check(game_state):
                unlocked.append(achievement)
        return unlocked