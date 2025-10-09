"""
strategy.py - Trading Strategy Modul
====================================
Enthält alle Trading-Strategien und den Strategy Manager.
Konsolidiert die besten Features aus allen vier Versionen.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

# LSOB strategy will be loaded lazily to avoid circular import
LSOB_AVAILABLE = False
LSOBStrategy = None


# ========== BASE STRATEGY CLASS ==========

class BaseStrategy(ABC):
    """
    Abstrakte Basisklasse für Trading-Strategien
    
    Alle Strategien müssen diese Klasse erweitern und
    die generate_signal() Methode implementieren.
    """
    
    def __init__(self, name: str, params: Dict[str, Any]):
        """
        Args:
            name: Name der Strategie
            params: Parameter-Dictionary
        """
        self.name = name
        self.params = params
        self.enabled = True
        logger.info(f"✓ Strategie initialisiert: {name}")
    
    @abstractmethod
    def generate_signal(self, df: pd.DataFrame) -> int:
        """
        Generiere Trading-Signal basierend auf Daten
        
        Args:
            df: DataFrame mit OHLCV-Daten (open, high, low, close, volume)
        
        Returns:
            Signal: 1 = BUY, 0 = HOLD, -1 = SELL
        """
        pass
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """Validiere Input-Daten"""
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        
        for col in required_columns:
            if col not in df.columns:
                logger.error(f"Fehlende Spalte: {col}")
                return False
        
        if len(df) < 2:
            logger.warning(f"Zu wenig Daten für {self.name}")
            return False
        
        return True
    
    def update_params(self, new_params: Dict[str, Any]):
        """Update Parameter"""
        self.params.update(new_params)
        logger.info(f"Parameter aktualisiert für {self.name}")
    
    def get_info(self) -> Dict[str, Any]:
        """Hole Strategie-Info"""
        return {
            'name': self.name,
            'enabled': self.enabled,
            'params': self.params
        }


# ========== CONCRETE STRATEGIES ==========

class MACrossoverStrategy(BaseStrategy):
    """Moving Average Crossover - Trend-Following Strategie"""
    
    def __init__(self, params: Dict[str, Any]):
        super().__init__("MA_Crossover", params)
        self.short_window = params.get('short_window', 50)
        self.long_window = params.get('long_window', 200)
    
    def generate_signal(self, df: pd.DataFrame) -> int:
        """Generiere Signal basierend auf MA Crossover"""
        if not self.enabled or not self.validate_data(df):
            return 0
        
        if len(df) < self.long_window + 1:
            return 0
        
        # Berechne Moving Averages
        df_copy = df.copy()
        df_copy['SMA_short'] = df_copy['close'].rolling(window=self.short_window).mean()
        df_copy['SMA_long'] = df_copy['close'].rolling(window=self.long_window).mean()
        
        # Aktuelle und vorherige Werte
        short_curr = df_copy['SMA_short'].iloc[-1]
        short_prev = df_copy['SMA_short'].iloc[-2]
        long_curr = df_copy['SMA_long'].iloc[-1]
        long_prev = df_copy['SMA_long'].iloc[-2]
        
        if pd.isna(short_curr) or pd.isna(long_curr):
            return 0
        
        # Bullish Crossover: Short MA kreuzt über Long MA
        if short_curr > long_curr and short_prev <= long_prev:
            return 1  # BUY
        
        # Bearish Crossover: Short MA kreuzt unter Long MA
        if short_curr < long_curr and short_prev >= long_prev:
            return -1  # SELL
        
        return 0  # HOLD


class RSIStrategy(BaseStrategy):
    """RSI Mean Reversion - Überverkauft/Überkauft Strategie"""
    
    def __init__(self, params: Dict[str, Any]):
        super().__init__("RSI_MeanReversion", params)
        self.window = params.get('window', 14)
        self.oversold = params.get('oversold_threshold', 30)
        self.overbought = params.get('overbought_threshold', 70)
    
    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Berechne RSI (Relative Strength Index)"""
        delta = prices.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        
        avg_gain = gain.rolling(window=period, min_periods=period).mean()
        avg_loss = loss.rolling(window=period, min_periods=period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def generate_signal(self, df: pd.DataFrame) -> int:
        """Generiere Signal basierend auf RSI"""
        if not self.enabled or not self.validate_data(df):
            return 0
        
        if len(df) < self.window + 1:
            return 0
        
        df_copy = df.copy()
        df_copy['RSI'] = self.calculate_rsi(df_copy['close'], self.window)
        
        rsi_curr = df_copy['RSI'].iloc[-1]
        rsi_prev = df_copy['RSI'].iloc[-2]
        
        if pd.isna(rsi_curr) or pd.isna(rsi_prev):
            return 0
        
        # BUY: RSI steigt über oversold threshold (Erholung von überverkauft)
        if rsi_curr > self.oversold and rsi_prev <= self.oversold:
            return 1  # BUY
        
        # SELL: RSI fällt unter overbought threshold (Korrektur von überkauft)
        if rsi_curr < self.overbought and rsi_prev >= self.overbought:
            return -1  # SELL
        
        return 0  # HOLD


class BollingerBandsStrategy(BaseStrategy):
    """Bollinger Bands Breakout - Volatilitäts-Strategie"""
    
    def __init__(self, params: Dict[str, Any]):
        super().__init__("Bollinger_Bands", params)
        self.window = params.get('window', 20)
        self.std_dev = params.get('std_dev', 2.0)
    
    def generate_signal(self, df: pd.DataFrame) -> int:
        """Generiere Signal basierend auf Bollinger Bands"""
        if not self.enabled or not self.validate_data(df):
            return 0
        
        if len(df) < self.window + 1:
            return 0
        
        df_copy = df.copy()
        
        # Berechne Bollinger Bands
        df_copy['BB_middle'] = df_copy['close'].rolling(window=self.window).mean()
        df_copy['BB_std'] = df_copy['close'].rolling(window=self.window).std()
        df_copy['BB_upper'] = df_copy['BB_middle'] + (df_copy['BB_std'] * self.std_dev)
        df_copy['BB_lower'] = df_copy['BB_middle'] - (df_copy['BB_std'] * self.std_dev)
        
        price_curr = df_copy['close'].iloc[-1]
        price_prev = df_copy['close'].iloc[-2]
        upper_curr = df_copy['BB_upper'].iloc[-1]
        upper_prev = df_copy['BB_upper'].iloc[-2]
        lower_curr = df_copy['BB_lower'].iloc[-1]
        lower_prev = df_copy['BB_lower'].iloc[-2]
        
        if pd.isna(upper_curr) or pd.isna(lower_curr):
            return 0
        
        # BUY: Preis bricht ÜBER oberes Band (Breakout nach oben)
        if price_curr > upper_curr and price_prev <= upper_prev:
            return 1  # BUY
        
        # SELL: Preis bricht UNTER unteres Band (Breakout nach unten)
        if price_curr < lower_curr and price_prev >= lower_prev:
            return -1  # SELL
        
        return 0  # HOLD


class EMACrossoverStrategy(BaseStrategy):
    """EMA Crossover - Schnelle Trend-Strategie für Daytrading"""
    
    def __init__(self, params: Dict[str, Any]):
        super().__init__("EMA_Crossover", params)
        self.short_window = params.get('short_window', 9)
        self.long_window = params.get('long_window', 21)
    
    def generate_signal(self, df: pd.DataFrame) -> int:
        """Generiere Signal basierend auf EMA Crossover"""
        if not self.enabled or not self.validate_data(df):
            return 0
        
        if len(df) < self.long_window + 1:
            return 0
        
        df_copy = df.copy()
        
        # Berechne EMAs
        df_copy['EMA_short'] = df_copy['close'].ewm(span=self.short_window, adjust=False).mean()
        df_copy['EMA_long'] = df_copy['close'].ewm(span=self.long_window, adjust=False).mean()
        
        short_curr = df_copy['EMA_short'].iloc[-1]
        short_prev = df_copy['EMA_short'].iloc[-2]
        long_curr = df_copy['EMA_long'].iloc[-1]
        long_prev = df_copy['EMA_long'].iloc[-2]
        
        if pd.isna(short_curr) or pd.isna(long_curr):
            return 0
        
        # Bullish Crossover
        if short_curr > long_curr and short_prev <= long_prev:
            return 1  # BUY
        
        # Bearish Crossover
        if short_curr < long_curr and short_prev >= long_prev:
            return -1  # SELL
        
        return 0  # HOLD


# ========== STRATEGY MANAGER ==========

class StrategyManager:
    """
    Verwaltet und koordiniert mehrere Trading-Strategien
    
    Features:
    - Parallele Ausführung mehrerer Strategien
    - Signal-Aggregation (AND/OR Logik)
    - Dynamisches Aktivieren/Deaktivieren
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: Konfiguration mit active_strategies, cooperation_logic, strategies
        """
        # Initialize strategy map with base strategies
        self.STRATEGY_MAP = {
            'ma_crossover': MACrossoverStrategy,
            'rsi': RSIStrategy,
            'bollinger_bands': BollingerBandsStrategy,
            'ema_crossover': EMACrossoverStrategy
        }
        
        # Try to add LSOB strategy (lazy import to avoid circular dependency)
        try:
            from lsob_strategy import LSOBStrategy
            self.STRATEGY_MAP['lsob'] = LSOBStrategy
            logger.debug("✓ LSOB strategy loaded")
        except ImportError as e:
            logger.debug(f"LSOB strategy not available: {e}")
        
        self.config = config
        self.strategies = {}
        self.cooperation_logic = config.get('cooperation_logic', 'OR')
        self._initialize_strategies()
    
    def _initialize_strategies(self):
        """Initialisiere alle aktiven Strategien"""
        active_strategies = self.config.get('active_strategies', [])
        strategy_params = self.config.get('strategies', {})
        
        for strategy_name in active_strategies:
            if strategy_name in self.STRATEGY_MAP:
                params = strategy_params.get(strategy_name, {})
                strategy_class = self.STRATEGY_MAP[strategy_name]
                strategy = strategy_class(params)
                self.strategies[strategy_name] = strategy
                logger.info(f"✓ Strategie geladen: {strategy_name}")
            else:
                logger.warning(f"Unbekannte Strategie: {strategy_name}")
    
    def get_aggregated_signal(self, df: pd.DataFrame) -> tuple[int, List[str]]:
        """
        Hole aggregiertes Signal von allen aktiven Strategien
        
        Args:
            df: OHLCV DataFrame
        
        Returns:
            (signal, triggering_strategies)
            signal: 1=BUY, 0=HOLD, -1=SELL
            triggering_strategies: Liste der Strategien die Signal gaben
        """
        if not self.strategies:
            return 0, []
        
        signals = {}
        for name, strategy in self.strategies.items():
            if strategy.enabled:
                signal = strategy.generate_signal(df)
                signals[name] = signal
        
        if not signals:
            return 0, []
        
        if self.cooperation_logic == 'AND':
            return self._aggregate_and(signals)
        else:
            return self._aggregate_or(signals)
    
    def _aggregate_and(self, signals: Dict[str, int]) -> tuple[int, List[str]]:
        """AND-Logik: Alle Strategien müssen zustimmen"""
        buy_strategies = [name for name, sig in signals.items() if sig == 1]
        sell_strategies = [name for name, sig in signals.items() if sig == -1]
        
        # BUY nur wenn ALLE BUY sagen
        if len(buy_strategies) == len(signals):
            return 1, buy_strategies
        
        # SELL nur wenn ALLE SELL sagen
        if len(sell_strategies) == len(signals):
            return -1, sell_strategies
        
        return 0, []
    
    def _aggregate_or(self, signals: Dict[str, int]) -> tuple[int, List[str]]:
        """OR-Logik: Mindestens eine Strategie muss Signal geben"""
        buy_strategies = [name for name, sig in signals.items() if sig == 1]
        sell_strategies = [name for name, sig in signals.items() if sig == -1]
        
        if buy_strategies:
            return 1, buy_strategies
        
        if sell_strategies:
            return -1, sell_strategies
        
        return 0, []
    
    def get_strategy(self, name: str) -> Optional[BaseStrategy]:
        """Hole spezifische Strategie"""
        return self.strategies.get(name)
    
    def enable_strategy(self, name: str):
        """Aktiviere Strategie"""
        if name in self.strategies:
            self.strategies[name].enabled = True
            logger.info(f"Strategie aktiviert: {name}")
    
    def disable_strategy(self, name: str):
        """Deaktiviere Strategie"""
        if name in self.strategies:
            self.strategies[name].enabled = False
            logger.info(f"Strategie deaktiviert: {name}")
    
    def update_strategy_params(self, name: str, params: Dict[str, Any]):
        """Update Parameter einer Strategie"""
        if name in self.strategies:
            self.strategies[name].update_params(params)
    
    def set_cooperation_logic(self, logic: str):
        """Setze Cooperation Logic (AND/OR)"""
        if logic in ['AND', 'OR']:
            self.cooperation_logic = logic
            logger.info(f"Cooperation Logic: {logic}")
        else:
            logger.warning(f"Ungültige Logic: {logic}")
    
    def get_all_strategies_info(self) -> Dict[str, Any]:
        """Hole Info über alle Strategien"""
        return {
            name: strategy.get_info()
            for name, strategy in self.strategies.items()
        }


# ========== TRADING ENGINE ==========

class TradingStrategy:
    """
    Haupt-Trading-Strategie-Klasse
    
    Diese Klasse kombiniert alle Strategien und verwaltet
    die Trading-Logik.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: Trading-Konfiguration
        """
        self.config = config
        self.strategy_manager = StrategyManager(config)
        logger.info("✓ TradingStrategy initialisiert")
    
    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analysiere Marktdaten und generiere Trading-Signal
        
        Args:
            df: DataFrame mit OHLCV-Daten
        
        Returns:
            Dictionary mit Signal und Details
        """
        signal, strategies = self.strategy_manager.get_aggregated_signal(df)
        
        current_price = df['close'].iloc[-1] if len(df) > 0 else 0
        
        return {
            'signal': signal,
            'signal_text': self._signal_to_text(signal),
            'triggering_strategies': strategies,
            'current_price': current_price,
            'timestamp': df['timestamp'].iloc[-1] if 'timestamp' in df.columns else None
        }
    
    @staticmethod
    def _signal_to_text(signal: int) -> str:
        """Konvertiere Signal zu Text"""
        if signal == 1:
            return "BUY"
        elif signal == -1:
            return "SELL"
        else:
            return "HOLD"
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update Konfiguration"""
        self.config.update(new_config)
        self.strategy_manager = StrategyManager(self.config)
        logger.info("Konfiguration aktualisiert")
