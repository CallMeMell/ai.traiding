"""
rl_environment.py - Reinforcement Learning Trading Environment
==============================================================
OpenAI Gym-compatible trading environment for training RL agents.

This module provides a custom Gym environment for trading strategies,
compatible with Stable-Baselines3 and other RL frameworks.
"""

import gym
from gym import spaces
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple, List
import logging

logger = logging.getLogger(__name__)


class TradingEnvironment(gym.Env):
    """
    Custom Trading Environment for Reinforcement Learning
    
    State Space:
        - Recent prices (normalized)
        - Technical indicators (RSI, MA, etc.)
        - Current position (0=no position, 1=long)
        - Available capital (normalized)
        - Current holdings (normalized)
    
    Action Space:
        Discrete(21): [BUY_10%, BUY_20%, ..., BUY_100%, HOLD, SELL_10%, ..., SELL_100%]
    
    Reward:
        Portfolio value change + Sharpe bonus - Drawdown penalty
    """
    
    metadata = {'render.modes': ['human']}
    
    def __init__(
        self,
        data: pd.DataFrame,
        initial_capital: float = 10000.0,
        commission_rate: float = 0.001,
        window_size: int = 30,
        features: Optional[List[str]] = None
    ):
        """
        Initialize the trading environment
        
        Args:
            data: DataFrame with OHLCV data and indicators
            initial_capital: Starting capital in USD
            commission_rate: Trading commission rate (0.001 = 0.1%)
            window_size: Number of candles to include in state
            features: List of feature columns to include in state
        """
        super(TradingEnvironment, self).__init__()
        
        self.data = data.reset_index(drop=True)
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.window_size = window_size
        
        # Default features if not specified
        if features is None:
            self.features = ['close', 'volume', 'rsi', 'ma_short', 'ma_long']
        else:
            self.features = features
        
        # Validate features exist
        missing = [f for f in self.features if f not in self.data.columns]
        if missing:
            raise ValueError(f"Missing features in data: {missing}")
        
        # Action space: 21 discrete actions
        # 0-9: BUY 10%, 20%, ..., 100%
        # 10: HOLD
        # 11-20: SELL 10%, 20%, ..., 100%
        self.action_space = spaces.Discrete(21)
        
        # Observation space: flattened window of features + portfolio state
        n_features = len(self.features)
        obs_shape = (window_size * n_features + 3,)  # +3 for position, capital, holdings
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=obs_shape,
            dtype=np.float32
        )
        
        # Episode tracking
        self.current_step = 0
        self.max_steps = len(self.data) - window_size - 1
        
        # Portfolio state
        self.capital = initial_capital
        self.holdings = 0.0  # Amount of asset held
        self.position = 0  # 0=no position, 1=long
        self.total_trades = 0
        
        # Performance tracking
        self.portfolio_values = []
        self.trades_history = []
        self.max_portfolio_value = initial_capital
        
        logger.info(f"TradingEnvironment initialized: {self.max_steps} steps, {n_features} features")
    
    def reset(self) -> np.ndarray:
        """Reset the environment to initial state"""
        self.current_step = 0
        self.capital = self.initial_capital
        self.holdings = 0.0
        self.position = 0
        self.total_trades = 0
        self.portfolio_values = [self.initial_capital]
        self.trades_history = []
        self.max_portfolio_value = self.initial_capital
        
        return self._get_observation()
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict]:
        """
        Execute one step in the environment
        
        Args:
            action: Action to take (0-20)
        
        Returns:
            observation: Current state
            reward: Reward for this step
            done: Whether episode is finished
            info: Additional information
        """
        # Get current price
        current_price = self._get_current_price()
        
        # Execute action
        action_type, action_amount = self._decode_action(action)
        trade_info = self._execute_action(action_type, action_amount, current_price)
        
        # Move to next step
        self.current_step += 1
        
        # Calculate portfolio value
        portfolio_value = self._calculate_portfolio_value()
        self.portfolio_values.append(portfolio_value)
        
        # Update max portfolio value
        if portfolio_value > self.max_portfolio_value:
            self.max_portfolio_value = portfolio_value
        
        # Calculate reward
        reward = self._calculate_reward()
        
        # Check if episode is done
        done = self.current_step >= self.max_steps
        
        # Prepare info
        info = {
            'portfolio_value': portfolio_value,
            'capital': self.capital,
            'holdings': self.holdings,
            'position': self.position,
            'total_trades': self.total_trades,
            'trade_info': trade_info
        }
        
        return self._get_observation(), reward, done, info
    
    def _get_observation(self) -> np.ndarray:
        """Get current observation (state)"""
        # Get window of historical data
        start_idx = self.current_step
        end_idx = self.current_step + self.window_size
        
        if end_idx > len(self.data):
            # Pad with last observation if needed
            window_data = self.data.iloc[-self.window_size:]
        else:
            window_data = self.data.iloc[start_idx:end_idx]
        
        # Extract features and normalize
        feature_data = window_data[self.features].values
        normalized_features = self._normalize_features(feature_data)
        
        # Flatten features
        flattened_features = normalized_features.flatten()
        
        # Add portfolio state
        current_price = self._get_current_price()
        portfolio_value = self._calculate_portfolio_value()
        
        portfolio_state = np.array([
            self.position,  # 0 or 1
            self.capital / self.initial_capital,  # Normalized capital
            (self.holdings * current_price) / self.initial_capital  # Normalized holdings value
        ], dtype=np.float32)
        
        # Combine
        observation = np.concatenate([flattened_features, portfolio_state])
        
        return observation.astype(np.float32)
    
    def _normalize_features(self, features: np.ndarray) -> np.ndarray:
        """Normalize features to prevent large values"""
        # Simple min-max normalization per feature
        normalized = np.zeros_like(features, dtype=np.float32)
        for i in range(features.shape[1]):
            col = features[:, i]
            min_val = col.min()
            max_val = col.max()
            if max_val > min_val:
                normalized[:, i] = (col - min_val) / (max_val - min_val)
            else:
                normalized[:, i] = 0.5
        return normalized
    
    def _decode_action(self, action: int) -> Tuple[str, float]:
        """
        Decode action integer to action type and amount
        
        Returns:
            action_type: 'BUY', 'SELL', or 'HOLD'
            action_amount: Percentage (0.1 to 1.0)
        """
        if action < 10:
            # BUY actions (0-9)
            return 'BUY', (action + 1) * 0.1
        elif action == 10:
            # HOLD action
            return 'HOLD', 0.0
        else:
            # SELL actions (11-20)
            return 'SELL', (action - 10) * 0.1
    
    def _execute_action(self, action_type: str, amount: float, price: float) -> Dict:
        """Execute trading action"""
        trade_info = {
            'action': action_type,
            'amount': amount,
            'price': price,
            'executed': False
        }
        
        if action_type == 'BUY' and self.position == 0:
            # Calculate how much to buy
            buy_amount = self.capital * amount
            commission = buy_amount * self.commission_rate
            shares = (buy_amount - commission) / price
            
            if shares > 0:
                self.holdings += shares
                self.capital -= buy_amount
                self.position = 1
                self.total_trades += 1
                trade_info['executed'] = True
                trade_info['shares'] = shares
                trade_info['commission'] = commission
                
                self.trades_history.append({
                    'step': self.current_step,
                    'action': 'BUY',
                    'price': price,
                    'shares': shares,
                    'capital': self.capital
                })
        
        elif action_type == 'SELL' and self.position == 1:
            # Sell portion of holdings
            shares_to_sell = self.holdings * amount
            sell_value = shares_to_sell * price
            commission = sell_value * self.commission_rate
            
            self.holdings -= shares_to_sell
            self.capital += sell_value - commission
            self.total_trades += 1
            trade_info['executed'] = True
            trade_info['shares'] = shares_to_sell
            trade_info['commission'] = commission
            
            # Update position
            if self.holdings < 0.0001:  # Close to zero
                self.holdings = 0.0
                self.position = 0
            
            self.trades_history.append({
                'step': self.current_step,
                'action': 'SELL',
                'price': price,
                'shares': shares_to_sell,
                'capital': self.capital
            })
        
        return trade_info
    
    def _get_current_price(self) -> float:
        """Get current market price"""
        idx = min(self.current_step + self.window_size, len(self.data) - 1)
        return self.data.iloc[idx]['close']
    
    def _calculate_portfolio_value(self) -> float:
        """Calculate current portfolio value"""
        current_price = self._get_current_price()
        return self.capital + (self.holdings * current_price)
    
    def _calculate_reward(self) -> float:
        """
        Calculate reward for current step
        
        Reward = Portfolio Return + Sharpe Bonus - Drawdown Penalty
        """
        if len(self.portfolio_values) < 2:
            return 0.0
        
        # Portfolio return
        current_value = self.portfolio_values[-1]
        previous_value = self.portfolio_values[-2]
        portfolio_return = (current_value - previous_value) / previous_value
        
        # Sharpe bonus (simplified - based on recent returns)
        if len(self.portfolio_values) >= 10:
            recent_returns = np.diff(self.portfolio_values[-10:]) / self.portfolio_values[-10:-1]
            sharpe = np.mean(recent_returns) / (np.std(recent_returns) + 1e-8)
            sharpe_bonus = sharpe * 0.1
        else:
            sharpe_bonus = 0.0
        
        # Drawdown penalty
        drawdown = (self.max_portfolio_value - current_value) / self.max_portfolio_value
        drawdown_penalty = -drawdown * 0.5
        
        # Combined reward
        reward = portfolio_return + sharpe_bonus + drawdown_penalty
        
        return reward
    
    def render(self, mode='human'):
        """Render the environment (optional)"""
        if mode == 'human':
            portfolio_value = self._calculate_portfolio_value()
            roi = (portfolio_value - self.initial_capital) / self.initial_capital * 100
            
            print(f"Step: {self.current_step}/{self.max_steps}")
            print(f"Portfolio Value: ${portfolio_value:.2f} (ROI: {roi:.2f}%)")
            print(f"Capital: ${self.capital:.2f}")
            print(f"Holdings: {self.holdings:.4f}")
            print(f"Position: {self.position}")
            print(f"Total Trades: {self.total_trades}")
            print("-" * 50)
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get performance metrics for the episode"""
        if len(self.portfolio_values) < 2:
            return {}
        
        portfolio_values = np.array(self.portfolio_values)
        returns = np.diff(portfolio_values) / portfolio_values[:-1]
        
        final_value = portfolio_values[-1]
        roi = (final_value - self.initial_capital) / self.initial_capital * 100
        
        # Sharpe ratio (annualized, assuming daily data)
        if len(returns) > 1 and np.std(returns) > 0:
            sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252)
        else:
            sharpe = 0.0
        
        # Max drawdown
        peak = np.maximum.accumulate(portfolio_values)
        drawdown = (peak - portfolio_values) / peak
        max_drawdown = np.max(drawdown) * 100
        
        return {
            'final_value': final_value,
            'roi': roi,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'total_trades': self.total_trades,
            'total_steps': self.current_step
        }
