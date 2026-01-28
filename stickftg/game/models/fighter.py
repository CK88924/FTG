from dataclasses import dataclass, field
from typing import List
from .types import Vec2
from .state import FighterState
from .hitbox import Box, AttackFrame

@dataclass
class Fighter:
    name: str
    pos: Vec2
    vel: Vec2
    facing: int  # +1 right, -1 left
    hp: int = 100
    state: FighterState = FighterState.IDLE

    on_ground: bool = True
    state_frame: int = 0          # current frame inside current state
    hitstun_left: int = 0
    hitstun_left: int = 0
    has_hit: bool = False
    
    # Attack details

    
    # 0 = not blocking, 1 = blocking
    # Logic is mainly in state, but we might want a flag or just use state.

    # Combo support
    combo_count: int = 0
    # Provide a list of attacks for the combo chain
    # We will initialize this in __post_init__ or direct field default if we want custom chains per fighter
    attack_chain: List[AttackFrame] = field(default_factory=list)

    def __post_init__(self):
        # Define a 3-hit combo chain if not provided
        if not self.attack_chain:
            # 1. Quick Punch
            a1 = AttackFrame(
                startup=6, active=4, recovery=8,
                damage=5, knockback_x=20.0, # Reduced significant knockback to allow combos
                hitbox_w=80, hitbox_h=30,
                hitbox_offset_x=40, hitbox_offset_y=-75
            )
            # 2. Kick
            a2 = AttackFrame(
                startup=8, active=6, recovery=12,
                damage=8, knockback_x=150.0,
                hitbox_w=120, hitbox_h=40,
                hitbox_offset_x=20, hitbox_offset_y=-55
            ) # wider reach, starts closer
            # 3. Heavy Finisher
            a3 = AttackFrame(
                startup=12, active=8, recovery=20,
                damage=15, knockback_x=400.0,
                hitbox_w=120, hitbox_h=60,
                hitbox_offset_x=60, hitbox_offset_y=-80
            ) 
            self.attack_chain = [a1, a2, a3]
            
    @property
    def attack_def(self) -> AttackFrame:
        return self.attack_chain[0]


    def reset_state_frame(self):
        self.state_frame = 0

    def set_state(self, st: FighterState):
        if self.state != st:
            self.state = st
            self.reset_state_frame()
            self.has_hit = False

    def step_state_frame(self):
        self.state_frame += 1

    def hurtbox(self) -> Box:
        # Simple body box (stickman) — tune as you like
        return Box(self.pos.x - 18, self.pos.y - 90, 36, 90)

    def current_hitbox(self) -> Box | None:
        # Only during ATTACK active frames
        if self.state != FighterState.ATTACK:
            return None
        f = self.state_frame
        a = self.attack_def
        if f < a.startup:
            return None
        if f >= a.startup + a.active:
            return None

        # Place hitbox in front of fighter depending on facing
        x = self.pos.x + self.facing * a.hitbox_offset_x
        y = self.pos.y + a.hitbox_offset_y
        if self.facing < 0:
            x -= a.hitbox_w  # mirror
        return Box(x, y, a.hitbox_w, a.hitbox_h)

    def is_dead(self) -> bool:
        return self.hp <= 0
