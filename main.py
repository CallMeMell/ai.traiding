"""
main.py - Haupt-Anwendung für Live-Trading
==========================================
Startet den Trading-Bot im Live-Modus
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

# Globale Variablen
logger = None
is_running = False


class LiveTradingBot:
    """
    Live Trading Bot
    
    Simuliert Live-Trading mit fortlaufenden Marktdaten.
    In Production würde dies echte API-Calls zu Alpaca/Binance machen.
    """
    
    def __init__(self):
        """Initialisiere Trading Bot"""
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
        
        # Initialisiere Komponenten
        self.strategy = TradingStrategy(config.to_dict())
        self.trade_logger = TradeLogger(config.trades_file)
        
        # Trading State
        self.current_position = 0  # 0=keine Position, 1=long, -1=short
        self.entry_price = 0.0
        self.capital = config.initial_capital
        self.initial_capital = self.capital
        
        # Daten (Simulation)
        self.data: Optional[pd.DataFrame] = None
        self.current_index = 0
        
        logger.info(f"Initial Capital: ${self.capital:,.2f}")
        logger.info(f"Trading Symbol: {config.trading_symbol}")
        logger.info(f"Update Interval: {config.update_interval}s")
        logger.info(f"Active Strategies: {config.active_strategies}")
        logger.info(f"Cooperation Logic: {config.cooperation_logic}")
        logger.info("=" * 70)
    
    def initialize_data(self):
        """Initialisiere Marktdaten (simuliert)"""
        logger.info("Generiere initiale Marktdaten...")
        self.data = generate_sample_data(n_bars=500, start_price=30000)
        self.current_index = len(self.data) - 1
        logger.info(f"✓ {len(self.data)} Kerzen generiert")
    
    def add_new_candle(self):
        """Füge neue Kerze hinzu (simuliert Live-Daten)"""
        if self.data is None:
            return
        
        # Hole letzten Preis
        last_close = self.data['close'].iloc[-1]
        
        # Generiere neue Kerze mit Random Walk
        new_price = last_close + np.random.normal(0, 100)
        new_price = max(new_price, 1000)  # Verhindere negative Preise
        
        new_candle = pd.DataFrame({
            'timestamp': [datetime.now()],
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
