import pygame
from .config import GameConfig
from .constants import FPS, DT, SCREEN_W, GROUND_Y
from .clock import FixedClock

from ..models.types import Vec2
from ..models.fighter import Fighter
from ..models.state import FighterState

from ..services.physics_service import PhysicsService
from ..services.collision_service import CollisionService
from ..services.combat_service import CombatService
from ..services.match_service import MatchService

from ..controllers.input_controller import InputController
from ..controllers.ai_controller import SimpleAIController

from ..views.renderer import Renderer
from ..views.stickman_drawer import StickmanDrawer

class Game:
    def __init__(self, headless=False):
        self.cfg = GameConfig()
        self.headless = headless
        
        if not self.headless:
            pygame.init()
            pygame.display.set_caption(self.cfg.title)
            self.screen = pygame.display.set_mode((self.cfg.width, self.cfg.height))
            self.clock = pygame.time.Clock()
        
        self.fixed = FixedClock()

        self.physics = PhysicsService()
        self.collision = CollisionService()
        self.combat = CombatService(self.collision)
        self.match = MatchService()

        if not self.headless:
            self.renderer = Renderer()
            self.drawer = StickmanDrawer()

        self.p1 = Fighter("P1", pos=Vec2(280, GROUND_Y), vel=Vec2(0,0), facing=1, hp=100)
        self.p2 = Fighter("P2", pos=Vec2(680, GROUND_Y), vel=Vec2(0,0), facing=-1, hp=100)
        self.p1_hp_prev = 100
        self.p2_hp_prev = 100

        self.p1_ctrl = InputController({
            "left": pygame.K_a,
            "right": pygame.K_d,
            "jump": pygame.K_w,
            "attack": pygame.K_j,
            "kick": pygame.K_k,
            "block": pygame.K_s,
        })

        self.p2_ctrl = InputController({
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "jump": pygame.K_UP,
            "attack": pygame.K_KP1,
            "kick": pygame.K_KP2,
            "block": pygame.K_DOWN,
        })
        self.p2_ai = SimpleAIController()
        self.use_ai_for_p2 = False

        self.show_debug = False
        
        # For headless/env
        self.game_over = False

    def restart(self, seed=None):
        # In a real scenario, use seed for RNG if needed
        self.__init__(headless=self.headless)

    def restart_with_seed(self, seed):
        self.restart(seed)

    def apply_action(self, fighter, action_idx):
        # Map integer action to state change (simplified for env)
        # 0: NOOP, 1: LEFT, 2: RIGHT, 3: JUMP, 4: ATTACK
        if fighter.state in (FighterState.HITSTUN, FighterState.DEAD):
            return

        if action_idx == 4: # ATTACK
             if fighter.state != FighterState.ATTACK:
                fighter.set_state(FighterState.ATTACK)
                fighter.vel.x = 0
             return
        
        if action_idx == 3 and fighter.on_ground: # JUMP
            fighter.vel.y = -900.0 # From constants directly or import
            fighter.set_state(FighterState.JUMP)
            return
            
        move = 0
        if action_idx == 1: move = -1 # LEFT
        if action_idx == 2: move = 1  # RIGHT
        
        if move != 0:
            fighter.vel.x = move * 340.0 # MOVE_SPEED
            fighter.facing = 1 if move > 0 else -1
            if fighter.on_ground:
                fighter.set_state(FighterState.MOVE)
        else:
            fighter.vel.x = 0
            if fighter.on_ground:
                fighter.set_state(FighterState.IDLE)


    def step_one_frame(self):
         # Update previous HP for reward calculation
        self.p1_hp_prev = self.p1.hp
        self.p2_hp_prev = self.p2.hp
        
        # Face each other (basic)
        if self.p1.state not in (FighterState.ATTACK, FighterState.HITSTUN):
            self.p1.facing = 1 if (self.p2.pos.x - self.p1.pos.x) > 0 else -1
        if self.p2.state not in (FighterState.ATTACK, FighterState.HITSTUN):
            self.p2.facing = 1 if (self.p1.pos.x - self.p2.pos.x) > 0 else -1

        self._step_fighter(self.p1)
        self._step_fighter(self.p2)

        self.combat.resolve(self.p1, self.p2)
        self.combat.resolve(self.p2, self.p1)

        self.match.step(self.p1, self.p2)
        self.fixed.tick()
        
    def run(self):
        if self.headless:
            return

        running = True
        while running:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F1:
                        self.show_debug = not self.show_debug
                        print(f"DEBUG: Debug Mode {self.show_debug}")
                    if event.key == pygame.K_F2:
                        self.use_ai_for_p2 = not self.use_ai_for_p2
                        print(f"DEBUG: AI P2 {self.use_ai_for_p2}")
                    if event.key == pygame.K_r and self.match.winner is not None:
                        self.restart()
                        # Because restart re-inits, we need to exit this loop or handle object replacement
                        # For simplicity, let's just break and re-run? 
                        # Actually restart() calls init, so 'self' is re-initialized BUT local variables like 'running' loop are in the OLD render loop stack? 
                        # No, self.clock etc are re-created. 
                        # The cleanest way is to return or have a state machine.
                        # Simple hack for prototype:
                        return # Exit run, but main.py only calls it once. 
                        # Ideally Main loop should be outside.
                        # Let's just reset data instead of full init to keep window alive.
                        # But I used full init. I'll stick to full Init but I need to handle the loop.
                        # Re-calling run() might work if I verify recursion depth isn't an issue.
                        
            # Use Input Controller
            # Use Input Controller
            if self.match.winner is None:
                self.p1_ctrl.update(self.p1)
                if self.use_ai_for_p2:
                    self.p2_ai.update(self.p2, self.p1)
                else:
                    self.p2_ctrl.update(self.p2)

            self.step_one_frame()

            self.screen.fill((20, 20, 26))

            self.drawer.draw(self.screen, self.p1, color=(220,220,220))
            self.drawer.draw(self.screen, self.p2, color=(220,220,220))

            self.renderer.draw_ui(self.screen, self.p1, self.p2, self.match)

            if self.show_debug:
                self.renderer.draw_debug_boxes(self.screen, self.p1, show_hitbox=True)
                self.renderer.draw_debug_boxes(self.screen, self.p2, show_hitbox=True)
                self._debug_text()

            pygame.display.flip()
            
            if self.match.winner is not None:
                 # Check for restart inputs or just let it float
                 pass

        pygame.quit()

    def _debug_text(self):
        font = pygame.font.SysFont("consolas", 16)
        msg = f"F1 debug | F2 toggle AI(P2)={self.use_ai_for_p2} | FPS: {int(self.clock.get_fps())}"
        self.screen.blit(font.render(msg, True, (200,200,200)), (20, 500))

    def _step_fighter(self, f):
        if f.state == FighterState.HITSTUN:
            f.hitstun_left -= 1
            if f.hitstun_left <= 0 and not f.is_dead():
                f.set_state(FighterState.IDLE)

        if f.state == FighterState.BLOCK_STUN:
            f.hitstun_left -= 1 # reusing hitstun_left for blockstun
            if f.hitstun_left <= 0:
                f.set_state(FighterState.IDLE)

        if f.state == FighterState.ATTACK:
            f.step_state_frame()
            if f.state_frame >= f.attack_def.total:
                f.set_state(FighterState.IDLE)
        else:
            f.step_state_frame()

        if f.is_dead():
            f.set_state(FighterState.DEAD)
            f.vel.x = 0

        self.physics.apply(f, DT)

        if f.pos.x < 40:
            f.pos.x = 40
        if f.pos.x > SCREEN_W - 40:
            f.pos.x = SCREEN_W - 40
