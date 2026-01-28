import pygame
from ..core.constants import SCREEN_W, GROUND_Y

class Renderer:
    def __init__(self):
        self.font = pygame.font.SysFont("consolas", 20)

    def draw_ui(self, screen, p1, p2, match):
        pygame.draw.line(screen, (120, 120, 120), (0, GROUND_Y), (SCREEN_W, GROUND_Y), 2)

        self._hp_bar(screen, 60, 40, p1.hp, (60, 200, 60))
        self._hp_bar(screen, SCREEN_W-260, 40, p2.hp, (200, 60, 60))

        screen.blit(self.font.render(p1.name, True, (220,220,220)), (60, 15))
        screen.blit(self.font.render(p2.name, True, (220,220,220)), (SCREEN_W-260, 15))

        sec_left = max(0, match.frame_left // 60)
        t = self.font.render(f"TIME {sec_left:02d}", True, (240,240,240))
        screen.blit(t, (SCREEN_W//2 - 50, 15))

        if match.winner is not None:
            msg = self.font.render(f"WINNER: {match.winner}  (R to restart)", True, (255, 220, 60))
            screen.blit(msg, (SCREEN_W//2 - 190, 80))

    def _hp_bar(self, screen, x, y, hp, color):
        w, h = 200, 16
        hp = max(0, min(100, hp))
        fill = int(w * (hp/100.0))
        pygame.draw.rect(screen, (60,60,60), (x, y, w, h))
        pygame.draw.rect(screen, color, (x, y, fill, h))
        pygame.draw.rect(screen, (220,220,220), (x, y, w, h), 2)

    def draw_debug_boxes(self, screen, fighter, show_hitbox=False):
        pygame.draw.rect(screen, (80, 160, 255), fighter.hurtbox().rect(), 1)
        if show_hitbox:
            hit = fighter.current_hitbox()
            if hit:
                pygame.draw.rect(screen, (255, 120, 80), hit.rect(), 1)
