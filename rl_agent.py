"""
rl_agent.py - Reinforcement Learning Agent Wrapper
==================================================
Wrapper for training and using RL agents (DQN, PPO) with Stable-Baselines3.
"""

import os
import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime
import numpy as np
import pandas as pd

from stable_baselines3 import DQN, PPO
from stable_baselines3.common.callbacks import BaseCallback, EvalCallback
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.monitor import Monitor

from rl_environment import TradingEnvironment

logger = logging.getLogger(__name__)


class TrainingCallback(BaseCallback):
    """
    Custom callback for tracking training progress
    """
    
    def __init__(self, log_interval: int = 100, verbose: int = 0):
        super(TrainingCallback, self).__init__(verbose)
        self.log_interval = log_interval
        self.episode_rewards = []
        self.episode_lengths = []
    
    def _on_step(self) -> bool:
        # Log every N steps
        if self.n_calls % self.log_interval == 0:
            logger.info(f"Training step: {self.n_calls}")
        return True
    
    def _on_rollout_end(self) -> None:
        """Called at the end of a rollout"""
        if len(self.model.ep_info_buffer) > 0:
            ep_info = self.model.ep_info_buffer[-1]
            self.episode_rewards.append(ep_info['r'])
            self.episode_lengths.append(ep_info['l'])


class RLAgent:
    """
    Reinforcement Learning Agent for Trading
    
    Supports DQN and PPO algorithms from Stable-Baselines3
    """
    
    def __init__(
        self,
        algorithm: str = 'PPO',
        env: Optional[TradingEnvironment] = None,
        model_dir: str = 'models/rl',
        **model_kwargs
    ):
        """
        Initialize RL Agent
        
        Args:
            algorithm: 'DQN' or 'PPO'
            env: Trading environment
            model_dir: Directory to save models
            **model_kwargs: Additional arguments for the model
        """
        self.algorithm = algorithm.upper()
        self.env = env
        self.model_dir = model_dir
        self.model = None
        self.model_kwargs = model_kwargs
        
        # Create model directory
        os.makedirs(model_dir, exist_ok=True)
        
        if self.algorithm not in ['DQN', 'PPO']:
            raise ValueError(f"Unsupported algorithm: {algorithm}. Use 'DQN' or 'PPO'.")
        
        logger.info(f"RLAgent initialized with {self.algorithm}")
    
    def create_model(
        self,
        env: Optional[TradingEnvironment] = None,
        policy: str = 'MlpPolicy',
        **kwargs
    ):
        """
        Create a new model
        
        Args:
            env: Trading environment (uses self.env if not provided)
            policy: Policy network type
            **kwargs: Model-specific parameters
        """
        if env is not None:
            self.env = env
        
        if self.env is None:
            raise ValueError("Environment must be provided")
        
        # Wrap environment
        wrapped_env = DummyVecEnv([lambda: Monitor(self.env)])
        
        # Merge kwargs
        model_params = {**self.model_kwargs, **kwargs}
        
        # Create model based on algorithm
        if self.algorithm == 'DQN':
            self.model = DQN(
                policy,
                wrapped_env,
                verbose=1,
                **model_params
            )
            logger.info("DQN model created")
        
        elif self.algorithm == 'PPO':
            self.model = PPO(
                policy,
                wrapped_env,
                verbose=1,
                **model_params
            )
            logger.info("PPO model created")
        
        return self.model
    
    def train(
        self,
        total_timesteps: int = 100000,
        log_interval: int = 1000,
        eval_freq: int = 10000,
        eval_env: Optional[TradingEnvironment] = None,
        save_freq: int = 10000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Train the RL agent
        
        Args:
            total_timesteps: Total training steps
            log_interval: How often to log progress
            eval_freq: How often to evaluate the agent
            eval_env: Environment for evaluation
            save_freq: How often to save the model
            **kwargs: Additional training arguments
        
        Returns:
            Training metrics
        """
        if self.model is None:
            raise ValueError("Model not created. Call create_model() first.")
        
        # Create callbacks
        callbacks = [TrainingCallback(log_interval=log_interval)]
        
        # Add evaluation callback if eval_env provided
        if eval_env is not None:
            eval_callback = EvalCallback(
                DummyVecEnv([lambda: Monitor(eval_env)]),
                eval_freq=eval_freq,
                best_model_save_path=os.path.join(self.model_dir, 'best_model'),
                log_path=os.path.join(self.model_dir, 'eval_logs'),
                deterministic=True,
                render=False
            )
            callbacks.append(eval_callback)
        
        logger.info(f"Starting training for {total_timesteps} timesteps...")
        
        # Train
        start_time = datetime.now()
        self.model.learn(
            total_timesteps=total_timesteps,
            callback=callbacks,
            **kwargs
        )
        training_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Training completed in {training_time:.2f} seconds")
        
        # Save final model
        self.save_model('final_model')
        
        return {
            'total_timesteps': total_timesteps,
            'training_time': training_time,
            'algorithm': self.algorithm
        }
    
    def predict(
        self,
        observation: np.ndarray,
        deterministic: bool = True
    ) -> tuple:
        """
        Predict action for given observation
        
        Args:
            observation: Current state
            deterministic: Whether to use deterministic policy
        
        Returns:
            action, state
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call create_model() or load_model() first.")
        
        action, state = self.model.predict(observation, deterministic=deterministic)
        return action, state
    
    def evaluate(
        self,
        env: TradingEnvironment,
        n_episodes: int = 10,
        deterministic: bool = True
    ) -> Dict[str, float]:
        """
        Evaluate the agent on an environment
        
        Args:
            env: Environment to evaluate on
            n_episodes: Number of episodes to run
            deterministic: Use deterministic policy
        
        Returns:
            Evaluation metrics
        """
        if self.model is None:
            raise ValueError("Model not loaded")
        
        episode_rewards = []
        episode_lengths = []
        all_metrics = []
        
        for episode in range(n_episodes):
            obs = env.reset()
            done = False
            episode_reward = 0
            episode_length = 0
            
            while not done:
                action, _ = self.predict(obs, deterministic=deterministic)
                obs, reward, done, info = env.step(action)
                episode_reward += reward
                episode_length += 1
            
            episode_rewards.append(episode_reward)
            episode_lengths.append(episode_length)
            
            # Get performance metrics
            metrics = env.get_performance_metrics()
            all_metrics.append(metrics)
            
            logger.info(f"Episode {episode + 1}/{n_episodes}: "
                       f"Reward={episode_reward:.2f}, "
                       f"ROI={metrics.get('roi', 0):.2f}%")
        
        # Aggregate metrics
        avg_roi = np.mean([m.get('roi', 0) for m in all_metrics])
        avg_sharpe = np.mean([m.get('sharpe_ratio', 0) for m in all_metrics])
        avg_drawdown = np.mean([m.get('max_drawdown', 0) for m in all_metrics])
        
        return {
            'mean_reward': np.mean(episode_rewards),
            'std_reward': np.std(episode_rewards),
            'mean_episode_length': np.mean(episode_lengths),
            'mean_roi': avg_roi,
            'mean_sharpe': avg_sharpe,
            'mean_drawdown': avg_drawdown,
            'n_episodes': n_episodes
        }
    
    def save_model(self, name: str = 'model'):
        """Save the trained model"""
        if self.model is None:
            raise ValueError("No model to save")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.algorithm}_{name}_{timestamp}"
        filepath = os.path.join(self.model_dir, filename)
        
        self.model.save(filepath)
        logger.info(f"Model saved to {filepath}")
        
        return filepath
    
    def load_model(self, filepath: str):
        """Load a trained model"""
        if not os.path.exists(filepath + '.zip'):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        if self.algorithm == 'DQN':
            self.model = DQN.load(filepath)
        elif self.algorithm == 'PPO':
            self.model = PPO.load(filepath)
        
        logger.info(f"Model loaded from {filepath}")
        return self.model
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model"""
        if self.model is None:
            return {}
        
        return {
            'algorithm': self.algorithm,
            'policy': str(self.model.policy),
            'n_envs': self.model.n_envs,
            'observation_space': str(self.model.observation_space),
            'action_space': str(self.model.action_space)
        }


def create_training_environment(
    data: pd.DataFrame,
    initial_capital: float = 10000.0,
    **kwargs
) -> TradingEnvironment:
    """
    Helper function to create a training environment
    
    Args:
        data: Historical data with OHLCV and indicators
        initial_capital: Starting capital
        **kwargs: Additional environment parameters
    
    Returns:
        TradingEnvironment instance
    """
    return TradingEnvironment(
        data=data,
        initial_capital=initial_capital,
        **kwargs
    )


def train_rl_agent(
    algorithm: str,
    train_data: pd.DataFrame,
    eval_data: Optional[pd.DataFrame] = None,
    initial_capital: float = 10000.0,
    total_timesteps: int = 100000,
    model_dir: str = 'models/rl',
    **kwargs
) -> RLAgent:
    """
    Convenience function to train an RL agent
    
    Args:
        algorithm: 'DQN' or 'PPO'
        train_data: Training data
        eval_data: Evaluation data (optional)
        initial_capital: Starting capital
        total_timesteps: Training steps
        model_dir: Model save directory
        **kwargs: Additional parameters
    
    Returns:
        Trained RLAgent
    """
    # Create environments
    train_env = create_training_environment(train_data, initial_capital)
    eval_env = None
    if eval_data is not None:
        eval_env = create_training_environment(eval_data, initial_capital)
    
    # Create agent
    agent = RLAgent(algorithm=algorithm, env=train_env, model_dir=model_dir)
    
    # Create model
    agent.create_model()
    
    # Train
    agent.train(
        total_timesteps=total_timesteps,
        eval_env=eval_env,
        **kwargs
    )
    
    return agent
