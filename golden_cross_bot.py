"""
golden_cross_bot.py - Vollständiger Golden Cross Trading Bot
============================================================

Kombiniert:
- Golden Cross Strategie
- Alpaca Integration (Primary) / Binance Integration (Legacy)
- Risikomanagement
- Paper-Trading
- Live-Monitoring

VERWENDUNG:
    # Paper-Trading (simuliert) with Alpaca:
    python golden_cross_bot.py --mode paper --symbol AAPL
    
    # Paper-Trading with crypto:
    python golden_cross_bot.py --mode paper --symbol BTCUSD
    
    # Live Trading (VORSICHT!):
    python golden_cross_bot.py --mode live --symbol AAPL
"""

import sys
import time
import signal
import argparse
from typing import Optional
from datetime import datetime, timedelta
import logging

from golden_cross_strategy import GoldenCrossStrategy
from utils import setup_logging, TradeLogger

# Try to import Alpaca (primary)
try:
    from alpaca_integration import AlpacaDataProvider, AlpacaOrderExecutor
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False
    logging.warning("Alpaca integration not available")

# Try to import Binance (legacy support)
try:
    from binance_integration import BinanceDataProvider, PaperTradingExecutor
    BINANCE_AVAILABLE = True
except ImportError:
    BINANCE_AVAILABLE = False
    logging.warning("Binance integration not available")

logger = None
is_running = False


class GoldenCrossBot:
    """
    Vollständiger Golden Cross Trading Bot
    
    Features:
    - Live-Daten von Binance
    - Golden Cross Detection mit Multi-Filter
    - Automatisches Risikomanagement
    - Paper/Testnet/Live Modi
    - Detailliertes Logging
    """
    
    def __init__(self, symbol: str = 'BTCUSDT', mode: str = 'paper',
                 initial_capital: float = 10000.0):
        """
        Args:
            symbol: Trading-Pair (z.B. 'BTCUSDT')
            mode: 'paper', 'testnet' oder 'live'
            initial_capital: Startkapital für Paper-Trading
        """
        global logger
        logger = setup_logging(
            log_level="INFO",
            log_file=f"logs/golden_cross_bot_{symbol}_{mode}.log"
        )
        
        self.symbol = symbol
        self.mode = mode
        self.initial_capital = initial_capital
        
        logger.info("=" * 70)
        logger.info(f"🌟 GOLDEN CROSS BOT - {mode.upper()} MODE")
        logger.info("=" * 70)
        logger.info(f"Symbol: {symbol}")
        logger.info(f"Mode: {mode}")
        logger.info(f"Initial Capital: ${initial_capital:,.2f}")
        logger.info("=" * 70)
        
        # Initialisiere Komponenten
        self._init_components()
        
        # Trading State
        self.current_position = None
        self.last_check_time = None
        
        # Performance Tracking
        self.trades_count = 0
        self.total_pnl = 0.0
    
    def _init_components(self):
        """Initialize all components"""
        
        # 1. Golden Cross Strategy
        strategy_params = {
            'short_window': 50,
            'long_window': 200,
            'confirmation_days': 3,
            'min_spread_pct': 1.0,
            'volume_confirmation': True,
            'trend_strength_filter': True,
            'volatility_filter': True,
            'max_volatility': 0.05
        }
        self.strategy = GoldenCrossStrategy(strategy_params)
        logger.info("✓ Golden Cross Strategy initialized")
        
        # 2. Data Provider - Try Alpaca first, then Binance
        if self.mode == 'paper':
            # Paper-Trading: Try Alpaca first
            if ALPACA_AVAILABLE:
                try:
                    self.data_provider = AlpacaDataProvider(paper=True)
                    if self.data_provider.test_connection():
                        logger.info("✓ Alpaca Data Provider initialized (Paper Trading)")
                        self.api_type = 'alpaca'
                        return
                except Exception as e:
                    logger.warning(f"Alpaca initialization failed: {e}")
            
            # Fallback to Binance if available
            if BINANCE_AVAILABLE:
                try:
                    self.data_provider = BinanceDataProvider(testnet=True)
                    logger.info("✓ Binance Data Provider initialized (Paper Trading)")
                    self.api_type = 'binance'
                    return
                except Exception as e:
                    logger.warning(f"Binance initialization failed: {e}")
            
            # No API available
            self.data_provider = None
            self.api_type = 'simulation'
            logger.info("✓ Paper-Trading Mode: No API connection, using simulation")
        else:
            # Live/Testnet mode: Try Alpaca first
            paper_mode = (self.mode != 'live')
            
            if ALPACA_AVAILABLE:
                try:
                    self.data_provider = AlpacaDataProvider(paper=paper_mode)
                    if self.data_provider.test_connection():
                        logger.info(f"✓ Alpaca Data Provider initialized ({'Paper' if paper_mode else 'Live'} Trading)")
                        self.api_type = 'alpaca'
                        return
                except Exception as e:
                    logger.warning(f"Alpaca initialization failed: {e}")
            
            # Fallback to Binance
            if BINANCE_AVAILABLE:
                testnet = (self.mode == 'testnet')
                self.data_provider = BinanceDataProvider(testnet=testnet)
                self.api_type = 'binance'
                logger.info(f"✓ Binance Data Provider initialized ({'Testnet' if testnet else 'Live'})")
            
            if not self.data_provider.test_connection():
                raise ConnectionError("Binance-Verbindung fehlgeschlagen!")
            
            logger.info(f"✓ Binance-Verbindung: {'TESTNET' if testnet else 'PRODUCTION'}")
        
        # 3. Order Executor
        if self.mode == 'live':
            logger.warning("=" * 70)
            logger.warning("⚠️  LIVE TRADING MODE - ECHTES GELD!")
            logger.warning("=" * 70)
            # TODO: Implement real order executor
            raise NotImplementedError("Live-Trading noch nicht implementiert!")
        else:
            self.executor = PaperTradingExecutor(initial_capital=self.initial_capital)
            logger.info("✓ Paper-Trading Executor initialisiert")
        
        # 4. Trade Logger
        self.trade_logger = TradeLogger(
            filepath=f"data/golden_cross_trades_{self.symbol}.csv"
        )
        logger.info("✓ Trade Logger initialisiert")
    
    def get_market_data(self) -> Optional[pd.DataFrame]:
        """
        Hole aktuelle Marktdaten
        
        Returns:
            DataFrame mit OHLCV-Daten oder None
        """
        try:
            if self.mode == 'paper':
                # Paper-Trading: Nutze simulierte Daten
                from utils import generate_sample_data
                df = generate_sample_data(n_bars=300, start_price=30000)
                logger.debug("Simulierte Daten generiert")
                return df
            else:
                # Echte Daten von Binance
                df = self.data_provider.get_historical_klines(
                    symbol=self.symbol,
                    interval='1d',  # Tages-Kerzen für Golden Cross
                    limit=300
                )
                logger.debug(f"Marktdaten geladen: {len(df)} Kerzen")
                return df
        
        except Exception as e:
            logger.error(f"Fehler beim Laden der Marktdaten: {e}")
            return None
    
    def check_and_execute(self):
        """Haupt-Trading-Logik: Prüfe Signal und führe Trade aus"""
        
        # 1. Hole Marktdaten
        df = self.get_market_data()
        if df is None or len(df) == 0:
            logger.warning("Keine Marktdaten verfügbar")
            return
        
        # 2. Analysiere mit Golden Cross Strategie
        signal = self.strategy.generate_signal(df)
        current_price = df['close'].iloc[-1]
        
        logger.info(f"💹 Aktueller Preis: ${current_price:,.2f}")
        
        # 3. Verarbeite Signal
        if signal == 1 and not self.executor.has_position(self.symbol):
            # BUY Signal und keine Position
            self._execute_buy(current_price)
        
        elif signal == -1 and self.executor.has_position(self.symbol):
            # SELL Signal und Position vorhanden
            self._execute_sell(current_price)
        
        elif signal == 0:
            # HOLD
            if self.executor.has_position(self.symbol):
                position = self.executor.get_position(self.symbol)
                unrealized_pnl = (current_price - position['entry_price']) * position['quantity']
                unrealized_pnl_pct = (unrealized_pnl / (position['entry_price'] * position['quantity'])) * 100
                
                logger.info(
                    f"⏸️  HOLD | "
                    f"Position: {position['quantity']} @ ${position['entry_price']:.2f} | "
                    f"Unrealized P&L: ${unrealized_pnl:.2f} ({unrealized_pnl_pct:+.2f}%)"
                )
            else:
                logger.info("⏸️  HOLD | Keine Position")
        
        # 4. Update Last Check Time
        self.last_check_time = datetime.now()
    
    def _execute_buy(self, price: float):
        """
        Führe BUY Order aus
        
        Args:
            price: Kaufpreis
        """
        # Berechne Position Size (z.B. 20% des verfügbaren Kapitals)
        position_size_pct = 0.20
        available_capital = self.executor.capital
        position_value = available_capital * position_size_pct
        quantity = position_value / price
        
        # Runde auf sinnvolle Precision (für BTC: 3 Dezimalstellen)
        quantity = round(quantity, 3)
        
        logger.info("=" * 70)
        logger.info("🎯 EXECUTING BUY ORDER")
        logger.info("=" * 70)
        logger.info(f"Symbol: {self.symbol}")
        logger.info(f"Price: ${price:,.2f}")
        logger.info(f"Quantity: {quantity}")
        logger.info(f"Total Value: ${quantity * price:,.2f}")
        logger.info("=" * 70)
        
        # Führe aus
        result = self.executor.buy(self.symbol, quantity, price)
        
        if result['status'] == 'SUCCESS':
            # Log Trade
            self.trade_logger.log_trade(
                order_type='BUY',
                price=price,
                quantity=quantity,
                strategies=['GoldenCross'],
                capital=self.executor.capital,
                symbol=self.symbol
            )
            
            self.trades_count += 1
            logger.info("✅ BUY ORDER ERFOLGREICH")
        else:
            logger.error(f"❌ BUY ORDER FEHLGESCHLAGEN: {result.get('reason', 'Unknown')}")
    
    def _execute_sell(self, price: float):
        """
        Führe SELL Order aus
        
        Args:
            price: Verkaufspreis
        """
        position = self.executor.get_position(self.symbol)
        
        logger.info("=" * 70)
        logger.info("🎯 EXECUTING SELL ORDER")
        logger.info("=" * 70)
        logger.info(f"Symbol: {self.symbol}")
        logger.info(f"Price: ${price:,.2f}")
        logger.info(f"Quantity: {position['quantity']}")
        logger.info(f"Entry Price: ${position['entry_price']:,.2f}")
        logger.info("=" * 70)
        
        # Führe aus
        result = self.executor.sell(self.symbol, price)
        
        if result['status'] == 'SUCCESS':
            trade = result['trade']
            pnl = trade['pnl']
            
            # Log Trade
            self.trade_logger.log_trade(
                order_type='SELL',
                price=price,
                quantity=position['quantity'],
                strategies=['GoldenCross'],
                capital=self.executor.capital,
                pnl=pnl,
                symbol=self.symbol
            )
            
            self.trades_count += 1
            self.total_pnl += pnl
            
            emoji = "✅💰" if pnl > 0 else "❌📉"
            logger.info(f"{emoji} SELL ORDER ERFOLGREICH")
            logger.info(f"P&L: ${pnl:.2f} ({trade['pnl_pct']:+.2f}%)")
        else:
            logger.error(f"❌ SELL ORDER FEHLGESCHLAGEN: {result.get('reason', 'Unknown')}")
    
    def print_status(self):
        """Drucke aktuellen Status"""
        print("\n" + "=" * 70)
        print("📊 BOT STATUS")
        print("=" * 70)
        
        # Performance
        perf = self.executor.get_performance_summary()
        print(f"\n💰 PERFORMANCE:")
        print(f"  Initial Capital:  ${perf['initial_capital']:,.2f}")
        print(f"  Current Capital:  ${perf['current_capital']:,.2f}")
        print(f"  Total P&L:        ${perf['total_pnl']:,.2f}")
        print(f"  ROI:              {perf['roi']:+.2f}%")
        print(f"  Total Trades:     {perf['total_trades']}")
        print(f"  Win Rate:         {perf['win_rate']:.1f}%")
        
        # Position
        print(f"\n📍 POSITION:")
        if self.executor.has_position(self.symbol):
            position = self.executor.get_position(self.symbol)
            print(f"  {self.symbol}: {position['quantity']} @ ${position['entry_price']:,.2f}")
            print(f"  Entry Time: {position['entry_time']}")
        else:
            print("  Keine offene Position")
        
        # Strategie Info
        print(f"\n🎯 STRATEGIE STATUS:")
        info = self.strategy.get_info()
        if info.get('last_cross_type'):
            print(f"  Letzter Cross: {info['last_cross_type'].upper()}")
            print(f"  Cross Datum: {info['last_cross_date']}")
            print(f"  Bestätigt: {'Ja' if info['confirmed'] else 'Nein'}")
        else:
            print("  Kein aktiver Cross")
        
        print("=" * 70)
    
    def run(self, check_interval: int = 3600):
        """
        Starte Bot
        
        Args:
            check_interval: Sekunden zwischen Checks (default: 3600 = 1 Stunde)
        """
        global is_running
        is_running = True
        
        logger.info("🚀 Bot startet...")
        logger.info(f"Check-Intervall: {check_interval}s ({check_interval/3600:.1f}h)")
        logger.info("Drücke Ctrl+C zum Beenden\n")
        
        try:
            while is_running:
                logger.info("\n" + "=" * 70)
                logger.info(f"🔄 CHECK @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info("=" * 70)
                
                # Führe Check aus
                self.check_and_execute()
                
                # Status anzeigen
                self.print_status()
                
                # Warte bis zum nächsten Check
                if is_running:
                    logger.info(f"\n⏳ Nächster Check in {check_interval}s...")
                    time.sleep(check_interval)
        
        except KeyboardInterrupt:
            logger.info("\n⏹️ Benutzer-Abbruch erkannt")
        except Exception as e:
            logger.error(f"❌ Unerwarteter Fehler: {e}", exc_info=True)
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Sauberes Herunterfahren"""
        global is_running
        is_running = False
        
        logger.info("\n" + "=" * 70)
        logger.info("📊 FINAL REPORT")
        logger.info("=" * 70)
        
        # Final Performance
        perf = self.executor.get_performance_summary()
        logger.info(f"\n💰 FINAL PERFORMANCE:")
        logger.info(f"  Initial Capital:  ${perf['initial_capital']:,.2f}")
        logger.info(f"  Final Capital:    ${perf['current_capital']:,.2f}")
        logger.info(f"  Total P&L:        ${perf['total_pnl']:,.2f}")
        logger.info(f"  ROI:              {perf['roi']:+.2f}%")
        logger.info(f"  Total Trades:     {perf['total_trades']}")
        logger.info(f"  Win Rate:         {perf['win_rate']:.1f}%")
        
        # Warnings
        if self.executor.has_position(self.symbol):
            logger.warning("⚠️ Offene Position beim Beenden!")
        
        # Cleanup
        if self.data_provider:
            self.data_provider.close()
        
        logger.info("\n" + "=" * 70)
        logger.info("🛑 Golden Cross Bot beendet")
        logger.info("=" * 70)


def signal_handler(sig, frame):
    """Handler für Ctrl+C"""
    global is_running
    is_running = False


def main():
    """Hauptfunktion mit CLI-Argumenten"""
    parser = argparse.ArgumentParser(
        description='Golden Cross Trading Bot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  # Paper-Trading (Simulation):
  python golden_cross_bot.py --mode paper --symbol BTCUSDT
  
  # Testnet:
  python golden_cross_bot.py --mode testnet --symbol BTCUSDT --capital 5000
  
  # Custom Check-Intervall (alle 30 Minuten):
  python golden_cross_bot.py --mode paper --interval 1800
        """
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        choices=['paper', 'testnet', 'live'],
        default='paper',
        help='Trading-Modus (default: paper)'
    )
    
    parser.add_argument(
        '--symbol',
        type=str,
        default='BTCUSDT',
        help='Trading-Pair (default: BTCUSDT)'
    )
    
    parser.add_argument(
        '--capital',
        type=float,
        default=10000.0,
        help='Initial Capital (default: 10000)'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=3600,
        help='Check-Intervall in Sekunden (default: 3600 = 1h)'
    )
    
    args = parser.parse_args()
    
    # Registriere Signal-Handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Sicherheitswarnung für Live-Mode
    if args.mode == 'live':
        print("\n" + "=" * 70)
        print("⚠️  WARNUNG: LIVE TRADING MODE")
        print("=" * 70)
        print("Du bist dabei LIVE TRADING mit ECHTEM GELD zu starten!")
        print("Bist du dir sicher?\n")
        confirm = input("Tippe 'CONFIRM' um fortzufahren: ")
        
        if confirm != 'CONFIRM':
            print("Abgebrochen.")
            sys.exit(0)
    
    try:
        # Erstelle und starte Bot
        bot = GoldenCrossBot(
            symbol=args.symbol,
            mode=args.mode,
            initial_capital=args.capital
        )
        
        bot.run(check_interval=args.interval)
    
    except Exception as e:
        print(f"\n❌ Fataler Fehler: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
