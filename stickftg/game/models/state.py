from enum import Enum, auto

class FighterState(Enum):
    IDLE = auto()
    MOVE = auto()
    JUMP = auto()
    ATTACK = auto()
    BLOCK = auto()
    BLOCK_STUN = auto()
    HITSTUN = auto()
    DEAD = auto()
