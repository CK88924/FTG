from ..core.constants import MOVE_SPEED
from ..models.state import FighterState

class SimpleAIController:
    def update(self, fighter, opponent):
        if fighter.state in (FighterState.HITSTUN, FighterState.DEAD, FighterState.ATTACK):
            return

        dx = opponent.pos.x - fighter.pos.x

        if abs(dx) < 90 and fighter.state != FighterState.ATTACK:
            fighter.set_state(FighterState.ATTACK)
            fighter.vel.x = 0
            fighter.facing = 1 if dx > 0 else -1
            return

        if dx > 10:
            fighter.vel.x = MOVE_SPEED * 0.8
            fighter.facing = 1
            if fighter.on_ground:
                fighter.set_state(FighterState.MOVE)
        elif dx < -10:
            fighter.vel.x = -MOVE_SPEED * 0.8
            fighter.facing = -1
            if fighter.on_ground:
                fighter.set_state(FighterState.MOVE)
        else:
            fighter.vel.x = 0
            if fighter.on_ground:
                fighter.set_state(FighterState.IDLE)
