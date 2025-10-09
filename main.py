"""
main.py - Haupt-Anwendung für Live-Trading
==========================================
Startet den Trading-Bot im Live-Modus mit Alpaca API Integration
"""
import sys
import time
import signal
from typing import Optional
import pandas as pd
import numpy as np
from datetime import datetime

# Imports
from config import config
from strategy import TradingStrategy
from utils import setup_logging, TradeLogger, generate_sample_data, validate_ohlcv_data

# Try to import Binance integration (Primary)
try:
    from binance_integration import BinanceDataProvider, PaperTradingExecutor
    BINANCE_AVAILABLE = True
except ImportError:
    BINANCE_AVAILABLE = False

# Try to import Alpaca integration (Legacy support)
try:
    from alpaca_integration import AlpacaDataProvider, AlpacaOrderExecutor
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False

# Globale Variablen
logger = None
is_running = False


class LiveTradingBot:
    """
    Live Trading Bot with Binance API Integration
    
    Supports both live trading with Binance API and simulated trading.
    Mode is determined by API key availability.
    """
    
    def __init__(self, use_live_data: bool = True, paper_trading: bool = True):
        """
        Initialize Trading Bot
        
        Args:
            use_live_data: True to use Binance API, False for simulation
            paper_trading: True for paper trading (testnet), False for live trading
        """
        global logger
        logger = setup_logging(
            log_level=config.log_level,
            log_file=config.log_file,
            max_bytes=config.log_max_bytes,
            backup_count=config.log_backup_count
        )
        
        logger.info("=" * 70)
        logger.info("🚀 LIVE TRADING BOT GESTARTET")
        logger.info("=" * 70)
        
        # Initialize Binance integration if available and requested
        self.use_live_data = use_live_data and BINANCE_AVAILABLE
        self.paper_trading = paper_trading
        self.binance_data_provider = None
        self.binance_order_executor = None
        self.api_type = 'simulation'
        
        if self.use_live_data:
            try:
                # Check if API keys are available
                if paper_trading:
                    # Use testnet keys for paper trading
                    api_key = config.BINANCE_TESTNET_API_KEY or config.BINANCE_API_KEY
                    api_secret = config.BINANCE_TESTNET_SECRET_KEY or config.BINANCE_SECRET_KEY
                else:
                    # Use production keys for live trading
                    api_key = config.BINANCE_API_KEY
                    api_secret = config.BINANCE_SECRET_KEY
                
                if api_key and api_secret:
                    self.binance_data_provider = BinanceDataProvider(
                        api_key=api_key,
                        api_secret=api_secret,
                        testnet=paper_trading
                    )
                    
                    # Test connection
                    if self.binance_data_provider.test_connection():
                        logger.info(f"✓ Binance Data Provider initialized ({'Testnet' if paper_trading else 'Live'})")
                        
                        # Initialize order executor for paper trading
                        if paper_trading:
                            self.binance_order_executor = PaperTradingExecutor(
                                initial_capital=config.initial_capital
                            )
                            logger.info("✓ Binance Paper Trading Executor initialized")
                        else:
                            # For live trading, we'll use the data provider's order methods
                            logger.warning("⚠️ Live trading mode - using real orders!")
                        
                        self.api_type = 'binance'
                    else:
                        logger.warning("⚠️ Binance connection failed, falling back to simulation")
                        self.use_live_data = False
                        self.binance_data_provider = None
                else:
                    logger.warning("⚠️ Binance API keys not found, using simulation mode")
                    self.use_live_data = False
            except Exception as e:
                logger.error(f"❌ Error initializing Binance: {e}")
                logger.info("Falling back to simulation mode")
                self.use_live_data = False
                self.binance_data_provider = None
                self.binance_order_executor = None
        
        if not self.use_live_data:
            logger.info("📊 Running in SIMULATION mode")
        
        # Initialize Components
        self.strategy = TradingStrategy(config.to_dict())
        self.trade_logger = TradeLogger(config.trades_file)
        
        # Trading State
        self.current_position = 0  # 0=keine Position, 1=long, -1=short
        self.entry_price = 0.0
        self.capital = config.initial_capital
        self.initial_capital = self.capital
        
        # Data (Simulation mode)
        self.data: Optional[pd.DataFrame] = None
        self.current_index = 0
        
        logger.info(f"Initial Capital: ${self.capital:,.2f}")
        logger.info(f"Trading Symbol: {config.trading_symbol}")
        logger.info(f"Update Interval: {config.update_interval}s")
        logger.info(f"Active Strategies: {config.active_strategies}")
        logger.info(f"Cooperation Logic: {config.cooperation_logic}")
        logger.info(f"Mode: {'LIVE (Binance)' if self.use_live_data else 'SIMULATION'}")
        logger.info(f"Trading Type: {'PAPER (Testnet)' if paper_trading else 'LIVE'}")
        logger.info("=" * 70)
    
    def initialize_data(self):
        """Initialize market data (from Binance or simulated)"""
        if self.use_live_data and self.binance_data_provider:
            try:
                logger.info(f"Loading historical data from Binance for {config.trading_symbol}...")
                
                # Convert trading symbol format if needed (BTC/USDT -> BTCUSDT)
                symbol = config.trading_symbol.replace('/', '')
                
                # Get historical data from Binance
                self.data = self.binance_data_provider.get_historical_klines(
                    symbol=symbol,
                    interval='15m',
                    limit=500
                )
                
                if self.data is not None and len(self.data) > 0:
                    self.current_index = len(self.data) - 1
                    logger.info(f"✓ {len(self.data)} bars loaded from Binance")
                else:
                    logger.warning("No data from Binance, falling back to simulation")
                    self.use_live_data = False
                    self.data = generate_sample_data(n_bars=500, start_price=30000)
                    self.current_index = len(self.data) - 1
                    
            except Exception as e:
                logger.error(f"Error loading Binance data: {e}")
                logger.info("Falling back to simulation mode")
                self.use_live_data = False
                self.data = generate_sample_data(n_bars=500, start_price=30000)
                self.current_index = len(self.data) - 1
        else:
            logger.info("Generating simulated market data...")
            self.data = generate_sample_data(n_bars=500, start_price=30000)
            self.current_index = len(self.data) - 1
            logger.info(f"✓ {len(self.data)} candles generated")
    
    def add_new_candle(self):
        """Add new candle (from Binance or simulated)"""
        if self.data is None:
            return
        
        if self.use_live_data and self.binance_data_provider:
            try:
                # Get latest data from Binance
                symbol = config.trading_symbol.replace('/', '')
                current_price = self.binance_data_provider.get_current_price(symbol)
                
                if current_price > 0:
                    # Create new candle with current price
                    last_close = self.data['close'].iloc[-1]
                    new_candle = pd.DataFrame({
                        'open': [last_close],
                        'high': [max(current_price, last_close)],
                        'low': [min(current_price, last_close)],
                        'close': [current_price],
                        'volume': [self.data['volume'].iloc[-1]]  # Use last volume as estimate
                    })
                    
                    self.data = pd.concat([self.data, new_candle], ignore_index=True)
                    self.current_index = len(self.data) - 1
                    return
            except Exception as e:
                logger.warning(f"Error getting live data: {e}, using simulation")
        
        # Simulation mode: Generate new candle with Random Walk
        last_close = self.data['close'].iloc[-1]
        
        new_price = last_close + np.random.normal(0, 100)
        new_price = max(new_price, 1000)  # Prevent negative prices
        
        new_candle = pd.DataFrame({
            'open': [last_close],
            'high': [new_price + abs(np.random.normal(0, 50))],
            'low': [new_price - abs(np.random.normal(0, 50))],
            'close': [new_price],
            'volume': [np.random.uniform(100, 1000)]
        })
        
        self.data = pd.concat([self.data, new_candle], ignore_index=True)
        self.current_index = len(self.data) - 1
    
    def process_signal(self, analysis: dict):
        """
        Verarbeite Trading-Signal
        
        Args:
            analysis: Signal-Dictionary von Strategy
        """
        signal = analysis['signal']
        current_price = analysis['current_price']
        strategies = analysis['triggering_strategies']
        
        # BUY Signal und keine Position
        if signal == 1 and self.current_position == 0:
            self.current_position = 1
            self.entry_price = current_price
            
            self.trade_logger.log_trade(
                order_type='BUY',
                price=current_price,
                quantity=config.trade_size,
                strategies=strategies,
                capital=self.capital,
                symbol=config.trading_symbol
            )
            
            logger.info(f"📈 BUY @ ${current_price:.2f} | Strategien: {strategies}")
        
        # SELL Signal und Long Position
        elif signal == -1 and self.current_position == 1:
            pnl = (current_price - self.entry_price) * config.trade_size
            self.capital += pnl
            self.current_position = 0
            
            self.trade_logger.log_trade(
                order_type='SELL',
                price=current_price,
                quantity=config.trade_size,
                strategies=strategies,
                capital=self.capital,
                pnl=pnl,
                symbol=config.trading_symbol
            )
            
            pnl_emoji = "💰" if pnl > 0 else "📉"
            logger.info(
                f"{pnl_emoji} SELL @ ${current_price:.2f} | "
                f"P&L: ${pnl:.2f} | "
                f"Capital: ${self.capital:.2f} | "
                f"Strategien: {strategies}"
            )
    
    def run(self):
        """Haupt-Trading-Loop"""
        global is_running
        is_running = True
        
        # Initialisiere Daten
        self.initialize_data()
        
        logger.info("🔄 Trading-Loop aktiv")
        logger.info("Drücke Ctrl+C zum Beenden\n")
        
        try:
            while is_running:
                # Füge neue Kerze hinzu (simuliert neue Marktdaten)
                self.add_new_candle()
                
                # Hole aktuelle Daten
                df_current = self.data.iloc[:self.current_index + 1].copy()
                
                # Validiere Daten
                is_valid, error = validate_ohlcv_data(df_current)
                if not is_valid:
                    logger.error(f"Ungültige Daten: {error}")
                    time.sleep(config.update_interval)
                    continue
                
                # Analysiere Markt
                analysis = self.strategy.analyze(df_current)
                
                # Verarbeite Signal
                self.process_signal(analysis)
                
                # Status-Update
                current_price = df_current['close'].iloc[-1]
                position_text = "None"
                if self.current_position == 1:
                    position_text = f"Long @ ${self.entry_price:.2f}"
                
                logger.info(
                    f"💹 Preis: ${current_price:.2f} | "
                    f"Position: {position_text} | "
                    f"Capital: ${self.capital:.2f}"
                )
                
                # Warte bis zum nächsten Update
                time.sleep(config.update_interval)
                
        except KeyboardInterrupt:
            logger.info("\n⏹️ Benutzer-Abbruch erkannt")
            self.shutdown()
        except Exception as e:
            logger.error(f"❌ Kritischer Fehler: {e}", exc_info=True)
            self.shutdown()
    
    def shutdown(self):
        """Sauberes Herunterfahren"""
        global is_running
        is_running = False
        
        logger.info("=" * 70)
        logger.info("📊 FINAL REPORT")
        logger.info("=" * 70)
        
        # Berechne Performance
        total_pnl = self.capital - self.initial_capital
        roi = (total_pnl / self.initial_capital) * 100
        
        trades = self.trade_logger.get_all_trades()
        
        logger.info(f"Initial Capital:  ${self.initial_capital:,.2f}")
        logger.info(f"Final Capital:    ${self.capital:,.2f}")
        logger.info(f"Total P&L:        ${total_pnl:,.2f}")
        logger.info(f"ROI:              {roi:.2f}%")
        logger.info(f"Total Trades:     {len(trades)}")
        
        if self.current_position != 0:
            logger.warning("⚠️ Offene Position beim Beenden!")
        
        logger.info("=" * 70)
        logger.info("🛑 Live Trading Bot beendet")
        logger.info("=" * 70)


def signal_handler(sig, frame):
    """Handler für Ctrl+C"""
    global is_running
    is_running = False


def main():
    """Hauptfunktion"""
    # Registriere Signal-Handler
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        bot = LiveTradingBot()
        bot.run()
    except Exception as e:
        if logger:
            logger.error(f"❌ Fataler Fehler: {e}", exc_info=True)
        else:
            print(f"❌ Fataler Fehler: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
