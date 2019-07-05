from enum import Enum, auto


class GameState(Enum):
    PLAYER_TURN = auto()
    ENEMY_TURN = auto()
    PLAYER_DEAD = auto()
