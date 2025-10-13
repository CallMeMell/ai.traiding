"""
demo_rl_training.py - Demo of RL Training
=========================================
Demonstrates training RL agents (DQN/PPO) for trading.
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime
import os

from rl_environment import TradingEnvironment
from rl_agent import RLAgent, train_rl_agent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_separator(title: str = ""):
    """Print a separator line"""
    print("\n" + "=" * 70)
    if title:
        print(f"  {title}")
        print("=" * 70)


def create_sample_data(n_samples: int = 500) -> pd.DataFrame:
    """Create sample trading data with indicators"""
    np.random.seed(42)
    
    # Generate price data with trend
    prices = 100 + np.cumsum(np.random.randn(n_samples) * 2 + 0.05)
    
    # Calculate indicators
    data = pd.DataFrame({
        'close': prices,
        'volume': np.random.randint(1000, 10000, n_samples),
    })
    
    # RSI
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['rsi'] = 100 - (100 / (1 + rs))
    
    # Moving averages
    data['ma_short'] = data['close'].rolling(window=10).mean()
    data['ma_long'] = data['close'].rolling(window=30).mean()
    
    # Fill NaN values
    data = data.fillna(method='bfill')
    
    return data


def demo_environment_basics():
    """Demo 1: Environment basics"""
    print_separator("Demo 1: RL Environment Basics")
    
    # Create sample data
    data = create_sample_data(n_samples=300)
    
    # Create environment
    env = TradingEnvironment(
        data=data,
        initial_capital=10000.0,
        commission_rate=0.001,
        window_size=30
    )
    
    print(f"\n📊 Environment Created:")
    print(f"   Initial Capital: ${env.initial_capital:,.2f}")
    print(f"   Max Steps: {env.max_steps}")
    print(f"   Action Space: {env.action_space.n} actions")
    print(f"   Observation Shape: {env.observation_space.shape}")
    
    # Reset environment
    obs = env.reset()
    print(f"\n🔄 Environment Reset")
    print(f"   Observation shape: {obs.shape}")
    print(f"   Observation sample: {obs[:5]}")
    
    # Take some random actions
    print(f"\n🎮 Taking Random Actions:")
    for i in range(5):
        action = np.random.randint(0, 21)
        obs, reward, done, info = env.step(action)
        
        print(f"\n   Step {i+1}:")
        print(f"   - Action: {action}")
        print(f"   - Reward: {reward:.4f}")
        print(f"   - Portfolio Value: ${info['portfolio_value']:.2f}")
        print(f"   - Position: {info['position']}")
    
    # Get final metrics
    print(f"\n📈 Performance Metrics:")
    metrics = env.get_performance_metrics()
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.2f}")
        else:
            print(f"   {key}: {value}")


def demo_ppo_training():
    """Demo 2: Train PPO agent"""
    print_separator("Demo 2: Training PPO Agent")
    
    # Create training and evaluation data
    train_data = create_sample_data(n_samples=400)
    eval_data = create_sample_data(n_samples=100)
    
    print(f"\n📚 Data Prepared:")
    print(f"   Training samples: {len(train_data)}")
    print(f"   Evaluation samples: {len(eval_data)}")
    
    # Create environments
    train_env = TradingEnvironment(train_data, initial_capital=10000.0)
    eval_env = TradingEnvironment(eval_data, initial_capital=10000.0)
    
    # Create agent
    print(f"\n🤖 Creating PPO Agent...")
    agent = RLAgent(algorithm='PPO', env=train_env, model_dir='models/rl_demo')
    
    # Create model with custom hyperparameters
    agent.create_model(
        learning_rate=0.0003,
        n_steps=2048,
        batch_size=64
    )
    
    print(f"   Model created with PPO algorithm")
    print(f"   Policy: MlpPolicy")
    
    # Train (using fewer timesteps for demo)
    print(f"\n🎯 Training Agent...")
    print(f"   Training timesteps: 10,000 (reduced for demo)")
    
    training_info = agent.train(
        total_timesteps=10000,
        log_interval=2000,
        eval_env=eval_env,
        eval_freq=5000
    )
    
    print(f"\n✅ Training Complete!")
    print(f"   Training time: {training_info['training_time']:.2f} seconds")
    
    # Evaluate trained agent
    print(f"\n📊 Evaluating Agent...")
    eval_metrics = agent.evaluate(eval_env, n_episodes=5)
    
    print(f"\n📈 Evaluation Results:")
    print(f"   Mean Reward: {eval_metrics['mean_reward']:.2f}")
    print(f"   Mean ROI: {eval_metrics['mean_roi']:.2f}%")
    print(f"   Mean Sharpe: {eval_metrics['mean_sharpe']:.2f}")
    print(f"   Mean Drawdown: {eval_metrics['mean_drawdown']:.2f}%")
    
    # Save model
    model_path = agent.save_model('demo_ppo')
    print(f"\n💾 Model saved to: {model_path}")


def demo_dqn_training():
    """Demo 3: Train DQN agent"""
    print_separator("Demo 3: Training DQN Agent")
    
    # Create data
    train_data = create_sample_data(n_samples=400)
    
    print(f"\n📚 Data Prepared: {len(train_data)} samples")
    
    # Create environment
    train_env = TradingEnvironment(train_data, initial_capital=10000.0)
    
    # Create DQN agent
    print(f"\n🤖 Creating DQN Agent...")
    agent = RLAgent(algorithm='DQN', env=train_env, model_dir='models/rl_demo')
    
    agent.create_model(
        learning_rate=0.0001,
        buffer_size=50000,
        batch_size=32
    )
    
    print(f"   Model created with DQN algorithm")
    
    # Train
    print(f"\n🎯 Training Agent (10,000 timesteps)...")
    agent.train(total_timesteps=10000, log_interval=2000)
    
    print(f"\n✅ DQN Training Complete!")
    
    # Save
    model_path = agent.save_model('demo_dqn')
    print(f"💾 Model saved to: {model_path}")


def demo_agent_inference():
    """Demo 4: Using trained agent for inference"""
    print_separator("Demo 4: Agent Inference")
    
    # Create test data
    test_data = create_sample_data(n_samples=200)
    test_env = TradingEnvironment(test_data, initial_capital=10000.0)
    
    print(f"\n🧪 Test Data: {len(test_data)} samples")
    
    # Create and train a simple agent for demo
    print(f"\n🤖 Training quick agent for inference demo...")
    agent = RLAgent(algorithm='PPO', env=test_env, model_dir='models/rl_demo')
    agent.create_model()
    agent.train(total_timesteps=5000, log_interval=5000)
    
    # Run inference
    print(f"\n🔮 Running Inference...")
    obs = test_env.reset()
    
    total_reward = 0
    steps = 0
    
    for _ in range(50):
        # Get action from agent
        action, _ = agent.predict(obs, deterministic=True)
        
        # Take action
        obs, reward, done, info = test_env.step(action)
        
        total_reward += reward
        steps += 1
        
        if done:
            break
    
    # Get final metrics
    metrics = test_env.get_performance_metrics()
    
    print(f"\n📊 Inference Results:")
    print(f"   Steps: {steps}")
    print(f"   Total Reward: {total_reward:.2f}")
    print(f"   Final Portfolio Value: ${metrics['final_value']:.2f}")
    print(f"   ROI: {metrics['roi']:.2f}%")
    print(f"   Total Trades: {metrics['total_trades']}")


def main():
    """Run all demos"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 20 + "RL Trading Demo" + " " * 33 + "║")
    print("╚" + "=" * 68 + "╝")
    
    # Run demos
    demo_environment_basics()
    demo_ppo_training()
    demo_dqn_training()
    demo_agent_inference()
    
    print_separator("All Demos Complete!")
    print("\n📝 Next Steps:")
    print("   1. Experiment with hyperparameters in hyperparameter_tuning.py")
    print("   2. Train on your own data")
    print("   3. Deploy models via ml_api.py")
    print("   4. Integrate with your trading strategy")
    print("")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
