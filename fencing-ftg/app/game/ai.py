from .models import GameState, ActionType, FencerState, Fencer
import random

class SimpleAI:
    def __init__(self, player_id: int):
        self.player_id = player_id
        # Reaction delay or randomness can be added here
        self.tick_counter = 0
        self.action_cooldown = 0

    def decide(self, game_state: GameState) -> ActionType:
        self.tick_counter += 1
        if self.action_cooldown > 0:
            self.action_cooldown -= 1
            return ActionType.IDLE

        me: Fencer = game_state.fencers[self.player_id]
        opponent: Fencer = game_state.fencers[1 - self.player_id]
        
        # Extract useful info
        # Check distance
        # NOTE: GameState distance is absolute.
        # But positions are absolute.
        # P1 (0) is on Left (small x), P2 (1) is on Right (large x).
        # Distance = P2.x - P1.x
        
        dist = abs(me.position - opponent.position)
        
        # Simple Logic
        # 1. If opponent attacking, try to retreat (step back)
        if opponent.state in [FencerState.ATTACK_STARTUP, FencerState.ATTACK_ACTIVE] and dist < 2.5:
             # Retreat!
             self.action_cooldown = 5
             return ActionType.STEP_BACK
             
        # 2. If range is too far, get closer
        if dist > 3.0:
            return ActionType.STEP_FORWARD
            
        # 3. If range is Optimal (around 2.0), try to attack or dither
        if 1.5 <= dist <= 2.5:
            dice = random.random()
            if dice < 0.05: # Small chance to attack per tick
                self.action_cooldown = 20
                return ActionType.THRUST
            elif dice < 0.06: # Even smaller chance to lunge
                self.action_cooldown = 30
                return ActionType.LUNGE
            elif dice < 0.10: # Adjustment steps
                if dist > 2.2: return ActionType.STEP_FORWARD
                if dist < 1.8: return ActionType.STEP_BACK
        
        # 4. If too close, back off
        if dist < 1.5:
            return ActionType.STEP_BACK
            
        return ActionType.IDLE
