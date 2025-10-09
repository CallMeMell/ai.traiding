"""
utils.py - Hilfsmodule für Logging, Datenvalidierung, etc.
==========================================================
Zentrale Utilities für den Trading-Bot
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional
import pandas as pd


def setup_logging(
    log_level: str = "INFO",
    log_file: str = "logs/trading_bot.log",
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Richte zentrales Logging ein
    
    Args:
        log_level: Log-Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Pfad zur Log-Datei
        max_bytes: Maximale Größe pro Log-Datei
        backup_count: Anzahl Backup-Dateien
    
    Returns:
        Konfigurierter Logger
    """
    # Erstelle logs Verzeichnis falls nicht vorhanden
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Root Logger konfigurieren
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Entferne existierende Handler
    logger.handlers = []
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File Handler mit Rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    logger.info("=" * 60)
    logger.info("Logging initialisiert")
    logger.info(f"Log-Datei: {log_file}")
    logger.info(f"Log-Level: {log_level}")
    logger.info("=" * 60)
    
    return logger


def validate_ohlcv_data(df: pd.DataFrame) -> tuple[bool, Optional[str]]:
    """
    Validiere OHLCV DataFrame
    
    Args:
        df: DataFrame mit Marktdaten
    
    Returns:
        (is_valid, error_message)
    """
    required_columns = ['open', 'high', 'low', 'close', 'volume']
    
    # Prüfe Spalten
    for col in required_columns:
        if col not in df.columns:
            return False, f"Fehlende Spalte: {col}"
    
    # Prüfe Datentypen
    for col in required_columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            return False, f"Spalte {col} ist nicht numerisch"
    
    # Prüfe auf NaN
    if df[required_columns].isnull().any().any():
        return False, "DataFrame enthält NaN-Werte"
    
    # Prüfe auf negative Werte
    if (df[required_columns] < 0).any().any():
        return False, "DataFrame enthält negative Werte"
    
    # Prüfe OHLC-Logik (High >= Low, etc.)
    if not (df['high'] >= df['low']).all():
        return False, "Ungültige OHLC-Daten: High < Low"
    
    if not (df['high'] >= df['close']).all():
        return False, "Ungültige OHLC-Daten: High < Close"
    
    if not (df['low'] <= df['close']).all():
        return False, "Ungültige OHLC-Daten: Low > Close"
    
    # Mindestanzahl Zeilen
    if len(df) < 2:
        return False, "Zu wenig Daten (min. 2 Zeilen)"
    
    return True, None


def format_currency(amount: float) -> str:
    """Formatiere Betrag als Währung"""
    return f"${amount:,.2f}"


def format_percentage(value: float) -> str:
    """Formatiere Wert als Prozent"""
    return f"{value:.2f}%"


def calculate_sharpe_ratio(returns: list, risk_free_rate: float = 0.0) -> float:
    """
    Berechne Sharpe Ratio
    
    Args:
        returns: Liste von Renditen (als Dezimalzahlen, z.B. 0.02 für 2%)
        risk_free_rate: Risikofreier Zinssatz (annualisiert)
    
    Returns:
        Sharpe Ratio
    """
    import numpy as np
    
    if not returns or len(returns) < 2:
        return 0.0
    
    returns_array = np.array(returns)
    excess_returns = returns_array - risk_free_rate
    
    if np.std(excess_returns) == 0:
        return 0.0
    
    sharpe = np.mean(excess_returns) / np.std(excess_returns)
    
    # Annualisiere (angenommen täglich, 252 Handelstage)
    # Für andere Zeiträume müsste man anpassen
    sharpe_annualized = sharpe * np.sqrt(252)
    
    return sharpe_annualized


def calculate_max_drawdown(equity_curve: list) -> tuple:
    """
    Berechne Maximum Drawdown
    
    Args:
        equity_curve: Liste von Kapitalwerten
    
    Returns:
        Tuple (max_drawdown_percent, max_drawdown_value, peak_value, trough_value)
    """
    import numpy as np
    
    if not equity_curve or len(equity_curve) < 2:
        return 0.0, 0.0, 0.0, 0.0
    
    equity_array = np.array(equity_curve)
    
    # Berechne running maximum
    running_max = np.maximum.accumulate(equity_array)
    
    # Berechne Drawdown
    drawdown = (equity_array - running_max) / running_max
    
    # Finde Maximum Drawdown
    max_dd_idx = np.argmin(drawdown)
    max_dd_percent = drawdown[max_dd_idx] * 100
    
    # Finde Peak und Trough
    peak_idx = np.argmax(running_max[:max_dd_idx + 1])
    peak_value = equity_array[peak_idx]
    trough_value = equity_array[max_dd_idx]
    max_dd_value = trough_value - peak_value
    
    return max_dd_percent, max_dd_value, peak_value, trough_value


def calculate_performance_metrics(trades: list, equity_curve: list = None, initial_capital: float = 10000.0) -> dict:
    """
    Berechne Performance-Metriken aus Trade-Liste
    
    Args:
        trades: Liste von Trade-Dictionaries
        equity_curve: Optional Liste von Kapitalwerten für erweiterte Metriken
        initial_capital: Startkapital für Berechnungen
    
    Returns:
        Dictionary mit Performance-Metriken
    """
    if not trades:
        return {
            'total_trades': 0,
            'total_pnl': 0.0,
            'win_rate': 0.0,
            'best_trade': 0.0,
            'worst_trade': 0.0,
            'avg_pnl': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'max_drawdown_value': 0.0
        }
    
    pnls = [float(t.get('pnl', 0)) for t in trades if t.get('pnl', '0') != '0.00']
    
    total_trades = len(trades)
    total_pnl = sum(pnls)
    wins = [p for p in pnls if p > 0]
    win_rate = (len(wins) / len(pnls) * 100) if pnls else 0
    best_trade = max(pnls) if pnls else 0
    worst_trade = min(pnls) if pnls else 0
    avg_pnl = total_pnl / len(pnls) if pnls else 0
    
    # Berechne Sharpe Ratio wenn möglich
    sharpe_ratio = 0.0
    if pnls and len(pnls) >= 2:
        # Konvertiere PnL zu Returns
        returns = [pnl / initial_capital for pnl in pnls]
        sharpe_ratio = calculate_sharpe_ratio(returns)
    
    # Berechne Maximum Drawdown wenn equity curve vorhanden
    max_drawdown = 0.0
    max_drawdown_value = 0.0
    if equity_curve and len(equity_curve) >= 2:
        max_dd_percent, max_dd_value, _, _ = calculate_max_drawdown(equity_curve)
        max_drawdown = max_dd_percent
        max_drawdown_value = max_dd_value
    
    return {
        'total_trades': total_trades,
        'total_pnl': total_pnl,
        'win_rate': win_rate,
        'best_trade': best_trade,
        'worst_trade': worst_trade,
        'avg_pnl': avg_pnl,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'max_drawdown_value': max_drawdown_value
    }


def generate_sample_data(n_bars: int = 1000, start_price: float = 30000) -> pd.DataFrame:
    """
    Generiere simulierte OHLCV-Daten für Testing
    
    Args:
        n_bars: Anzahl der Kerzen
        start_price: Start-Preis
    
    Returns:
        DataFrame mit simulierten OHLCV-Daten
    """
    import numpy as np
    
    dates = pd.date_range(end=datetime.now(), periods=n_bars, freq='15min')
    
    # Simuliere Preisverlauf mit Random Walk
    np.random.seed(42)
    price = start_price
    prices = [price]
    
    for _ in range(n_bars - 1):
        change = np.random.normal(0, 100)  # Volatilität
        price += change
        price = max(price, 1000)  # Verhindere negative Preise
        prices.append(price)
    
    prices = np.array(prices)
    
    # Erstelle OHLCV
    df = pd.DataFrame({
        'timestamp': dates,
        'open': prices + np.random.normal(0, 50, n_bars),
        'high': prices + abs(np.random.normal(50, 30, n_bars)),
        'low': prices - abs(np.random.normal(50, 30, n_bars)),
        'close': prices,
        'volume': np.random.uniform(100, 1000, n_bars)
    })
    
    return df


def save_trades_to_csv(trades: list, filepath: str = "data/trades.csv"):
    """
    Speichere Trades in CSV-Datei
    
    Args:
        trades: Liste von Trade-Dictionaries
        filepath: Pfad zur CSV-Datei
    """
    if not trades:
        return
    
    # Erstelle Verzeichnis falls nicht vorhanden
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    df = pd.DataFrame(trades)
    df.to_csv(filepath, index=False, encoding='utf-8')
    
    logging.info(f"✓ {len(trades)} Trades gespeichert in {filepath}")


def load_trades_from_csv(filepath: str = "data/trades.csv") -> list:
    """
    Lade Trades aus CSV-Datei
    
    Args:
        filepath: Pfad zur CSV-Datei
    
    Returns:
        Liste von Trade-Dictionaries
    """
    if not os.path.exists(filepath):
        return []
    
    try:
        df = pd.read_csv(filepath, encoding='utf-8')
        return df.to_dict('records')
    except Exception as e:
        logging.error(f"Fehler beim Laden der Trades: {e}")
        return []


class TradeLogger:
    """
    Utility-Klasse für Trade-Logging mit CSV-Unterstützung
    """
    
    def __init__(self, filepath: str = "data/trades.csv"):
        """
        Args:
            filepath: Pfad zur Trades-CSV-Datei
        """
        self.filepath = filepath
        self._initialize_file()
    
    def _initialize_file(self):
        """Initialisiere CSV-Datei mit Header"""
        if not os.path.exists(self.filepath):
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            
            df = pd.DataFrame(columns=[
                'timestamp', 'symbol', 'order_type', 'price',
                'quantity', 'triggering_strategies', 'capital', 'pnl'
            ])
            df.to_csv(self.filepath, index=False, encoding='utf-8')
            logging.info(f"✓ Trade-Log erstellt: {self.filepath}")
    
    def log_trade(self, order_type: str, price: float, quantity: float,
                  strategies: list, capital: float, pnl: float = 0.0,
                  symbol: str = "BTC/USDT"):
        """
        Protokolliere Trade
        
        Args:
            order_type: 'BUY' oder 'SELL'
            price: Ausführungspreis
            quantity: Menge
            strategies: Liste der triggering strategies
            capital: Aktuelles Kapital
            pnl: Profit/Loss
            symbol: Trading-Symbol
        """
        trade = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'order_type': order_type,
            'price': f"{price:.2f}",
            'quantity': quantity,
            'triggering_strategies': ', '.join(strategies),
            'capital': f"{capital:.2f}",
            'pnl': f"{pnl:.2f}"
        }
        
        # Append to CSV
        df = pd.DataFrame([trade])
        df.to_csv(self.filepath, mode='a', header=False, index=False, encoding='utf-8')
        
        logging.info(f"✓ Trade protokolliert: {order_type} @ ${price:.2f}")
    
    def get_all_trades(self) -> list:
        """Hole alle Trades"""
        return load_trades_from_csv(self.filepath)
    
    def clear_trades(self):
        """Lösche alle Trades"""
        self._initialize_file()
        logging.info("Trade-History gelöscht")
