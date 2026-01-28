
import pygame
from game.core.game import Game


p1_scheme = {
    "up": pygame.K_w,
    "down": pygame.K_s,
    "left": pygame.K_a,
    "right": pygame.K_d,
    "attack": pygame.K_j,
    "kick": pygame.K_k,
    "block": pygame.K_l
}

p2_scheme = {
    "up": pygame.K_UP,
    "down": pygame.K_DOWN,
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "attack": pygame.K_KP1,
    "kick": pygame.K_KP2,
    "block": pygame.K_KP3
}


if __name__ == "__main__":
    Game().run()

