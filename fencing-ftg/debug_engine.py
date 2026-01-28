import sys
import os

# Add app to path
sys.path.append(os.getcwd())

from app.game.engine import GameEngine
from app.game.models import ActionType, FencerState, GameMode

def test_hit_logic():
    print("--- Testing Hit Logic ---")
    engine = GameEngine()
    
    # Move players close
    engine.state.fencers[0].position = 4.0
    engine.state.fencers[1].position = 5.0 # Distance = 1.0 (Reach is 1.5)
    engine.state.update_distance()
    print(f"Start Dist: {engine.state.distance}")
    
    # P1 Thrust
    print("P1 Acts: THRUST")
    actions = {0: ActionType.THRUST, 1: ActionType.IDLE}
    engine.process_tick(actions)
    
    print(f"Tick 1: P1 State: {engine.state.fencers[0].state}, Timer: {engine.state.fencers[0].state_timer}")
    
    # Simulate ticks for Startup
    for i in range(10):
        engine.process_tick({0: ActionType.IDLE, 1: ActionType.IDLE})
        s = engine.state.fencers[0].state
        t = engine.state.fencers[0].state_timer
        print(f"Tick {i+2}: State: {s}, Timer: {t}")
        if s == FencerState.ATTACK_ACTIVE:
            print(">>> ENTERED ACTIVE STATE")
        if engine.state.last_event:
            print(f">>> EVENT: {engine.state.last_event}")
            break

    # Check score
    print(f"Final Score: P1={engine.state.fencers[0].score}, P2={engine.state.fencers[1].score}")

if __name__ == "__main__":
    test_hit_logic()
