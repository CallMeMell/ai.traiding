"""
strategy_comparison.py - Vergleiche verschiedene Trading-Strategien
===================================================================

Vergleicht:
- Golden Cross (50/200)
- MA Crossover (20/50)
- RSI
- EMA Crossover
- Bollinger Bands

Mit den gleichen historischen Daten!
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any
import logging

# Import Strategien
from strategy import (
    MACrossoverStrategy,
    RSIStrategy,
    BollingerBandsStrategy,
    EMACrossoverStrategy
)
from golden_cross_strategy import GoldenCrossStrategy
from utils import generate_sample_data, setup_logging

logger = setup_logging(log_level="INFO")


class StrategyComparator:
    """
    Vergleicht verschiedene Trading-Strategien
    
    Führt Backtest für alle Strategien mit gleichen Daten durch
    und vergleicht Performance-Metriken.
    """
    
    def __init__(self, initial_capital: float = 10000.0):
        """
        Args:
            initial_capital: Startkapital für alle Strategien
        """
        self.initial_capital = initial_capital
        self.results: Dict[str, Dict[str, Any]] = {}
        
        logger.info("=" * 70)
        logger.info("📊 STRATEGY COMPARISON TOOL")
        logger.info("=" * 70)
        logger.info(f"Initial Capital: ${initial_capital:,.2f}")
    
    def setup_strategies(self) -> Dict[str, Any]:
        """
        Erstelle alle Strategien mit Standard-Parametern
        
        Returns:
            Dictionary mit Strategie-Instanzen
        """
        strategies = {
            'Golden Cross (50/200)': GoldenCrossStrategy({
                'short_window': 50,
                'long_window': 200,
                'confirmation_days': 3,
                'volume_confirmation': True,
                'trend_strength_filter': True
            }),
            
            'MA Crossover (20/50)': MACrossoverStrategy({
                'short_window': 20,
                'long_window': 50
            }),
            
            'RSI Mean Reversion': RSIStrategy({
                'window': 14,
                'oversold_threshold': 35,
                'overbought_threshold': 65
            }),
            
            'EMA Crossover (9/21)': EMACrossoverStrategy({
                'short_window': 9,
                'long_window': 21
            }),
            
            'Bollinger Bands': BollingerBandsStrategy({
                'window': 20,
                'std_dev': 2.0
            })
        }
        
        logger.info(f"\n✓ {len(strategies)} Strategien geladen")
        return strategies
    
    def backtest_strategy(self, strategy: Any, df: pd.DataFrame, 
                         strategy_name: str, trade_size: float = 100.0) -> Dict[str, Any]:
        """
        Führe Backtest für eine Strategie durch
        
        Args:
            strategy: Strategie-Instanz
            df: OHLCV DataFrame
            strategy_name: Name der Strategie
            trade_size: Trade-Größe
        
        Returns:
            Dictionary mit Performance-Metriken
        """
        logger.info(f"\n🔄 Backtesting: {strategy_name}")
        
        capital = self.initial_capital
        position = 0
        entry_price = 0
        trades = []
        
        # Mindestanzahl für Indikatoren
        if hasattr(strategy, 'long_window'):
            min_bars = strategy.long_window + 10
        else:
            min_bars = 100
        
        # Durchlaufe Daten
        for i in range(min_bars, len(df)):
            df_slice = df.iloc[:i+1].copy()
            
            signal = strategy.generate_signal(df_slice)
            current_price = df_slice['close'].iloc[-1]
            
            # BUY
            if signal == 1 and position == 0:
                position = 1
                entry_price = current_price
                trades.append({
                    'type': 'BUY',
                    'price': current_price,
                    'capital_before': capital
                })
            
            # SELL
            elif signal == -1 and position == 1:
                pnl = (current_price - entry_price) * trade_size
                capital += pnl
                position = 0
                trades.append({
                    'type': 'SELL',
                    'price': current_price,
                    'pnl': pnl,
                    'capital_after': capital
                })
        
        # Berechne Metriken
        sell_trades = [t for t in trades if t['type'] == 'SELL']
        
        if not sell_trades:
            return {
                'strategy_name': strategy_name,
                'total_trades': 0,
                'total_pnl': 0,
                'roi': 0,
                'win_rate': 0,
                'best_trade': 0,
                'worst_trade': 0,
                'final_capital': capital
            }
        
        pnls = [t['pnl'] for t in sell_trades]
        total_pnl = sum(pnls)
        wins = [p for p in pnls if p > 0]
        
        metrics = {
            'strategy_name': strategy_name,
            'total_trades': len(sell_trades),
            'total_pnl': total_pnl,
            'roi': (total_pnl / self.initial_capital) * 100,
            'win_rate': (len(wins) / len(pnls)) * 100 if pnls else 0,
            'best_trade': max(pnls) if pnls else 0,
            'worst_trade': min(pnls) if pnls else 0,
            'avg_trade': total_pnl / len(pnls) if pnls else 0,
            'final_capital': capital
        }
        
        logger.info(f"  ✓ {len(sell_trades)} Trades | ROI: {metrics['roi']:.2f}%")
        
        return metrics
    
    def compare_all(self, df: pd.DataFrame, trade_size: float = 100.0):
        """
        Führe Vergleich aller Strategien durch
        
        Args:
            df: OHLCV DataFrame
            trade_size: Trade-Größe
        """
        logger.info("\n" + "=" * 70)
        logger.info("🚀 STARTE STRATEGY COMPARISON")
        logger.info("=" * 70)
        logger.info(f"Datenpunkte: {len(df)}")
        logger.info(f"Periode: {df['timestamp'].iloc[0]} bis {df['timestamp'].iloc[-1]}")
        
        # Setup Strategien
        strategies = self.setup_strategies()
        
        # Teste jede Strategie
        for name, strategy in strategies.items():
            try:
                result = self.backtest_strategy(strategy, df, name, trade_size)
                self.results[name] = result
            except Exception as e:
                logger.error(f"❌ Fehler bei {name}: {e}")
                self.results[name] = {
                    'strategy_name': name,
                    'error': str(e)
                }
        
        # Zeige Ergebnisse
        self._print_results()
    
    def _print_results(self):
        """Drucke detaillierte Ergebnisse"""
        
        logger.info("\n" + "=" * 70)
        logger.info("📊 COMPARISON RESULTS")
        logger.info("=" * 70)
        
        # Sortiere nach ROI
        sorted_results = sorted(
            [(name, res) for name, res in self.results.items() if 'error' not in res],
            key=lambda x: x[1]['roi'],
            reverse=True
        )
        
        # Tabellen-Header
        print(f"\n{'Rank':<6}{'Strategy':<30}{'Trades':<10}{'ROI':<12}{'Win Rate':<12}{'Avg Trade':<12}")
        print("-" * 82)
        
        # Zeige Ergebnisse
        for rank, (name, res) in enumerate(sorted_results, 1):
            emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
            
            print(f"{emoji} #{rank:<3}{name:<30}"
                  f"{res['total_trades']:<10}"
                  f"{res['roi']:>+10.2f}%  "
                  f"{res['win_rate']:>9.1f}%  "
                  f"${res['avg_trade']:>+9.2f}")
        
        print("-" * 82)
        
        # Details für Top-3
        logger.info("\n" + "=" * 70)
        logger.info("🏆 TOP 3 DETAILED RESULTS")
        logger.info("=" * 70)
        
        for rank, (name, res) in enumerate(sorted_results[:3], 1):
            logger.info(f"\n{rank}. {name}")
            logger.info(f"   Initial Capital:  ${self.initial_capital:,.2f}")
            logger.info(f"   Final Capital:    ${res['final_capital']:,.2f}")
            logger.info(f"   Total P&L:        ${res['total_pnl']:,.2f}")
            logger.info(f"   ROI:              {res['roi']:+.2f}%")
            logger.info(f"   Total Trades:     {res['total_trades']}")
            logger.info(f"   Win Rate:         {res['win_rate']:.1f}%")
            logger.info(f"   Best Trade:       ${res['best_trade']:,.2f}")
            logger.info(f"   Worst Trade:      ${res['worst_trade']:,.2f}")
            logger.info(f"   Avg Trade:        ${res['avg_trade']:,.2f}")
        
        # Fehler
        errors = [(name, res) for name, res in self.results.items() if 'error' in res]
        if errors:
            logger.info("\n⚠️ ERRORS:")
            for name, res in errors:
                logger.info(f"  - {name}: {res['error']}")
    
    def export_results(self, filepath: str = "data/strategy_comparison.csv"):
        """
        Exportiere Ergebnisse als CSV
        
        Args:
            filepath: Ziel-Datei
        """
        if not self.results:
            logger.warning("Keine Ergebnisse zum Exportieren")
            return
        
        # Konvertiere zu DataFrame
        results_list = []
        for name, res in self.results.items():
            if 'error' not in res:
                results_list.append(res)
        
        if not results_list:
            logger.warning("Keine erfolgreichen Ergebnisse")
            return
        
        df = pd.DataFrame(results_list)
        df = df.sort_values('roi', ascending=False)
        df.to_csv(filepath, index=False)
        
        logger.info(f"\n✓ Ergebnisse exportiert: {filepath}")


def main():
    """Hauptfunktion"""
    
    print("\n" + "=" * 70)
    print("  📊 STRATEGY COMPARISON TOOL")
    print("=" * 70)
    print("\nVergleicht alle Strategien mit den gleichen historischen Daten\n")
    
    # Optionen
    print("Datenquelle wählen:")
    print("  [1] Simulierte Daten (1000 Kerzen)")
    print("  [2] Simulierte Daten (2000 Kerzen)")
    print("  [3] CSV-Datei laden")
    print()
    
    choice = input("Wahl (1-3): ").strip()
    
    # Lade Daten
    if choice == "1":
        df = generate_sample_data(n_bars=1000, start_price=30000)
        logger.info("✓ Simulierte Daten generiert (1000 Kerzen)")
    elif choice == "2":
        df = generate_sample_data(n_bars=2000, start_price=30000)
        logger.info("✓ Simulierte Daten generiert (2000 Kerzen)")
    elif choice == "3":
        filepath = input("Pfad zur CSV: ").strip()
        df = pd.read_csv(filepath)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        logger.info(f"✓ Daten geladen: {len(df)} Kerzen")
    else:
        print("❌ Ungültige Wahl")
        return
    
    # Capital
    capital_input = input("\nInitial Capital ($) [10000]: ").strip() or "10000"
    capital = float(capital_input)
    
    # Trade Size
    trade_size_input = input("Trade Size [100]: ").strip() or "100"
    trade_size = float(trade_size_input)
    
    # Erstelle Comparator
    comparator = StrategyComparator(initial_capital=capital)
    
    # Führe Vergleich durch
    comparator.compare_all(df, trade_size=trade_size)
    
    # Export?
    export = input("\nErgebnisse als CSV exportieren? (j/n): ").strip().lower()
    if export == 'j':
        comparator.export_results()
    
    print("\n✓ Vergleich abgeschlossen!\n")


if __name__ == "__main__":
    main()
