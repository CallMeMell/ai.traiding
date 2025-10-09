"""
backtester.py - Backtesting Engine
===================================
Teste Trading-Strategien mit historischen Daten
"""
import sys
from typing import Optional, Dict, Any
import pandas as pd
from datetime import datetime

from config import config
from strategy import TradingStrategy
from utils import (
    setup_logging, TradeLogger, generate_sample_data,
    validate_ohlcv_data, calculate_performance_metrics,
    format_currency, format_percentage,
    generate_equity_curve_chart, generate_drawdown_chart,
    generate_pnl_distribution_chart
)

logger = None


class Backtester:
    """
    Backtesting Engine für Trading-Strategien
    
    Testet Strategien mit historischen OHLCV-Daten und
    liefert detaillierte Performance-Metriken.
    """
    
    def __init__(self, initial_capital: float = None):
        """
        Args:
            initial_capital: Startkapital (optional, nutzt sonst config)
        """
        global logger
        logger = setup_logging(
            log_level=config.log_level,
            log_file=config.log_file
        )
        
        logger.info("=" * 70)
        logger.info("📈 BACKTESTER INITIALISIERT")
        logger.info("=" * 70)
        
        # Initialisiere Komponenten
        self.strategy = TradingStrategy(config.to_dict())
        self.trade_logger = TradeLogger(config.trades_file)
        
        # Trading State
        self.initial_capital = initial_capital or config.backtest_initial_capital
        self.capital = self.initial_capital
        self.current_position = 0  # 0=keine Position, 1=long
        self.entry_price = 0.0
        
        # Metriken
        self.trades = []
        self.equity_curve = []
        
        logger.info(f"Initial Capital: ${self.initial_capital:,.2f}")
        logger.info(f"Strategien: {config.active_strategies}")
        logger.info(f"Cooperation Logic: {config.cooperation_logic}")
        logger.info("=" * 70 + "\n")
    
    def load_data(self, filepath: str) -> pd.DataFrame:
        """
        Lade historische Daten aus CSV
        
        Args:
            filepath: Pfad zur CSV-Datei mit OHLCV-Daten
        
        Returns:
            DataFrame mit validierten Daten
        """
        logger.info(f"Lade Daten von: {filepath}")
        
        try:
            df = pd.read_csv(filepath)
            
            # Konvertiere timestamp
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Validiere Daten
            is_valid, error = validate_ohlcv_data(df)
            if not is_valid:
                raise ValueError(f"Ungültige Daten: {error}")
            
            logger.info(f"✓ {len(df)} Kerzen geladen und validiert\n")
            return df
            
        except FileNotFoundError:
            logger.error(f"Datei nicht gefunden: {filepath}")
            raise
        except Exception as e:
            logger.error(f"Fehler beim Laden der Daten: {e}")
            raise
    
    def run(self, data: pd.DataFrame):
        """
        Führe Backtest mit gegebenen Daten durch
        
        Args:
            data: DataFrame mit OHLCV-Daten
        """
        logger.info("=" * 70)
        logger.info("🚀 STARTE BACKTEST")
        logger.info("=" * 70)
        logger.info(f"Periode: {data['timestamp'].iloc[0]} bis {data['timestamp'].iloc[-1]}")
        logger.info(f"Datenpunkte: {len(data)}")
        logger.info("=" * 70 + "\n")
        
        # Reset State
        self.capital = self.initial_capital
        self.current_position = 0
        self.trades = []
        self.equity_curve = []
        
        # Mindestanzahl für Indikatoren
        min_bars = 100
        
        # Iteriere durch Daten
        for i in range(min_bars, len(data)):
            # Hole Daten bis zu diesem Punkt
            df_slice = data.iloc[:i + 1].copy()
            
            # Analysiere
            analysis = self.strategy.analyze(df_slice)
            
            signal = analysis['signal']
            current_price = analysis['current_price']
            current_time = analysis.get('timestamp', data['timestamp'].iloc[i])
            strategies = analysis['triggering_strategies']
            
            # Verarbeite Signal
            if signal == 1 and self.current_position == 0:
                # BUY
                self.current_position = 1
                self.entry_price = current_price
                
                trade = {
                    'timestamp': current_time,
                    'type': 'BUY',
                    'price': current_price,
                    'quantity': config.trade_size,
                    'strategies': strategies,
                    'capital_before': self.capital,
                    'pnl': 0.0
                }
                self.trades.append(trade)
                
                logger.info(
                    f"📊 [{current_time}] BUY @ ${current_price:.2f} | "
                    f"Strategien: {', '.join(strategies)}"
                )
            
            elif signal == -1 and self.current_position == 1:
                # SELL
                pnl = (current_price - self.entry_price) * config.trade_size
                self.capital += pnl
                self.current_position = 0
                
                trade = {
                    'timestamp': current_time,
                    'type': 'SELL',
                    'price': current_price,
                    'quantity': config.trade_size,
                    'strategies': strategies,
                    'capital_before': self.capital - pnl,
                    'pnl': pnl
                }
                self.trades.append(trade)
                
                pnl_emoji = "💰" if pnl > 0 else "📉"
                logger.info(
                    f"📊 [{current_time}] SELL @ ${current_price:.2f} | "
                    f"P&L: ${pnl:.2f} | "
                    f"Capital: ${self.capital:.2f} | "
                    f"Strategien: {', '.join(strategies)}"
                )
            
            # Speichere Equity
            self.equity_curve.append({
                'timestamp': current_time,
                'capital': self.capital,
                'position_value': self.current_position * config.trade_size * current_price
            })
        
        # Generate Report
        self._generate_report()
    
    def _generate_report(self):
        """Generiere detaillierten Backtest-Report"""
        logger.info("\n" + "=" * 70)
        logger.info("📊 BACKTEST REPORT")
        logger.info("=" * 70)
        
        # Basis-Metriken
        total_pnl = self.capital - self.initial_capital
        roi = (total_pnl / self.initial_capital) * 100
        
        logger.info(f"\n💰 KAPITAL:")
        logger.info(f"  Initial Capital:  {format_currency(self.initial_capital)}")
        logger.info(f"  Final Capital:    {format_currency(self.capital)}")
        logger.info(f"  Total P&L:        {format_currency(total_pnl)}")
        logger.info(f"  ROI:              {format_percentage(roi)}")
        
        # Trade-Statistiken mit erweiterten Metriken
        if self.trades:
            sell_trades = [t for t in self.trades if t['type'] == 'SELL']
            
            if sell_trades:
                # Erstelle Equity Curve für Metriken
                equity_values = [eq['capital'] for eq in self.equity_curve] if self.equity_curve else None
                
                # Berechne alle Metriken mit neuer Funktion
                metrics = calculate_performance_metrics(
                    sell_trades,
                    equity_curve=equity_values,
                    initial_capital=self.initial_capital
                )
                
                logger.info(f"\n📈 TRADES:")
                logger.info(f"  Total Trades:     {metrics['total_trades']}")
                logger.info(f"  Win Rate:         {format_percentage(metrics['win_rate'])}")
                logger.info(f"  Best Trade:       {format_currency(metrics['best_trade'])}")
                logger.info(f"  Worst Trade:      {format_currency(metrics['worst_trade'])}")
                logger.info(f"  Average P&L:      {format_currency(metrics['avg_pnl'])}")
                logger.info(f"  Profit Factor:    {metrics['profit_factor']:.2f}")
                
                # Erweiterte Metriken
                logger.info(f"\n📊 ERWEITERTE METRIKEN:")
                logger.info(f"  Sharpe Ratio:     {metrics['sharpe_ratio']:.2f}")
                logger.info(f"  Max Drawdown:     {format_percentage(metrics['max_drawdown'])}")
                logger.info(f"  Calmar Ratio:     {metrics['calmar_ratio']:.2f}")
                logger.info(f"  Volatility:       {format_percentage(metrics['volatility'] * 100)}")
                
                if metrics['avg_trade_duration'] > 0:
                    # Convert seconds to hours
                    avg_hours = metrics['avg_trade_duration'] / 3600
                    logger.info(f"  Avg Trade Duration: {avg_hours:.2f} hours")
        
        # Strategie-Breakdown
        strategy_counts = {}
        for trade in self.trades:
            for strat in trade['strategies']:
                strategy_counts[strat] = strategy_counts.get(strat, 0) + 1
        
        if strategy_counts:
            logger.info(f"\n🎯 STRATEGIE-BREAKDOWN:")
            for strat, count in sorted(strategy_counts.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"  {strat}: {count} Signale")
        
        # Warnungen
        if self.current_position != 0:
            logger.warning("\n⚠️ Offene Position am Ende des Backtests!")
        
        logger.info("\n" + "=" * 70)
        logger.info("✓ Backtest abgeschlossen")
        logger.info("=" * 70 + "\n")
    
    def save_results(self, filepath: str = "data/backtest_results.csv"):
        """
        Speichere Backtest-Ergebnisse
        
        Args:
            filepath: Pfad zur Ziel-Datei
        """
        if not self.trades:
            logger.warning("Keine Trades zum Speichern")
            return
        
        df = pd.DataFrame(self.trades)
        df.to_csv(filepath, index=False, encoding='utf-8')
        logger.info(f"✓ Backtest-Ergebnisse gespeichert: {filepath}")
    
    def visualize_results(self, output_dir: str = "data", use_plotly: bool = False):
        """
        Generate visualizations of backtest results
        
        Args:
            output_dir: Directory to save visualizations
            use_plotly: Use Plotly instead of Matplotlib
        
        Returns:
            Dictionary with paths to generated charts
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info("\n" + "=" * 70)
        logger.info("📊 GENERATING VISUALIZATIONS")
        logger.info("=" * 70)
        
        charts = {}
        ext = '.html' if use_plotly else '.png'
        
        # 1. Equity Curve
        if self.equity_curve:
            equity_file = os.path.join(output_dir, f"equity_curve{ext}")
            result = generate_equity_curve_chart(
                self.equity_curve, 
                equity_file, 
                use_plotly=use_plotly,
                title="Equity Curve - Backtest Results"
            )
            if result:
                charts['equity_curve'] = result
        
        # 2. Drawdown Chart
        if self.equity_curve:
            drawdown_file = os.path.join(output_dir, f"drawdown{ext}")
            result = generate_drawdown_chart(
                self.equity_curve,
                drawdown_file,
                use_plotly=use_plotly,
                title="Drawdown - Backtest Results"
            )
            if result:
                charts['drawdown'] = result
        
        # 3. P&L Distribution
        if self.trades:
            pnl_file = os.path.join(output_dir, f"pnl_distribution{ext}")
            result = generate_pnl_distribution_chart(
                self.trades,
                pnl_file,
                use_plotly=use_plotly,
                title="P&L Distribution - Per Trade"
            )
            if result:
                charts['pnl_distribution'] = result
        
        logger.info(f"✓ Generated {len(charts)} visualization(s)")
        logger.info("=" * 70 + "\n")
        
        return charts


def main():
    """Hauptfunktion für Backtest"""
    print("=" * 70)
    print("📈 TRADING STRATEGY BACKTESTER")
    print("=" * 70)
    print()
    
    # Wähle Datenquelle
    print("Datenquelle wählen:")
    print("  [1] CSV-Datei laden")
    print("  [2] Simulierte Daten generieren")
    print()
    
    choice = input("Wahl (1/2): ").strip()
    
    try:
        backtester = Backtester()
        
        if choice == "1":
            # CSV laden
            default_path = config.backtest_data_file
            filepath = input(f"Pfad zur CSV [{default_path}]: ").strip() or default_path
            data = backtester.load_data(filepath)
        
        elif choice == "2":
            # Simulierte Daten
            n_bars = input("Anzahl Kerzen [1000]: ").strip() or "1000"
            n_bars = int(n_bars)
            
            logger.info(f"Generiere {n_bars} simulierte Kerzen...")
            data = generate_sample_data(n_bars=n_bars, start_price=30000)
            logger.info("✓ Daten generiert\n")
        
        else:
            print("❌ Ungültige Wahl")
            sys.exit(1)
        
        # Führe Backtest durch
        backtester.run(data)
        
        # Speichern?
        save = input("\nErgebnisse speichern? (j/n): ").strip().lower()
        if save == 'j':
            backtester.save_results()
    
    except KeyboardInterrupt:
        print("\n\n⏹️ Backtest abgebrochen")
        sys.exit(0)
    except Exception as e:
        if logger:
            logger.error(f"❌ Fehler: {e}", exc_info=True)
        else:
            print(f"❌ Fehler: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
