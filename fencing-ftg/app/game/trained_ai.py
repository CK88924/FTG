from stable_baselines3 import PPO
from .models import ActionType, FencerState
from .engine import GameEngine
import numpy as np
import os
from collections import deque

class TrainedAI:
    def __init__(self, model_path="app/models/ppo_fencing.zip", reaction_delay=15):
        self.model = None
        if os.path.exists(model_path):
            print(f"Loading trained model from {model_path}...")
            self.model = PPO.load(model_path)
        else:
            print(f"No trained model found at {model_path}.")
            
        self.state_map = {
            FencerState.NEUTRAL: 0,
            FencerState.MOVING_FORWARD: 1,
            FencerState.MOVING_BACKWARD: 2,
            FencerState.ATTACK_STARTUP: 3,
            FencerState.ATTACK_ACTIVE: 4,
            FencerState.RECOVERY: 5,
            FencerState.HIT: 6
        }
        
        # Reaction Delay
        self.reaction_delay = reaction_delay
        self.obs_buffer = deque(maxlen=reaction_delay)

    def process(self, engine: GameEngine, my_player_index: int, opponent_index: int) -> ActionType:
        if not self.model:
            return ActionType.IDLE

        # Construct Observation matching Gym Env
        eng = engine.state
        p1 = eng.fencers[opponent_index] # Opponent (usually P1 if AI is P2)
        p2 = eng.fencers[my_player_index] # AI (usually P2)
        
        # The model was trained as Player 1 (Left Start, Pos ~2.0).
        # When playing as Player 2 (Right Start, Pos ~12.0), the coordinate inputs are out of distribution.
        # We must "Mirror" the world so the AI thinks it is Player 1.
        # Arena Length = 14.0
        
        # Mirror Logic:
        # Real P2 Pos = 12.0 -> Virtual P1 Pos = 14.0 - 12.0 = 2.0 (Matches training)
        # Real P1 Pos = 2.0  -> Virtual P2 Pos = 14.0 - 2.0 = 12.0 (Matches training)
        
        my_virtual_pos = 14.0 - p2.position
        op_virtual_pos = 14.0 - p1.position
        
        current_obs = np.array([
            eng.distance,
            my_virtual_pos,   # My Virtual Pos (looks like P1)
            op_virtual_pos,   # Op Virtual Pos (looks like P2)
            self.state_map.get(p2.state, 0), # My State
            self.state_map.get(p1.state, 0), # Op State
            p2.score,         # My Score
            p1.score          # Op Score
        ], dtype=np.float32)
        
        # --- Reaction Delay Logic ---
        self.obs_buffer.append(current_obs)
        
        # If buffer isn't full yet (start of game), just use current
        # But effectively we want the "delayed" obs which is at the LEFT of the deque
        if len(self.obs_buffer) < self.reaction_delay:
             delayed_obs = current_obs
        else:
             delayed_obs = self.obs_buffer[0] # The oldest observation
        
        action_idx, _ = self.model.predict(delayed_obs, deterministic=True)
        
        # Map back to ActionType
        act_map = {
            0: ActionType.IDLE,
            1: ActionType.STEP_FORWARD,
            2: ActionType.STEP_BACK,
            3: ActionType.THRUST,
            4: ActionType.LUNGE
        }
        return act_map.get(int(action_idx), ActionType.IDLE)
