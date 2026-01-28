from dataclasses import dataclass
import pygame

@dataclass
class Box:
    x: float
    y: float
    w: float
    h: float

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), int(self.w), int(self.h))

@dataclass
class AttackFrame:
    startup: int     # frames before active
    active: int      # active frames
    recovery: int    # frames after active
    damage: int
    knockback_x: float
    hitbox_w: int
    hitbox_h: int
    hitbox_offset_x: int
    hitbox_offset_y: int

    @property
    def total(self) -> int:
        return self.startup + self.active + self.recovery
