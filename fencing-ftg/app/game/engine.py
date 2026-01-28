from .models import Fencer, GameState, ActionType, FencerState, GameConfig
import random

class GameEngine:
    def __init__(self, config: GameConfig = GameConfig()):
        self.config = config
        self.state = GameState(
            fencers=[
                Fencer(id=0, position=4.0), # Left fencer
                Fencer(id=1, position=10.0) # Right fencer
            ]
        )
        self.state.update_distance()

    
    def process_tick(self, actions: dict[int, ActionType]):
        """
        Process one frame of the game.
        actions: dict mapping fencer_id to ActionType
        """
        if self.state.game_over:
            return

        # Handle Freeze/Reset Timer
        if hasattr(self, 'reset_timer') and self.reset_timer > 0:
            self.reset_timer -= 1
            if self.reset_timer == 0:
                self.state.last_event = None # Clear message
                self._reset_positions()
            return # Skip update during freeze

        self.state.tick_count += 1
        # self.state.last_event = None # Don't clear immediately if we want it to persist?
        # Actually logic above clears it after freeze.
        # But if no freeze (normal tick), we usually clear it? 
        # Let's leave last_event as None usually.
        if not hasattr(self, 'reset_timer') or self.reset_timer <= 0:
             self.state.last_event = None # Clear previous frame's event if not frozen

        # 1. Update Fencer States & Timers
        for fencer in self.state.fencers:
            self._update_fencer_state(fencer, actions.get(fencer.id, ActionType.IDLE))

        # 2. Movement Logic
        self._handle_movement()

        # 3. Collision/Boundary Check
        self._enforce_boundaries()

        # 4. Hit Detection
        self._check_hits()

        # 5. Timer Updates
        for fencer in self.state.fencers:
            if fencer.state_timer > 0:
                fencer.state_timer -= 1
            if fencer.state_timer == 0 and fencer.state not in [FencerState.NEUTRAL, FencerState.HIT, FencerState.ATTACK_STARTUP]:
                # Return to neutral after action completes
                fencer.state = FencerState.NEUTRAL
        
        self.state.update_distance()
        self._check_win_condition()

    def _update_fencer_state(self, fencer: Fencer, action: ActionType):
        # Only allow actions if in NEUTRAL state
        if fencer.state != FencerState.NEUTRAL:
            return
            
        fencer.last_action = action
        
        if action == ActionType.STEP_FORWARD:
            fencer.state = FencerState.MOVING_FORWARD
            fencer.state_timer = 10 # Example duration
        elif action == ActionType.STEP_BACK:
            fencer.state = FencerState.MOVING_BACKWARD
            fencer.state_timer = 10
        elif action == ActionType.THRUST:
            fencer.state = FencerState.ATTACK_STARTUP
            fencer.state_timer = 5 # Startup frames
        elif action == ActionType.LUNGE:
            fencer.state = FencerState.ATTACK_STARTUP
            fencer.state_timer = 8 # Longer startup for lunge
            
        # Startup transitions automatically handled in _check_hits or next tick if timer logic used for phases
        # Simplifying: Input directly sets state with timer.
        # For Attack Startup -> Active, we verify timer in main loop.
        
        # Improvement: Handle multi-phase actions (Startup -> Active -> Recovery)
        if fencer.state == FencerState.ATTACK_STARTUP and fencer.state_timer == 0:
             # This block might need to be in the main loop decrement section to transition
             pass

    def _handle_movement(self):
        # Calculate proposed positions
        f1 = self.state.fencers[0]
        f2 = self.state.fencers[1]
        
        move_dist_map = {
            FencerState.MOVING_FORWARD: 0.05,
            FencerState.MOVING_BACKWARD: -0.05,
            FencerState.ATTACK_ACTIVE: 0.1, # Lunge moves forward
        }

        # Apply movement for P1 (moves positive)
        p1_move = 0.0
        if f1.state == FencerState.MOVING_FORWARD: p1_move = f1.move_speed
        elif f1.state == FencerState.MOVING_BACKWARD: p1_move = -f1.move_speed
        elif f1.last_action == ActionType.LUNGE and f1.state == FencerState.ATTACK_ACTIVE: p1_move = f1.lunge_speed
        
        # Apply movement for P2 (moves negative, strictly facing left)
        p2_move = 0.0
        if f2.state == FencerState.MOVING_FORWARD: p2_move = -f2.move_speed # Forward for P2 is decreasing x
        elif f2.state == FencerState.MOVING_BACKWARD: p2_move = f2.move_speed
        elif f2.last_action == ActionType.LUNGE and f2.state == FencerState.ATTACK_ACTIVE: p2_move = -f2.lunge_speed

        f1.position += p1_move
        f2.position += p2_move

    def _enforce_boundaries(self):
        f1 = self.state.fencers[0]
        f2 = self.state.fencers[1]
        
        # Arena limits
        f1.position = max(0.0, min(f1.position, self.config.arena_length))
        f2.position = max(0.0, min(f2.position, self.config.arena_length))
        
        # Player collision (cannot pass each other)
        # Min distance 0.5m
        if f2.position - f1.position < 0.5:
            mid = (f1.position + f2.position) / 2
            f1.position = mid - 0.25
            f2.position = mid + 0.25

    def _check_hits(self):
        # Check simple Transition Startup -> Active
        for fencer in self.state.fencers:
            if fencer.state == FencerState.ATTACK_STARTUP and fencer.state_timer == 0:
                fencer.state = FencerState.ATTACK_ACTIVE
                # Increase active frames to make hitting easier (was 5/10)
                fencer.state_timer = 15 if fencer.last_action == ActionType.THRUST else 25

        f1 = self.state.fencers[0]
        f2 = self.state.fencers[1]
        dist = f2.position - f1.position
        
        # Hit Logic: if attacking and in range
        f1_hit = False
        f2_hit = False
        
        if f1.state == FencerState.ATTACK_ACTIVE:
            if dist <= f1.reach: # SImple reach check
                f1_hit = True
        
        if f2.state == FencerState.ATTACK_ACTIVE:
            if dist <= f2.reach:
                f2_hit = True
                
        if f1_hit and f2_hit:
            # Double touch
            f1.score += 1
            f2.score += 1
            self.state.last_event = "DOUBLE_TOUCH"
            self._start_freeze_frame()
        elif f1_hit:
            f1.score += 1
            self.state.last_event = "P1_POINT"
            self._start_freeze_frame()
        elif f2_hit:
            f2.score += 1
            self.state.last_event = "P2_POINT"
            self._start_freeze_frame()
            
    def _start_freeze_frame(self):
        # We need a way to pause updates for a bit to show the hit
        # Simple hack: Set a global "freeze" timer on the state?
        # Or just abuse state_timer on fencers to keep them showing "HIT"?
        # Let's use a convention: If last_event is set, we might delay reset?
        # But process_tick clears last_event.
        
        # Let's add a simple counter to GameEngine, not GameState to keep model simple?
        # Or just rely on client animation? 
        # Better: Reset positions AFTER a delay.
        # But process_tick runs every frame.
        # We need a 'reset_timer' in GameEngine.
        self.reset_timer = 60 # 1 second freeze

    def _reset_positions(self):
        self.state.fencers[0].position = 4.0
        self.state.fencers[1].position = 10.0
        for f in self.state.fencers:
            f.state = FencerState.NEUTRAL
            f.state_timer = 0
            f.last_action = ActionType.IDLE

    def _check_win_condition(self):
        f1 = self.state.fencers[0]
        f2 = self.state.fencers[1]
        if f1.score >= self.config.max_score or f2.score >= self.config.max_score:
            self.state.game_over = True
            if f1.score > f2.score: self.state.winner = 0
            elif f2.score > f1.score: self.state.winner = 1
            else: self.state.winner = -1 # Tie (Double touch win?)

    def reset_game(self):
        self._reset_positions()
        for f in self.state.fencers:
            f.score = 0
        self.state.game_over = False
        self.state.winner = None
        self.state.last_event = "GAME_RESTART"
        self.state.tick_count = 0
        if hasattr(self, 'reset_timer'):
            self.reset_timer = 0
