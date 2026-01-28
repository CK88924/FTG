from dataclasses import dataclass
from .constants import FPS

@dataclass
class FixedClock:
    fps: int = FPS
    frame: int = 0

    def tick(self):
        self.frame += 1
