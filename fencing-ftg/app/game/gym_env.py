import gymnasium as gym
from gymnasium import spaces
import numpy as np
from .engine import GameEngine
from .models import ActionType, FencerState, GameMode

class FencingEnv(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 60}

    def __init__(self, render_mode=None):
        self.engine = GameEngine()
        # Set to P2 mode just in case, though for Gym usually we control P1?
        # Let's assume the Agent controls Player 1 (Left). 
        # Opponent (P2) will be controlled by Rule-based AI or random (can be configured).
        
        # Action Space: 0: IDLE, 1: FORWARD, 2: BACK, 3: THRUST, 4: LUNGE
        self.action_space = spaces.Discrete(5)
        
        # Observation Space
        # [Distance, P1_Pos, P2_Pos, P1_State, P2_State, P1_Score, P2_Score]
        # State Enum mapped to int
        self.observation_space = spaces.Box(
            low=np.array([0.0, 0.0, 0.0, 0, 0, 0, 0], dtype=np.float32),
            high=np.array([14.0, 14.0, 14.0, 10, 10, 5, 5], dtype=np.float32),
            dtype=np.float32
        )
        
        self.state_map = {
            FencerState.NEUTRAL: 0,
            FencerState.MOVING_FORWARD: 1,
            FencerState.MOVING_BACKWARD: 2,
            FencerState.ATTACK_STARTUP: 3,
            FencerState.ATTACK_ACTIVE: 4,
            FencerState.RECOVERY: 5,
            FencerState.HIT: 6
        }
        
    def _get_obs(self):
        eng = self.engine.state
        p1 = eng.fencers[0]
        p2 = eng.fencers[1]
        
        return np.array([
            eng.distance,
            p1.position,
            p2.position,
            self.state_map.get(p1.state, 0),
            self.state_map.get(p2.state, 0),
            p1.score,
            p2.score
        ], dtype=np.float32)
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.engine.reset_game()
        # Ensure mode is PVE if we want built-in AI for P2? 
        # Actually engine doesn't run AI self-contained, Service does.
        # So here we need to manually move P2 or inject a "bot" step.
        return self._get_obs(), {}

    def step(self, action):
        # Map Discrete action to ActionType
        act_map = {
            0: ActionType.IDLE,
            1: ActionType.STEP_FORWARD,
            2: ActionType.STEP_BACK,
            3: ActionType.THRUST,
            4: ActionType.LUNGE
        }
        

        
        # Action might be a numpy array (0-d), cast to int
        if isinstance(action, np.ndarray):
            action = int(action)
            
        p1_action = act_map.get(action, ActionType.IDLE)
        
        # Simple Opponent AI (Random walk + attack)
        # In a real training loop, you might want a smarter opponent or self-play.
        # Here we do a very dumb random opponent.
        p2_action = ActionType.IDLE
        if self.engine.state.distance > 2.5:
             p2_action = ActionType.STEP_FORWARD # P2 forward moves left (closer)
        elif self.engine.state.distance < 1.0:
             p2_action = ActionType.STEP_BACK
        else:
             if np.random.rand() < 0.05: p2_action = ActionType.THRUST
        
        actions = {0: p1_action, 1: p2_action}
        
        self.engine.process_tick(actions)
        
        obs = self._get_obs()
        
        # Reward Calculation
        reward = -0.001 # Time penalty
        terminated = False
        truncated = False
        
        if self.engine.state.last_event == "P1_POINT":
            reward += 1.0
        elif self.engine.state.last_event == "P2_POINT":
            reward -= 1.0
        elif self.engine.state.last_event == "DOUBLE_TOUCH":
            reward -= 0.2
            
        if self.engine.state.game_over:
            terminated = True
            if self.engine.state.winner == 0:
                reward += 10.0 # Win Bonus
            elif self.engine.state.winner == 1:
                reward -= 10.0 # Loss Penalty
                
        return obs, reward, terminated, truncated, {}
