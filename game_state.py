from enum import Enum, auto

class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    SETTINGS = auto()
    LEADERBOARD = auto()

class StateMachine:
    def __init__(self):
        self.state = GameState.MENU

    def change_state(self, new_state):
        self.state = new_state

    def get_state(self):
        return self.state