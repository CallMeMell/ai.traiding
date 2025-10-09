"""
config.py - Zentrale Konfigurationsverwaltung
==============================================
Alle Parameter und API-Schlüssel an einem Ort.
Verwende Umgebungsvariablen für Sicherheit.
"""
import os
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import json

# Lade .env Dateien falls vorhanden
# Priorität: keys.env > .env
load_dotenv('keys.env')
load_dotenv()


@dataclass
class TradingConfig:
    """
    Zentrale Trading-Konfiguration
    
    Alle Parameter können über Umgebungsvariablen überschrieben werden.
    """
    
    # ========== API CREDENTIALS ==========
    ALPACA_API_KEY: str = os.getenv("ALPACA_API_KEY", "")
    ALPACA_SECRET_KEY: str = os.getenv("ALPACA_SECRET_KEY", "")
    ALPACA_BASE_URL: str = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # ========== TRADING PARAMETERS ==========
    trading_symbol: str = "BTC/USDT"
    timeframe: str = "15m"
    initial_capital: float = 10000.0
    trade_size: float = 100.0
    update_interval: int = 60  # Sekunden
    
    # ========== RISK MANAGEMENT ==========
    max_position_size: float = 1000.0
    max_positions: int = 10
    risk_per_trade: float = 0.02  # 2% pro Trade
    max_daily_loss: float = 0.05  # 5% maximaler Tagesverlust
    
    # Stop-Loss & Take-Profit
    enable_stop_loss: bool = True
    stop_loss_percent: float = 10.0
    enable_take_profit: bool = True
    take_profit_percent: float = 20.0
    enable_trailing_stop: bool = False
    trailing_stop_percent: float = 5.0
    
    # ========== STRATEGY CONFIGURATION ==========
    active_strategies: list = field(default_factory=lambda: ["rsi", "ema_crossover"])
    cooperation_logic: str = "OR"  # "AND" oder "OR"
    
    # Strategy Parameters
    strategies: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "ma_crossover": {
            "short_window": 50,
            "long_window": 200
        },
        "rsi": {
            "window": 14,
            "oversold_threshold": 35,
            "overbought_threshold": 65
        },
        "bollinger_bands": {
            "window": 20,
            "std_dev": 2.0
        },
        "ema_crossover": {
            "short_window": 9,
            "long_window": 21
        },
        "lsob": {
            "bb_window": 20,
            "bb_std": 2.0,
            "atr_window": 14,
            "volume_threshold": 1.2,
            "breakout_threshold": 0.005,
            "stop_loss_atr_mult": 2.0,
            "take_profit_atr_mult": 3.0,
            "max_volatility": 0.05
        }
    })
    
    # ========== TECHNICAL INDICATORS ==========
    enable_technical_analysis: bool = True
    use_moving_averages: bool = True
    use_rsi: bool = True
    rsi_period: int = 14
    rsi_overbought: float = 70.0
    rsi_oversold: float = 30.0
    
    # ========== LOGGING ==========
    log_level: str = "INFO"
    log_file: str = "logs/trading_bot.log"
    log_max_bytes: int = 10 * 1024 * 1024  # 10 MB
    log_backup_count: int = 5
    
    # ========== DATA STORAGE ==========
    trades_file: str = "data/trades.csv"
    data_directory: str = "data"
    use_database: bool = False
    database_path: str = "data/trading_bot.db"
    
    # ========== BACKTESTING ==========
    backtest_data_file: str = "data/historical_data.csv"
    backtest_initial_capital: float = 10000.0
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validiere Konfiguration
        
        Returns:
            (is_valid, error_message)
        """
        # API Keys sind optional für Backtest-Modus
        # if not self.ALPACA_API_KEY:
        #     return False, "ALPACA_API_KEY fehlt"
        
        if self.initial_capital <= 0:
            return False, "initial_capital muss positiv sein"
        
        if self.risk_per_trade <= 0 or self.risk_per_trade > 1:
            return False, "risk_per_trade muss zwischen 0 und 1 liegen"
        
        if self.cooperation_logic not in ["AND", "OR"]:
            return False, "cooperation_logic muss 'AND' oder 'OR' sein"
        
        if self.enable_stop_loss and (self.stop_loss_percent <= 0 or self.stop_loss_percent > 50):
            return False, "stop_loss_percent muss zwischen 0 und 50 liegen"
        
        return True, None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Konvertiere Config zu Dictionary
        
        Returns:
            Dictionary mit allen Konfigurationswerten
        """
        return {
            "trading_symbol": self.trading_symbol,
            "timeframe": self.timeframe,
            "active_strategies": self.active_strategies,
            "cooperation_logic": self.cooperation_logic,
            "strategies": self.strategies,
            "trade_size": self.trade_size,
            "initial_capital": self.initial_capital,
            "update_interval": self.update_interval,
        }
    
    def save_to_file(self, filepath: str = "config/trading_config.json"):
        """
        Speichere Konfiguration in JSON-Datei
        
        Args:
            filepath: Pfad zur Ziel-Datei
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_file(cls, filepath: str = "config/trading_config.json") -> 'TradingConfig':
        """
        Lade Konfiguration aus JSON-Datei
        
        Args:
            filepath: Pfad zur Config-Datei
        
        Returns:
            TradingConfig Instanz
        """
        if not os.path.exists(filepath):
            return cls()
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        return config


# Globale Config-Instanz
config = TradingConfig()

# Validiere Config beim Import
is_valid, error = config.validate()
if not is_valid:
    raise ValueError(f"Ungültige Konfiguration: {error}")
