"""
hyperparameter_tuning.py - Hyperparameter Optimization with Optuna
==================================================================
Automated hyperparameter tuning for RL agents and trading strategies.
"""

import optuna
from optuna.pruners import MedianPruner
from optuna.samplers import TPESampler
import logging
from typing import Dict, Any, Optional, Callable
import numpy as np
import pandas as pd
import json
import os
from datetime import datetime

from rl_environment import TradingEnvironment
from rl_agent import RLAgent

logger = logging.getLogger(__name__)


class HyperparameterTuner:
    """
    Hyperparameter tuner using Optuna for RL agents
    """
    
    def __init__(
        self,
        study_name: str,
        direction: str = 'maximize',
        storage: Optional[str] = None,
        sampler: Optional[optuna.samplers.BaseSampler] = None,
        pruner: Optional[optuna.pruners.BasePruner] = None
    ):
        """
        Initialize hyperparameter tuner
        
        Args:
            study_name: Name of the study
            direction: 'maximize' or 'minimize'
            storage: Optuna storage URL (e.g., 'sqlite:///optuna.db')
            sampler: Optuna sampler (default: TPESampler)
            pruner: Optuna pruner (default: MedianPruner)
        """
        self.study_name = study_name
        self.direction = direction
        
        if sampler is None:
            sampler = TPESampler(seed=42)
        
        if pruner is None:
            pruner = MedianPruner(n_startup_trials=5, n_warmup_steps=10)
        
        self.study = optuna.create_study(
            study_name=study_name,
            direction=direction,
            sampler=sampler,
            pruner=pruner,
            storage=storage,
            load_if_exists=True
        )
        
        logger.info(f"HyperparameterTuner initialized: {study_name}")
    
    def objective_rl_agent(
        self,
        trial: optuna.Trial,
        algorithm: str,
        train_data: pd.DataFrame,
        eval_data: pd.DataFrame,
        initial_capital: float = 10000.0,
        training_timesteps: int = 50000
    ) -> float:
        """
        Objective function for RL agent hyperparameter optimization
        
        Args:
            trial: Optuna trial
            algorithm: 'DQN' or 'PPO'
            train_data: Training data
            eval_data: Evaluation data
            initial_capital: Starting capital
            training_timesteps: Number of training steps
        
        Returns:
            Metric to optimize (e.g., mean ROI)
        """
        # Sample hyperparameters
        if algorithm == 'PPO':
            hyperparams = {
                'learning_rate': trial.suggest_float('learning_rate', 1e-5, 1e-3, log=True),
                'n_steps': trial.suggest_categorical('n_steps', [128, 256, 512, 1024, 2048]),
                'batch_size': trial.suggest_categorical('batch_size', [32, 64, 128, 256]),
                'n_epochs': trial.suggest_int('n_epochs', 3, 30),
                'gamma': trial.suggest_float('gamma', 0.9, 0.9999, log=True),
                'gae_lambda': trial.suggest_float('gae_lambda', 0.8, 0.99),
                'clip_range': trial.suggest_float('clip_range', 0.1, 0.4),
                'ent_coef': trial.suggest_float('ent_coef', 1e-8, 0.1, log=True)
            }
        
        elif algorithm == 'DQN':
            hyperparams = {
                'learning_rate': trial.suggest_float('learning_rate', 1e-5, 1e-3, log=True),
                'buffer_size': trial.suggest_categorical('buffer_size', [10000, 50000, 100000]),
                'batch_size': trial.suggest_categorical('batch_size', [32, 64, 128, 256]),
                'gamma': trial.suggest_float('gamma', 0.9, 0.9999, log=True),
                'exploration_fraction': trial.suggest_float('exploration_fraction', 0.1, 0.5),
                'exploration_final_eps': trial.suggest_float('exploration_final_eps', 0.01, 0.1),
                'target_update_interval': trial.suggest_int('target_update_interval', 1000, 10000)
            }
        
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        try:
            # Create environments
            train_env = TradingEnvironment(train_data, initial_capital=initial_capital)
            eval_env = TradingEnvironment(eval_data, initial_capital=initial_capital)
            
            # Create and train agent
            agent = RLAgent(algorithm=algorithm, env=train_env)
            agent.create_model(**hyperparams)
            
            # Train with fewer timesteps for tuning
            agent.train(
                total_timesteps=training_timesteps,
                log_interval=training_timesteps // 10
            )
            
            # Evaluate
            eval_metrics = agent.evaluate(eval_env, n_episodes=5)
            
            # Return metric to optimize (mean ROI)
            metric = eval_metrics['mean_roi']
            
            # Log trial results
            logger.info(f"Trial {trial.number}: ROI={metric:.2f}%, Sharpe={eval_metrics['mean_sharpe']:.2f}")
            
            return metric
        
        except Exception as e:
            logger.error(f"Trial {trial.number} failed: {e}")
            return -np.inf if self.direction == 'maximize' else np.inf
    
    def optimize(
        self,
        objective_func: Callable,
        n_trials: int = 50,
        timeout: Optional[int] = None,
        n_jobs: int = 1,
        show_progress_bar: bool = True,
        **objective_kwargs
    ) -> Dict[str, Any]:
        """
        Run hyperparameter optimization
        
        Args:
            objective_func: Objective function to optimize
            n_trials: Number of trials
            timeout: Timeout in seconds
            n_jobs: Number of parallel jobs
            show_progress_bar: Show progress bar
            **objective_kwargs: Arguments for objective function
        
        Returns:
            Best hyperparameters and results
        """
        logger.info(f"Starting optimization: {n_trials} trials")
        
        # Create objective with kwargs
        def objective(trial):
            return objective_func(trial, **objective_kwargs)
        
        # Optimize
        self.study.optimize(
            objective,
            n_trials=n_trials,
            timeout=timeout,
            n_jobs=n_jobs,
            show_progress_bar=show_progress_bar
        )
        
        # Get results
        best_params = self.study.best_params
        best_value = self.study.best_value
        
        logger.info(f"Optimization completed. Best value: {best_value:.4f}")
        logger.info(f"Best parameters: {best_params}")
        
        return {
            'best_params': best_params,
            'best_value': best_value,
            'n_trials': len(self.study.trials),
            'best_trial': self.study.best_trial.number
        }
    
    def get_best_params(self) -> Dict[str, Any]:
        """Get best hyperparameters"""
        return self.study.best_params
    
    def get_best_value(self) -> float:
        """Get best objective value"""
        return self.study.best_value
    
    def get_optimization_history(self) -> pd.DataFrame:
        """Get optimization history as DataFrame"""
        trials_df = self.study.trials_dataframe()
        return trials_df
    
    def save_results(self, filepath: str):
        """Save optimization results to JSON"""
        results = {
            'study_name': self.study_name,
            'direction': self.direction,
            'best_params': self.study.best_params,
            'best_value': self.study.best_value,
            'n_trials': len(self.study.trials),
            'timestamp': datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Results saved to {filepath}")
    
    def plot_optimization_history(self, filepath: Optional[str] = None):
        """Plot optimization history"""
        try:
            import matplotlib.pyplot as plt
            
            fig = optuna.visualization.matplotlib.plot_optimization_history(self.study)
            
            if filepath:
                fig.savefig(filepath)
                logger.info(f"Plot saved to {filepath}")
            else:
                plt.show()
            
            plt.close()
        
        except Exception as e:
            logger.warning(f"Could not plot optimization history: {e}")
    
    def plot_param_importances(self, filepath: Optional[str] = None):
        """Plot parameter importances"""
        try:
            import matplotlib.pyplot as plt
            
            fig = optuna.visualization.matplotlib.plot_param_importances(self.study)
            
            if filepath:
                fig.savefig(filepath)
                logger.info(f"Plot saved to {filepath}")
            else:
                plt.show()
            
            plt.close()
        
        except Exception as e:
            logger.warning(f"Could not plot parameter importances: {e}")


def tune_rl_agent(
    algorithm: str,
    train_data: pd.DataFrame,
    eval_data: pd.DataFrame,
    study_name: str = 'rl_agent_tuning',
    n_trials: int = 50,
    training_timesteps: int = 50000,
    initial_capital: float = 10000.0,
    save_results: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to tune RL agent hyperparameters
    
    Args:
        algorithm: 'DQN' or 'PPO'
        train_data: Training data
        eval_data: Evaluation data
        study_name: Name for the study
        n_trials: Number of optimization trials
        training_timesteps: Steps per trial
        initial_capital: Starting capital
        save_results: Save results to file
    
    Returns:
        Best hyperparameters and results
    """
    tuner = HyperparameterTuner(study_name=study_name, direction='maximize')
    
    results = tuner.optimize(
        objective_func=tuner.objective_rl_agent,
        n_trials=n_trials,
        algorithm=algorithm,
        train_data=train_data,
        eval_data=eval_data,
        initial_capital=initial_capital,
        training_timesteps=training_timesteps
    )
    
    if save_results:
        os.makedirs('models/tuning', exist_ok=True)
        tuner.save_results(f'models/tuning/{study_name}_results.json')
        tuner.plot_optimization_history(f'models/tuning/{study_name}_history.png')
        tuner.plot_param_importances(f'models/tuning/{study_name}_importances.png')
    
    return results


def tune_strategy_parameters(
    strategy_func: Callable,
    data: pd.DataFrame,
    param_ranges: Dict[str, tuple],
    study_name: str = 'strategy_tuning',
    n_trials: int = 100,
    metric: str = 'sharpe_ratio'
) -> Dict[str, Any]:
    """
    Tune strategy parameters using Optuna
    
    Args:
        strategy_func: Function that takes params and data, returns metrics
        data: Historical data
        param_ranges: Dict of parameter names to (min, max) tuples
        study_name: Name for the study
        n_trials: Number of trials
        metric: Metric to optimize ('sharpe_ratio', 'roi', etc.)
    
    Returns:
        Best parameters and results
    """
    def objective(trial):
        # Sample parameters
        params = {}
        for param_name, (min_val, max_val) in param_ranges.items():
            if isinstance(min_val, int) and isinstance(max_val, int):
                params[param_name] = trial.suggest_int(param_name, min_val, max_val)
            else:
                params[param_name] = trial.suggest_float(param_name, min_val, max_val)
        
        # Evaluate strategy
        try:
            metrics = strategy_func(params, data)
            return metrics.get(metric, -np.inf)
        except Exception as e:
            logger.error(f"Trial failed: {e}")
            return -np.inf
    
    tuner = HyperparameterTuner(study_name=study_name, direction='maximize')
    tuner.study.optimize(objective, n_trials=n_trials, show_progress_bar=True)
    
    return {
        'best_params': tuner.get_best_params(),
        'best_value': tuner.get_best_value(),
        'n_trials': n_trials
    }
