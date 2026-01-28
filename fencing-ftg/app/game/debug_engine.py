from .engine import GameEngine
from .models import ActionType, FencerState, GameMode

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
    # Startup is 5 frames. Then 15 active.
    for i in range(20):
        engine.process_tick({0: ActionType.IDLE, 1: ActionType.IDLE})
        s = engine.state.fencers[0].state
        t = engine.state.fencers[0].state_timer
        print(f"Tick {i+2}: State: {s}, Timer: {t}, Dist: {engine.state.distance}")
        if s == FencerState.ATTACK_ACTIVE and engine.state.last_event:
             # If we hit, last_event should be set? 
             # Wait, engine only checks hits in _check_hits().
             pass
        
        if engine.state.last_event:
            print(f">>> EVENT @ Tick {i+2}: {engine.state.last_event}")
            print(f">>> Score: P1={engine.state.fencers[0].score}")
            break

    # Check score
    print(f"Final Score: P1={engine.state.fencers[0].score}, P2={engine.state.fencers[1].score}")

if __name__ == "__main__":
    test_hit_logic()
