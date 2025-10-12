"""
main_with_dashboard.py - Live Trading Bot with Visual Dashboard
================================================================
Enhanced version of main.py with integrated dashboard functionality
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
from utils import setup_logging, TradeLogger, generate_sample_data, validate_ohlcv_data
from dashboard import create_dashboard, DashboardModal

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


class LiveTradingBotWithDashboard:
    """
    Live Trading Bot with Dashboard Integration
    
    Erweiterte Version mit integriertem Visual Dashboard.
    """
    
    def __init__(self):
        """Initialisiere Trading Bot mit Dashboard"""
        global logger
        logger = setup_logging(
            log_level=config.log_level,
            log_file=config.log_file,
            max_bytes=config.log_max_bytes,
            backup_count=config.log_backup_count
        )
        
        logger.info("=" * 70)
        logger.info("🚀 LIVE TRADING BOT MIT DASHBOARD GESTARTET")
        logger.info("=" * 70)
        
        # Initialisiere Komponenten
        self.strategy = TradingStrategy(config.to_dict())
        self.trade_logger = TradeLogger(config.trades_file)
        
        # Initialize Dashboard
        self.dashboard = create_dashboard(
            trades_file=config.trades_file,
            config_file="data/dashboard_config.json"
        )
        self.dashboard_modal = DashboardModal(self.dashboard)
        logger.info("✓ Dashboard initialized")
        
        # Validiere API-Keys vor Live-Trading Start
        is_dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
        
        if not is_dry_run:
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
                # Display warning on dashboard
                self.dashboard.display_api_key_warning(
                    f"🚨 KRITISCHER FEHLER: {api_msg}\n"
                    f"Live-Trading kann nicht gestartet werden!\n"
                    f"Bitte konfiguriere gültige API-Keys oder aktiviere DRY_RUN=true"
                )
                raise Exception(f"API-Key Validierung fehlgeschlagen: {api_msg}")
            
            logger.info(f"✅ {api_msg}")
            logger.warning("⚠️  ACHTUNG: Live-Trading mit echtem Geld aktiviert!")
        else:
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
                # Display warning on dashboard
                self.dashboard.display_api_key_warning(
                    f"{api_msg}\n"
                    f"DRY_RUN ist aktiviert - Trading läuft im Simulationsmodus\n"
                    f"Für Live-Trading müssen gültige API-Keys konfiguriert werden"
                )
            else:
                logger.info(f"✅ {api_msg}")
        
        # Trading State
        self.current_position = 0  # 0=keine Position, 1=long, -1=short
        self.entry_price = 0.0
        self.capital = config.initial_capital
        self.initial_capital = self.capital
        
        # Daten (Simulation)
        self.data: Optional[pd.DataFrame] = None
        self.current_index = 0
        
        # Dashboard update counter
        self.update_counter = 0
        self.dashboard_update_interval = 10  # Update dashboard every 10 iterations
        
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
    
    def update_dashboard(self):
        """Update dashboard metrics"""
        self.dashboard.display_metrics_console()
    
    def export_dashboard(self):
        """Export dashboard to HTML and generate charts"""
        logger.info("📊 Exporting dashboard...")
        
        # Export HTML
        self.dashboard.export_dashboard_html()
        
        # Generate charts
        charts = self.dashboard.generate_all_charts(use_plotly=True)
        logger.info(f"✓ Generated {len(charts)} chart(s)")
    
    def run(self):
        """Haupt-Trading-Loop mit Dashboard-Updates"""
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
                
                # Update dashboard periodically
                self.update_counter += 1
                if self.update_counter >= self.dashboard_update_interval:
                    logger.info("\n📊 Dashboard Update:")
                    self.update_dashboard()
                    self.update_counter = 0
                
                # Warte bis zum nächsten Update
                time.sleep(config.update_interval)
                
        except KeyboardInterrupt:
            logger.info("\n⏹️ Benutzer-Abbruch erkannt")
            self.shutdown()
        except Exception as e:
            logger.error(f"❌ Kritischer Fehler: {e}", exc_info=True)
            self.shutdown()
    
    def shutdown(self):
        """Sauberes Herunterfahren mit Dashboard-Export"""
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
        
        # Export Dashboard
        logger.info("\n📊 Exporting final dashboard...")
        self.export_dashboard()
        
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
        bot = LiveTradingBotWithDashboard()
        bot.run()
    except Exception as e:
        if logger:
            logger.error(f"❌ Fataler Fehler: {e}", exc_info=True)
        else:
            print(f"❌ Fataler Fehler: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
