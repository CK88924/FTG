from ..core.constants import GRAVITY, GROUND_Y

class PhysicsService:
    def apply(self, fighter, dt: float):
        fighter.vel.y += GRAVITY * dt
        fighter.pos.x += fighter.vel.x * dt
        fighter.pos.y += fighter.vel.y * dt

        if fighter.pos.y >= GROUND_Y:
            fighter.pos.y = GROUND_Y
            fighter.vel.y = 0.0
            fighter.on_ground = True
        else:
            fighter.on_ground = False
