import pygame

class StickmanDrawer:
    def draw(self, screen, fighter, color=(255,255,255)):
        x = int(fighter.pos.x)
        y = int(fighter.pos.y)

        # Body parts relative to ground position
        head = (x, y - 105)
        neck = (x, y - 90)
        hip  = (x, y - 45)

        shoulder_l = (x - 20, y - 80)
        shoulder_r = (x + 20, y - 80)

        if fighter.state.name == "ATTACK":
            # Varied attack animations based on attack_type and combo_count
            
            # ATTACK ANIMATIONS
            # Single Punch
            hand = (x + fighter.facing * 55, y - 75)

        elif fighter.state.name == "BLOCK" or fighter.state.name == "BLOCK_STUN":
             # Block pose: Hands up tight
             hand = (x + fighter.facing * 20, y - 95)
             shoulder_l = (x - 10, y - 85)
             shoulder_r = (x + 10, y - 85)
        else:
            hand = (x + fighter.facing * 30, y - 65)

        knee_l = (x - 15, y - 20)
        foot_l = (x - 25, y)
        knee_r = (x + 15, y - 20)
        foot_r = (x + 25, y)



        pygame.draw.circle(screen, color, head, 12, 2)
        pygame.draw.line(screen, color, neck, hip, 2)

        pygame.draw.line(screen, color, shoulder_l, hip, 2)
        pygame.draw.line(screen, color, shoulder_r, hip, 2)

        pygame.draw.line(screen, color, shoulder_r if fighter.facing > 0 else shoulder_l, hand, 3)

        pygame.draw.line(screen, color, hip, knee_l, 2)
        pygame.draw.line(screen, color, knee_l, foot_l, 2)
        pygame.draw.line(screen, color, hip, knee_r, 2)
        pygame.draw.line(screen, color, knee_r, foot_r, 2)
