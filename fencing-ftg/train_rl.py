import gymnasium as gym
from stable_baselines3 import PPO
from app.game.gym_env import FencingEnv
import os

def train():
    # 1. Create the environment
    # Using the class directly or registering it. 
    # Since we have the class, we can just instantiate it.
    env = FencingEnv()

    # 2. Define the model
    # MlpPolicy is suitable for vector observations.
    model = PPO("MlpPolicy", env, verbose=1, learning_rate=0.0003)

    # 3. Train the model
    # For a quick demo, we train for 10,000 steps. 
    # For a "Smart" AI, you might need 1M+ steps.
    print("Starting training...")
    try:
        model.learn(total_timesteps=10000)
    except KeyboardInterrupt:
        print("Training interrupted manually.")

    # 4. Save the model
    os.makedirs("app/models", exist_ok=True)
    model_path = "app/models/ppo_fencing"
    model.save(model_path)
    print(f"Model saved to {model_path}.zip")

    # 5. Optional: Test the model
    obs, _ = env.reset()
    print("Testing model...")
    for _ in range(10):
        action, _states = model.predict(obs, deterministic=True)
        obs, rewards, terminated, truncated, info = env.step(action)
        if terminated or truncated:
            obs, _ = env.reset()

if __name__ == "__main__":
    train()
