from dataclasses import dataclass
from .constants import SCREEN_W, SCREEN_H

@dataclass(frozen=True)
class GameConfig:
    width: int = SCREEN_W
    height: int = SCREEN_H
    title: str = "StickFTG - MVCS Prototype"
