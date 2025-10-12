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


def calculate_current_drawdown(equity_curve: list) -> float:
    """
    Berechne aktuellen Drawdown (vom Peak bis zum letzten Wert)
    
    Args:
        equity_curve: Liste von Kapitalwerten
    
    Returns:
        Current drawdown in Prozent (negative Zahl)
    """
    import numpy as np
    
    if not equity_curve or len(equity_curve) < 1:
        return 0.0
    
    equity_array = np.array(equity_curve)
    
    # Finde das Maximum bis jetzt
    peak_value = np.max(equity_array)
    
    # Aktueller Wert
    current_value = equity_array[-1]
    
    # Berechne aktuellen Drawdown
    if peak_value == 0:
        return 0.0
    
    current_drawdown = ((current_value - peak_value) / peak_value) * 100
    
    return current_drawdown


def calculate_calmar_ratio(total_return: float, max_drawdown_percent: float) -> float:
    """
    Berechne Calmar Ratio (Return / Max Drawdown)
    
    Args:
        total_return: Gesamtrendite in Prozent
        max_drawdown_percent: Maximum Drawdown in Prozent (negative Zahl)
    
    Returns:
        Calmar Ratio
    """
    if max_drawdown_percent == 0 or max_drawdown_percent >= 0:
        return 0.0
    
    # Calmar Ratio = Annualized Return / Absolute Max Drawdown
    calmar = total_return / abs(max_drawdown_percent)
    
    return calmar


def calculate_volatility(equity_curve: list) -> float:
    """
    Berechne Volatilität (Standardabweichung der Renditen)
    
    Args:
        equity_curve: Liste von Kapitalwerten
    
    Returns:
        Volatilität (annualisiert)
    """
    import numpy as np
    
    if not equity_curve or len(equity_curve) < 2:
        return 0.0
    
    equity_array = np.array(equity_curve)
    
    # Berechne Renditen
    returns = np.diff(equity_array) / equity_array[:-1]
    
    # Berechne Standardabweichung
    volatility = np.std(returns)
    
    # Annualisiere (angenommen täglich, 252 Handelstage)
    volatility_annualized = volatility * np.sqrt(252)
    
    return volatility_annualized


def calculate_avg_trade_duration(trades: list) -> float:
    """
    Berechne durchschnittliche Trade-Dauer
    
    Args:
        trades: Liste von Trade-Dictionaries mit Zeitstempeln
    
    Returns:
        Durchschnittliche Dauer in Sekunden (0 wenn nicht berechenbar)
    """
    from datetime import datetime
    
    if not trades or len(trades) < 2:
        return 0.0
    
    durations = []
    entry_time = None
    
    for trade in trades:
        # Parse timestamp
        timestamp_str = trade.get('timestamp', '')
        if not timestamp_str:
            continue
            
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
        except:
            continue
        
        trade_type = trade.get('type', trade.get('order_type', ''))
        
        # BUY = Entry, SELL = Exit
        if trade_type in ['BUY', 'LONG']:
            entry_time = timestamp
        elif trade_type in ['SELL', 'SHORT'] and entry_time:
            duration = (timestamp - entry_time).total_seconds()
            durations.append(duration)
            entry_time = None
    
    if not durations:
        return 0.0
    
    return sum(durations) / len(durations)


def calculate_profit_factor(trades: list) -> float:
    """
    Berechne Profit Factor (Gross Profit / Gross Loss)
    
    Args:
        trades: Liste von Trade-Dictionaries mit PnL
    
    Returns:
        Profit Factor
    """
    if not trades:
        return 0.0
    
    pnls = [float(t.get('pnl', 0)) for t in trades if t.get('pnl', '0') != '0.00']
    
    if not pnls:
        return 0.0
    
    gross_profit = sum(p for p in pnls if p > 0)
    gross_loss = abs(sum(p for p in pnls if p < 0))
    
    if gross_loss == 0:
        return float('inf') if gross_profit > 0 else 0.0
    
    return gross_profit / gross_loss


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
            'max_drawdown_value': 0.0,
            'calmar_ratio': 0.0,
            'volatility': 0.0,
            'avg_trade_duration': 0.0,
            'profit_factor': 0.0
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
    
    # Berechne Calmar Ratio
    calmar_ratio = 0.0
    if equity_curve and len(equity_curve) >= 2:
        total_return = ((equity_curve[-1] - equity_curve[0]) / equity_curve[0]) * 100
        calmar_ratio = calculate_calmar_ratio(total_return, max_drawdown)
    
    # Berechne Volatilität
    volatility = 0.0
    if equity_curve and len(equity_curve) >= 2:
        volatility = calculate_volatility(equity_curve)
    
    # Berechne durchschnittliche Trade-Dauer
    avg_trade_duration = calculate_avg_trade_duration(trades)
    
    # Berechne Profit Factor
    profit_factor = calculate_profit_factor(trades)
    
    return {
        'total_trades': total_trades,
        'total_pnl': total_pnl,
        'win_rate': win_rate,
        'best_trade': best_trade,
        'worst_trade': worst_trade,
        'avg_pnl': avg_pnl,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'max_drawdown_value': max_drawdown_value,
        'calmar_ratio': calmar_ratio,
        'volatility': volatility,
        'avg_trade_duration': avg_trade_duration,
        'profit_factor': profit_factor
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
                'quantity', 'triggering_strategies', 'capital', 'pnl',
                'is_real_money', 'profit_factor', 'win_rate', 'sharpe_ratio'
            ])
            df.to_csv(self.filepath, index=False, encoding='utf-8')
            logging.info(f"✓ Trade-Log erstellt: {self.filepath}")
    
    def log_trade(self, order_type: str, price: float, quantity: float,
                  strategies: list, capital: float, pnl: float = 0.0,
                  symbol: str = "BTC/USDT", is_real_money: bool = False,
                  profit_factor: float = 0.0, win_rate: float = 0.0,
                  sharpe_ratio: float = 0.0):
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
            is_real_money: Flag ob Echtgeld-Trade (default: False für Sicherheit)
            profit_factor: Profit Factor Metrik
            win_rate: Win Rate Metrik (in Prozent)
            sharpe_ratio: Sharpe Ratio Metrik
        """
        trade = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'order_type': order_type,
            'price': f"{price:.2f}",
            'quantity': quantity,
            'triggering_strategies': ', '.join(strategies),
            'capital': f"{capital:.2f}",
            'pnl': f"{pnl:.2f}",
            'is_real_money': is_real_money,
            'profit_factor': f"{profit_factor:.2f}",
            'win_rate': f"{win_rate:.2f}",
            'sharpe_ratio': f"{sharpe_ratio:.2f}"
        }
        
        # Append to CSV
        df = pd.DataFrame([trade])
        df.to_csv(self.filepath, mode='a', header=False, index=False, encoding='utf-8')
        
        # Logging mit Echtgeld-Flag
        real_money_indicator = "💰 ECHTGELD" if is_real_money else "🧪 DRY-RUN"
        logging.info(f"✓ Trade protokolliert: {real_money_indicator} {order_type} @ ${price:.2f}")
    
    def get_all_trades(self) -> list:
        """Hole alle Trades"""
        return load_trades_from_csv(self.filepath)
    
    def clear_trades(self):
        """Lösche alle Trades"""
        self._initialize_file()
        logging.info("Trade-History gelöscht")


# ==============================================================================
# VISUALIZATION FUNCTIONS
# ==============================================================================

def generate_equity_curve_chart(equity_curve: list, output_file: str = None, 
                                use_plotly: bool = False, title: str = "Equity Curve"):
    """
    Generate equity curve visualization
    
    Args:
        equity_curve: List of dict with 'timestamp' and 'capital' keys, or list of capital values
        output_file: Path to save chart (optional)
        use_plotly: Use Plotly instead of Matplotlib
        title: Chart title
    
    Returns:
        Path to saved file if output_file provided, else None
    """
    import numpy as np
    
    # Handle different equity_curve formats
    if not equity_curve:
        logging.warning("Empty equity curve")
        return None
    
    if isinstance(equity_curve[0], dict):
        timestamps = [e.get('timestamp', i) for i, e in enumerate(equity_curve)]
        capitals = [e['capital'] for e in equity_curve]
    else:
        # Simple list of values
        timestamps = list(range(len(equity_curve)))
        capitals = equity_curve
    
    if use_plotly:
        try:
            import plotly.graph_objects as go
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=capitals,
                mode='lines',
                name='Equity',
                line=dict(color='#2E86AB', width=2)
            ))
            
            fig.update_layout(
                title=title,
                xaxis_title='Time',
                yaxis_title='Capital ($)',
                template='plotly_white',
                hovermode='x unified'
            )
            
            if output_file:
                fig.write_html(output_file)
                logging.info(f"✓ Equity curve saved to: {output_file}")
                return output_file
            else:
                fig.show()
                return None
                
        except ImportError:
            logging.warning("Plotly not available, falling back to Matplotlib")
            use_plotly = False
    
    if not use_plotly:
        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')  # Non-interactive backend
            
            plt.figure(figsize=(12, 6))
            plt.plot(timestamps, capitals, linewidth=2, color='#2E86AB')
            plt.title(title, fontsize=14, fontweight='bold')
            plt.xlabel('Time', fontsize=12)
            plt.ylabel('Capital ($)', fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            if output_file:
                plt.savefig(output_file, dpi=150, bbox_inches='tight')
                plt.close()
                logging.info(f"✓ Equity curve saved to: {output_file}")
                return output_file
            else:
                plt.show()
                plt.close()
                return None
                
        except ImportError:
            logging.error("Neither Plotly nor Matplotlib available")
            return None


def generate_drawdown_chart(equity_curve: list, output_file: str = None,
                            use_plotly: bool = False, title: str = "Drawdown"):
    """
    Generate drawdown visualization
    
    Args:
        equity_curve: List of dict with 'timestamp' and 'capital' keys, or list of capital values
        output_file: Path to save chart (optional)
        use_plotly: Use Plotly instead of Matplotlib
        title: Chart title
    
    Returns:
        Path to saved file if output_file provided, else None
    """
    import numpy as np
    
    # Handle different equity_curve formats
    if not equity_curve:
        logging.warning("Empty equity curve")
        return None
    
    if isinstance(equity_curve[0], dict):
        timestamps = [e.get('timestamp', i) for i, e in enumerate(equity_curve)]
        capitals = np.array([e['capital'] for e in equity_curve])
    else:
        timestamps = list(range(len(equity_curve)))
        capitals = np.array(equity_curve)
    
    # Calculate drawdown
    running_max = np.maximum.accumulate(capitals)
    drawdown = (capitals - running_max) / running_max * 100
    
    if use_plotly:
        try:
            import plotly.graph_objects as go
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=drawdown,
                mode='lines',
                name='Drawdown',
                fill='tozeroy',
                line=dict(color='#A23B72', width=2),
                fillcolor='rgba(162, 59, 114, 0.3)'
            ))
            
            fig.update_layout(
                title=title,
                xaxis_title='Time',
                yaxis_title='Drawdown (%)',
                template='plotly_white',
                hovermode='x unified'
            )
            
            if output_file:
                fig.write_html(output_file)
                logging.info(f"✓ Drawdown chart saved to: {output_file}")
                return output_file
            else:
                fig.show()
                return None
                
        except ImportError:
            logging.warning("Plotly not available, falling back to Matplotlib")
            use_plotly = False
    
    if not use_plotly:
        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')
            
            plt.figure(figsize=(12, 6))
            plt.fill_between(range(len(drawdown)), drawdown, 0, 
                           color='#A23B72', alpha=0.3)
            plt.plot(drawdown, linewidth=2, color='#A23B72')
            plt.title(title, fontsize=14, fontweight='bold')
            plt.xlabel('Time', fontsize=12)
            plt.ylabel('Drawdown (%)', fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            if output_file:
                plt.savefig(output_file, dpi=150, bbox_inches='tight')
                plt.close()
                logging.info(f"✓ Drawdown chart saved to: {output_file}")
                return output_file
            else:
                plt.show()
                plt.close()
                return None
                
        except ImportError:
            logging.error("Neither Plotly nor Matplotlib available")
            return None


def generate_pnl_distribution_chart(trades: list, output_file: str = None,
                                   use_plotly: bool = False, title: str = "P&L Distribution"):
    """
    Generate P&L distribution histogram
    
    Args:
        trades: List of trade dictionaries with 'pnl' key
        output_file: Path to save chart (optional)
        use_plotly: Use Plotly instead of Matplotlib
        title: Chart title
    
    Returns:
        Path to saved file if output_file provided, else None
    """
    import numpy as np
    
    # Extract PnL values
    pnls = []
    for trade in trades:
        if 'pnl' in trade and trade['pnl'] != 0:
            pnl_val = trade['pnl']
            # Handle string PnL values
            if isinstance(pnl_val, str):
                try:
                    pnl_val = float(pnl_val)
                except:
                    continue
            pnls.append(pnl_val)
    
    if not pnls:
        logging.warning("No P&L data to visualize")
        return None
    
    if use_plotly:
        try:
            import plotly.graph_objects as go
            
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=pnls,
                nbinsx=30,
                marker_color='#18A558',
                opacity=0.7,
                name='P&L'
            ))
            
            # Add vertical line at zero
            fig.add_vline(x=0, line_dash="dash", line_color="red", opacity=0.5)
            
            fig.update_layout(
                title=title,
                xaxis_title='P&L ($)',
                yaxis_title='Frequency',
                template='plotly_white',
                showlegend=False
            )
            
            if output_file:
                fig.write_html(output_file)
                logging.info(f"✓ P&L distribution saved to: {output_file}")
                return output_file
            else:
                fig.show()
                return None
                
        except ImportError:
            logging.warning("Plotly not available, falling back to Matplotlib")
            use_plotly = False
    
    if not use_plotly:
        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')
            
            plt.figure(figsize=(12, 6))
            
            # Separate wins and losses
            wins = [p for p in pnls if p > 0]
            losses = [p for p in pnls if p < 0]
            
            # Plot histogram
            if wins:
                plt.hist(wins, bins=20, color='#18A558', alpha=0.7, label='Wins')
            if losses:
                plt.hist(losses, bins=20, color='#D32F2F', alpha=0.7, label='Losses')
            
            plt.axvline(x=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
            plt.title(title, fontsize=14, fontweight='bold')
            plt.xlabel('P&L ($)', fontsize=12)
            plt.ylabel('Frequency', fontsize=12)
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            if output_file:
                plt.savefig(output_file, dpi=150, bbox_inches='tight')
                plt.close()
                logging.info(f"✓ P&L distribution saved to: {output_file}")
                return output_file
            else:
                plt.show()
                plt.close()
                return None
                
        except ImportError:
            logging.error("Neither Plotly nor Matplotlib available")
            return None
