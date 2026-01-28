from enum import Enum
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict

class ActionType(Enum):
    IDLE = "IDLE"
    STEP_FORWARD = "STEP_FORWARD"
    STEP_BACK = "STEP_BACK"
    THRUST = "THRUST"
    LUNGE = "LUNGE"
    BEAT = "BEAT"

class FencerState(Enum):
    NEUTRAL = "NEUTRAL"
    MOVING_FORWARD = "MOVING_FORWARD"
    MOVING_BACKWARD = "MOVING_BACKWARD"
    ATTACK_STARTUP = "ATTACK_STARTUP"
    ATTACK_ACTIVE = "ATTACK_ACTIVE"
    RECOVERY = "RECOVERY"
    HIT = "HIT"

class GameMode(Enum):
    PVP = "PVP"
    PVE = "PVE"

class Weapon(BaseModel):
    min_range: float = 1.0
    best_range: float = 2.0
    max_range: float = 3.0
    
class Fencer(BaseModel):
    id: int
    score: int = 0
    position: float
    state: FencerState = FencerState.NEUTRAL
    state_timer: int = 0  # Frames remaining in current state
    last_action: ActionType = ActionType.IDLE
    
    # Configuration
    move_speed: float = 0.1
    lunge_speed: float = 0.3
    reach: float = 1.5
    
class GameConfig(BaseModel):
    max_score: int = 5
    tick_rate: int = 60
    arena_length: float = 14.0 # Standard Fencing strip length
    mode: GameMode = GameMode.PVP

class GameState(BaseModel):
    tick_count: int = 0
    fencers: List[Fencer]
    distance: float = 0.0
    game_over: bool = False
    winner: Optional[int] = None
    last_event: Optional[str] = None
    
    def update_distance(self):
        if len(self.fencers) == 2:
            self.distance = abs(self.fencers[0].position - self.fencers[1].position)

