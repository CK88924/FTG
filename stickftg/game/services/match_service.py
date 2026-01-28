from ..core.constants import ROUND_TIME_SEC, FPS
from ..models.state import FighterState

class MatchService:
    def __init__(self):
        self.round_frames = ROUND_TIME_SEC * FPS
        self.frame_left = self.round_frames
        self.winner = None

    def step(self, p1, p2):
        if self.winner is not None:
            return

        self.frame_left -= 1
        if p1.is_dead():
            self.winner = p2.name
            p1.set_state(FighterState.DEAD)
            return
        if p2.is_dead():
            self.winner = p1.name
            p2.set_state(FighterState.DEAD)
            return

        if self.frame_left <= 0:
            if p1.hp > p2.hp:
                self.winner = p1.name
            elif p2.hp > p1.hp:
                self.winner = p2.name
            else:
                self.winner = "DRAW"
