import asyncio
from typing import Dict
from .engine import GameEngine
from .models import ActionType, GameMode
from .ai import SimpleAI

class GameService:
    def __init__(self):
        self.engine = GameEngine()
        self.inputs: Dict[int, ActionType] = {}
        self.running = False
        self.ai = SimpleAI(player_id=1) # AI controls Player 2
        
    def set_player_action(self, player_id: int, action: ActionType):
        self.inputs[player_id] = action

    async def game_loop(self, update_callback):
        self.running = True
        while self.running:
            # 1. Process inputs and tick engine
            
            # P1 Input (Human)
            p1_action = self.inputs.get(0, ActionType.IDLE)
            
            # P2 Input (Human override or AI)
            p2_action = self.inputs.get(1, ActionType.IDLE)
            
            # AI Logic (Only if PVE)
            if self.engine.config.mode == GameMode.PVE:
                p2_action = self.ai.decide(self.engine.state)
            
            current_actions = {
                0: p1_action,
                1: p2_action
            }
            
            self.engine.process_tick(current_actions)
            
            # 2. Broadcast state
            await update_callback(self.engine.state)
            
            # 3. Wait for next tick (60 FPS -> ~0.016s)
            await asyncio.sleep(1/60)

    
    def set_mode(self, mode_str: str):
        try:
            from .models import GameMode
            new_mode = GameMode[mode_str]
            self.engine.config.mode = new_mode
            print(f"Game Mode switched to: {new_mode}")
        except:
            print(f"Invalid mode: {mode_str}")

    def restart_game(self):
        self.engine.reset_game()
        print("Game Restarted")

    def stop(self):
        self.running = False
