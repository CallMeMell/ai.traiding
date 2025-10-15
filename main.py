"""
main.py - Haupt-Anwendung für Live-Trading
==========================================
Startet den Trading-Bot im Live-Modus mit Alpaca API Integration
"""
import sys
import time
import signal
import os
from typing import Optional
import pandas as pd
import numpy as np
from datetime import datetime

# Imports
from config import config
from strategy import TradingStrategy
from utils import setup_logging, TradeLogger, generate_sample_data, validate_ohlcv_data, calculate_current_drawdown
from alerts import AlertManager

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

# Try to import unified Broker API (New unified interface)
try:
    from broker_api import BrokerFactory, BrokerInterface
    BROKER_API_AVAILABLE = True
except ImportError:
    BROKER_API_AVAILABLE = False

# Globale Variablen
logger = None
is_running = False


def validate_api_keys_for_live_trading() -> tuple[bool, str]:
    """
    Validiert API-Keys vor Live-Trading Start.
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
    api_key = os.getenv("BINANCE_API_KEY", "") or config.BINANCE_API_KEY
    api_secret = os.getenv("BINANCE_API_SECRET", "") or config.BINANCE_SECRET_KEY
    
    if not api_key:
        return False, "BINANCE_API_KEY fehlt - Live-Trading nicht möglich"
    
    if not api_secret:
        return False, "BINANCE_API_SECRET fehlt - Live-Trading nicht möglich"
    
    # Validiere Länge (Binance API Keys sind typischerweise 64 Zeichen)
    if len(api_key) < 10:
        return False, "BINANCE_API_KEY erscheint ungültig (zu kurz) - Live-Trading nicht möglich"
    
    if len(api_secret) < 10:
        return False, "BINANCE_API_SECRET erscheint ungültig (zu kurz) - Live-Trading nicht möglich"
    
    return True, "API-Keys validiert und bereit für Live-Trading"


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
        
        # Validiere API-Keys vor Live-Trading Start
        is_dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
        
        if use_live_data and not paper_trading and not is_dry_run:
            # Live-Trading mit echtem Geld - API-Keys MÜSSEN gültig sein
            logger.info("\n⚠️  LIVE-TRADING MODUS ERKANNT - Validiere API-Keys...")
            api_valid, api_msg = validate_api_keys_for_live_trading()
            
            if not api_valid:
                logger.critical("=" * 70)
                logger.critical("🚨 API-KEY VALIDIERUNG FEHLGESCHLAGEN! 🚨")
                logger.critical("=" * 70)
                logger.critical(api_msg)
                logger.critical("Live-Trading kann NICHT gestartet werden!")
                logger.critical("Bitte konfiguriere gültige API-Keys oder aktiviere DRY_RUN=true")
                logger.critical("=" * 70)
                raise Exception(f"API-Key Validierung fehlgeschlagen: {api_msg}")
            
            logger.info(f"✅ {api_msg}")
            logger.warning("⚠️  ACHTUNG: Live-Trading mit echtem Geld aktiviert!")
        elif use_live_data and not paper_trading:
            # DRY_RUN aktiviert - Warnung aber kein Abbruch
            logger.info("\n📊 DRY_RUN Modus aktiviert - API-Keys werden geprüft...")
            api_valid, api_msg = validate_api_keys_for_live_trading()
            
            if not api_valid:
                logger.warning("=" * 70)
                logger.warning("⚠️  API-KEY WARNUNG")
                logger.warning("=" * 70)
                logger.warning(api_msg)
                logger.warning("DRY_RUN ist aktiviert - Trading läuft weiter im Simulationsmodus")
                logger.warning("Für Live-Trading müssen gültige API-Keys konfiguriert werden")
                logger.warning("=" * 70)
            else:
                logger.info(f"✅ {api_msg}")
        
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
        
        # Circuit Breaker - Drawdown Tracking
        self.equity_curve = [self.initial_capital]
        self.circuit_breaker_triggered = False
        self.is_dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
        
        # Advanced Circuit Breaker (Feature flag for PR #187)
        # When use_advanced_circuit_breaker is True, we'd use CircuitBreakerManager
        # For now, just set the flag to False (legacy circuit breaker)
        self.use_advanced_cb = config.use_advanced_circuit_breaker
        self.circuit_breaker_manager = None  # Would be initialized if use_advanced_cb=True
        
        # Alert System
        self.alert_manager = AlertManager(
            enable_telegram=os.getenv('ENABLE_TELEGRAM_ALERTS', 'false').lower() == 'true',
            enable_email=os.getenv('ENABLE_EMAIL_ALERTS', 'false').lower() == 'true'
        )
        
        # Database Integration
        if config.use_database or os.getenv('USE_DATABASE', 'false').lower() == 'true':
            try:
                from db import DatabaseManager
                self.db = DatabaseManager(config.database_path)
                logger.info(f"✓ Database integration enabled: {config.database_path}")
            except ImportError:
                logger.warning("⚠️ Database module not found - running without database")
                self.db = None
        else:
            self.db = None
            logger.info("Database integration disabled")
        
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
        
        # Log broker API availability
        if BROKER_API_AVAILABLE:
            logger.info("✓ Unified Broker API available")
            logger.info("  Use broker_api.py for advanced trading features")
        
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
    
    def check_circuit_breaker(self) -> bool:
        """
        Prüfe Circuit Breaker (Drawdown-Limit)
        
        Returns:
            True wenn Circuit Breaker ausgelöst wurde
        """
        # Circuit Breaker nur im Production-Modus (nicht DRY_RUN)
        if self.is_dry_run:
            return False
        
        # Update equity curve
        self.equity_curve.append(self.capital)
        
        # Berechne aktuellen Drawdown
        current_drawdown = calculate_current_drawdown(self.equity_curve)
        
        # Prüfe ob Limit überschritten
        drawdown_limit_percent = config.max_drawdown_limit * 100
        
        if current_drawdown < -drawdown_limit_percent:
            self.circuit_breaker_triggered = True
            logger.critical("=" * 70)
            logger.critical("🚨 CIRCUIT BREAKER AUSGELÖST! 🚨")
            logger.critical("=" * 70)
            logger.critical(f"Aktueller Drawdown: {current_drawdown:.2f}%")
            logger.critical(f"Drawdown-Limit: {drawdown_limit_percent:.2f}%")
            logger.critical(f"Initial Capital: ${self.initial_capital:,.2f}")
            logger.critical(f"Current Capital: ${self.capital:,.2f}")
            logger.critical(f"Verlust: ${self.capital - self.initial_capital:,.2f}")
            logger.critical("Trading wird SOFORT gestoppt!")
            logger.critical("=" * 70)
            
            # Sende Circuit Breaker Alert
            self.alert_manager.send_circuit_breaker_alert(
                drawdown=current_drawdown,
                limit=drawdown_limit_percent,
                capital=self.capital,
                initial_capital=self.initial_capital
            )
            
            return True
        
        return False
    
    def process_signal(self, analysis: dict):
        """
        Verarbeite Trading-Signal
        
        Args:
            analysis: Signal-Dictionary von Strategy
        """
        # Prüfe Circuit Breaker vor Trade-Ausführung
        if self.check_circuit_breaker():
            logger.warning("⚠️ Trading gestoppt - Circuit Breaker aktiv")
            return
        
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
            
            # Log to database if enabled
            if self.db:
                try:
                    self.db.insert_trade(
                        symbol=config.trading_symbol,
                        order_type='BUY',
                        price=current_price,
                        quantity=config.trade_size,
                        strategies=strategies,
                        capital=self.capital,
                        pnl=0.0
                    )
                except Exception as e:
                    logger.warning(f"Failed to log trade to database: {e}")
            
            logger.info(f"📈 BUY @ ${current_price:.2f} | Strategien: {strategies}")
            
            # Sende Trade Alert
            self.alert_manager.send_trade_alert(
                order_type='BUY',
                symbol=config.trading_symbol,
                price=current_price,
                quantity=config.trade_size,
                strategies=strategies,
                capital=self.capital
            )
        
        # SELL Signal und Long Position
        elif signal == -1 and self.current_position == 1:
            pnl = (current_price - self.entry_price) * config.trade_size
            self.capital += pnl
            self.current_position = 0
            
            # Update equity curve nach Trade
            self.equity_curve.append(self.capital)
            
            self.trade_logger.log_trade(
                order_type='SELL',
                price=current_price,
                quantity=config.trade_size,
                strategies=strategies,
                capital=self.capital,
                pnl=pnl,
                symbol=config.trading_symbol
            )
            
            # Log to database if enabled
            if self.db:
                try:
                    self.db.insert_trade(
                        symbol=config.trading_symbol,
                        order_type='SELL',
                        price=current_price,
                        quantity=config.trade_size,
                        strategies=strategies,
                        capital=self.capital,
                        pnl=pnl
                    )
                    # Also update equity curve
                    drawdown = calculate_current_drawdown(self.equity_curve)
                    self.db.insert_equity_point(
                        capital=self.capital,
                        drawdown=drawdown
                    )
                except Exception as e:
                    logger.warning(f"Failed to log trade to database: {e}")
            
            pnl_emoji = "💰" if pnl > 0 else "📉"
            logger.info(
                f"{pnl_emoji} SELL @ ${current_price:.2f} | "
                f"P&L: ${pnl:.2f} | "
                f"Capital: ${self.capital:.2f} | "
                f"Strategien: {strategies}"
            )
            
            # Sende Trade Alert mit P&L
            self.alert_manager.send_trade_alert(
                order_type='SELL',
                symbol=config.trading_symbol,
                price=current_price,
                quantity=config.trade_size,
                strategies=strategies,
                capital=self.capital,
                pnl=pnl
            )
            
            # Prüfe Circuit Breaker nach Trade
            if self.check_circuit_breaker():
                logger.error("⚠️ Circuit Breaker nach Trade ausgelöst!")
                global is_running
                is_running = False
    
    def run(self):
        """Haupt-Trading-Loop"""
        global is_running
        is_running = True
        
        # Initialisiere Daten
        self.initialize_data()
        
        logger.info("🔄 Trading-Loop aktiv")
        logger.info(f"Circuit Breaker: {'AKTIV (Production)' if not self.is_dry_run else 'INAKTIV (DRY_RUN)'}")
        logger.info(f"Drawdown-Limit: {config.max_drawdown_limit * 100:.1f}%")
        logger.info("Drücke Ctrl+C zum Beenden\n")
        
        try:
            while is_running and not self.circuit_breaker_triggered:
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
                
                # Berechne aktuellen Drawdown für Status-Update
                current_dd = calculate_current_drawdown(self.equity_curve) if len(self.equity_curve) > 1 else 0.0
                
                logger.info(
                    f"💹 Preis: ${current_price:.2f} | "
                    f"Position: {position_text} | "
                    f"Capital: ${self.capital:.2f} | "
                    f"DD: {current_dd:.2f}%"
                )
                
                # Warte bis zum nächsten Update
                time.sleep(config.update_interval)
            
            # Falls Circuit Breaker ausgelöst
            if self.circuit_breaker_triggered:
                logger.error("🚨 Trading wurde durch Circuit Breaker gestoppt!")
                self.shutdown()
                
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
        
        # Berechne Maximum Drawdown
        from utils import calculate_max_drawdown
        if len(self.equity_curve) > 1:
            max_dd_pct, max_dd_val, peak_val, trough_val = calculate_max_drawdown(self.equity_curve)
            logger.info(f"Maximum Drawdown: {max_dd_pct:.2f}%")
        
        logger.info(f"Initial Capital:  ${self.initial_capital:,.2f}")
        logger.info(f"Final Capital:    ${self.capital:,.2f}")
        logger.info(f"Total P&L:        ${total_pnl:,.2f}")
        logger.info(f"ROI:              {roi:.2f}%")
        logger.info(f"Total Trades:     {len(trades)}")
        
        if self.circuit_breaker_triggered:
            logger.critical("🚨 CIRCUIT BREAKER WAR AKTIV!")
            logger.critical(f"Drawdown-Limit von {config.max_drawdown_limit * 100:.1f}% wurde überschritten")
        
        if self.current_position != 0:
            logger.warning("⚠️ Offene Position beim Beenden!")
        
        logger.info("=" * 70)
        logger.info("🛑 Live Trading Bot beendet")
        logger.info("=" * 70)


def signal_handler(sig, frame):
    """Handler für Ctrl+C"""
    global is_running
    is_running = False


def run_live_monitoring_mode():
    """
    Run in live monitoring mode
    
    Uses the LiveMarketMonitor for continuous market monitoring
    with strategy integration and alerts.
    """
    global logger
    logger = setup_logging(
        log_level=config.log_level,
        log_file=config.log_file,
        max_bytes=config.log_max_bytes,
        backup_count=config.log_backup_count
    )
    
    try:
        from live_market_monitor import LiveMarketMonitor
    except ImportError:
        logger.error("Live Market Monitor not available. Please ensure live_market_monitor.py exists.")
        return
    
    logger.info("=" * 70)
    logger.info("🔍 LIVE MARKET MONITORING MODE")
    logger.info("=" * 70)
    
    # Convert symbol format for Binance (BTC/USDT -> BTCUSDT)
    symbols = [s.replace('/', '') for s in config.monitor_symbols]
    
    logger.info(f"Monitoring symbols: {', '.join(symbols)}")
    logger.info(f"Interval: {config.monitor_interval}")
    logger.info(f"Update frequency: {config.monitor_update_interval}s")
    logger.info(f"Price alert threshold: {config.price_alert_threshold}%")
    
    # Determine API keys
    if config.BINANCE_TESTNET_API_KEY and config.BINANCE_TESTNET_SECRET_KEY:
        api_key = config.BINANCE_TESTNET_API_KEY
        api_secret = config.BINANCE_TESTNET_SECRET_KEY
        testnet = True
        logger.info("Using Binance TESTNET")
    elif config.BINANCE_API_KEY and config.BINANCE_SECRET_KEY:
        api_key = config.BINANCE_API_KEY
        api_secret = config.BINANCE_SECRET_KEY
        testnet = False
        logger.warning("⚠️ Using Binance PRODUCTION")
    else:
        api_key = None
        api_secret = None
        testnet = True
        logger.info("No API keys - using public data only")
    
    # Initialize monitor
    monitor = LiveMarketMonitor(
        symbols=symbols,
        interval=config.monitor_interval,
        update_interval=config.monitor_update_interval,
        exchange='binance',
        api_key=api_key,
        api_secret=api_secret,
        testnet=testnet,
        price_alert_threshold=config.price_alert_threshold
    )
    
    # Test connection
    logger.info("\nTesting connection...")
    if not monitor.test_connection():
        logger.error("❌ Connection failed. Check your API keys and network.")
        return
    logger.info("✓ Connection successful")
    
    # Integrate strategy if enabled
    if config.enable_strategy_alerts:
        logger.info("\nIntegrating trading strategies...")
        strategy = TradingStrategy(config.to_dict())
        monitor.integrate_strategy(strategy)
        logger.info(f"✓ Strategy integrated ({len(config.active_strategies)} strategies active)")
    
    logger.info("=" * 70)
    
    # Start monitoring
    try:
        monitor.start_monitoring()
    except KeyboardInterrupt:
        logger.info("\n⏹️ Monitoring stopped by user")
    except Exception as e:
        logger.error(f"❌ Monitoring error: {e}", exc_info=True)


def main():
    """Hauptfunktion"""
    # Registriere Signal-Handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Check if live monitoring mode is requested
    if len(sys.argv) > 1 and sys.argv[1] == '--monitor':
        run_live_monitoring_mode()
        return
    
    # Check if live monitoring is enabled in config
    if config.enable_live_monitoring:
        logger_temp = setup_logging(
            log_level=config.log_level,
            log_file=config.log_file,
            max_bytes=config.log_max_bytes,
            backup_count=config.log_backup_count
        )
        logger_temp.info("Live monitoring enabled in config. Use --monitor flag or disable in config.")
        logger_temp.info("Starting regular trading bot mode...")
    
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
