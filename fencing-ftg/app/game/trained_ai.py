from stable_baselines3 import PPO
from .models import ActionType, FencerState
from .engine import GameEngine
import numpy as np
import os

class TrainedAI:
    def __init__(self, model_path="app/models/ppo_fencing.zip"):
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

    def process(self, engine: GameEngine, my_player_index: int, opponent_index: int) -> ActionType:
        if not self.model:
            return ActionType.IDLE

        # Construct Observation matching Gym Env
        eng = engine.state
        p1 = eng.fencers[opponent_index] # Opponent (usually P1 if AI is P2)
        p2 = eng.fencers[my_player_index] # AI (usually P2)
        
        # Note: Gym Env assumes Agent is P1 (index 0). 
        # But here AI is P2 (index 1).
        # We need to feed the observation AS IF the AI is the agent.
        # So we swap positions? 
        # Wait, the Gym Env defined Obs as [Distance, P1_Pos, P2_Pos, ...]
        # PPO model learned that "P1_Pos" is "My Pos". 
        # So if AI is P2, we should probably map:
        # P1_Pos -> AI's Pos (P2)
        # P2_Pos -> Opponent's Pos (P1)
        # But wait, distance is symmetric.
        # Let's stick to the Gym Env definition:
        # Obs = [Distance, P1.pos, P2.pos, P1.state, P2.state, ...]
        # If the model was trained controlling P1 against a Dummy P2:
        # Then "My Pos" input was index 1.
        # If we use this model to control P2, we might need to be careful.
        # However, for now, let's just pass the raw state and see. 
        # If the model learned "I am Player 1", it might get confused if used for Player 2.
        # Ideally we should train an agent for P2 specifically, OR mirror the inputs.
        
        # The model was trained as Player 1 (Left Start, Pos ~2.0).
        # When playing as Player 2 (Right Start, Pos ~12.0), the coordinate inputs are out of distribution.
        # We must "Mirror" the world so the AI thinks it is Player 1.
        # Arena Length = 14.0
        
        # Mirror Logic:
        # Real P2 Pos = 12.0 -> Virtual P1 Pos = 14.0 - 12.0 = 2.0 (Matches training)
        # Real P1 Pos = 2.0  -> Virtual P2 Pos = 14.0 - 2.0 = 12.0 (Matches training)
        
        my_virtual_pos = 14.0 - p2.position
        op_virtual_pos = 14.0 - p1.position
        
        obs = np.array([
            eng.distance,
            my_virtual_pos,   # My Virtual Pos (looks like P1)
            op_virtual_pos,   # Op Virtual Pos (looks like P2)
            self.state_map.get(p2.state, 0), # My State
            self.state_map.get(p1.state, 0), # Op State
            p2.score,         # My Score
            p1.score          # Op Score
        ], dtype=np.float32)

        action_idx, _ = self.model.predict(obs, deterministic=True)
        
        # Map back to ActionType
        act_map = {
            0: ActionType.IDLE,
            1: ActionType.STEP_FORWARD,
            2: ActionType.STEP_BACK,
            3: ActionType.THRUST,
            4: ActionType.LUNGE
        }
        return act_map.get(int(action_idx), ActionType.IDLE)
