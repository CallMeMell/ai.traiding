"""
strategy_selector.py - Automatische Strategie-Auswahl
======================================================

Analysiert alle verfügbaren Strategien mittels Backtest und wählt
die beste Strategie basierend auf robusten Metriken aus.

Berücksichtigt:
- ROI (Return on Investment)
- Sharpe Ratio (Risk-adjusted returns)
- Calmar Ratio (Return/Max Drawdown)
- Maximum Drawdown
- Win Rate
- Anzahl der Trades (Mindestanzahl für Robustheit)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
import logging

from batch_backtester import BatchBacktester
from strategy import (
    MACrossoverStrategy,
    RSIStrategy,
    BollingerBandsStrategy,
    EMACrossoverStrategy
)
from golden_cross_strategy import GoldenCrossStrategy
from utils import setup_logging, generate_sample_data, validate_ohlcv_data

logger = None


@dataclass
class StrategyScore:
    """Score und Metriken für eine Strategie"""
    name: str
    score: float
    roi: float
    sharpe_ratio: float
    calmar_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    avg_trade: float
    final_capital: float
    metrics: Dict[str, Any]


class StrategySelector:
    """
    Automatische Auswahl der optimalen Trading-Strategie
    
    Führt Backtest für alle Strategien durch und wählt die
    beste basierend auf einem robusten Scoring-System.
    """
    
    def __init__(self, 
                 initial_capital: float = 10000.0,
                 trade_size: float = 100.0,
                 min_trades: int = 10,
                 weights: Optional[Dict[str, float]] = None):
        """
        Args:
            initial_capital: Startkapital für Backtest
            trade_size: Handelsgröße
            min_trades: Mindestanzahl Trades für Robustheit
            weights: Gewichtung der Metriken im Score (optional)
        """
        global logger
        logger = setup_logging(log_level="INFO")
        
        self.initial_capital = initial_capital
        self.trade_size = trade_size
        self.min_trades = min_trades
        
        # Standard-Gewichtung der Metriken
        self.weights = weights or {
            'roi': 0.30,           # 30% - Wichtigste Metrik
            'sharpe_ratio': 0.25,  # 25% - Risk-adjusted returns
            'calmar_ratio': 0.20,  # 20% - Return/Drawdown
            'win_rate': 0.15,      # 15% - Erfolgsquote
            'max_drawdown': 0.10   # 10% - Risiko (invertiert)
        }
        
        self.results: Dict[str, StrategyScore] = {}
        self.backtester = BatchBacktester(initial_capital, trade_size)
    
    def setup_strategies(self) -> Dict[str, Any]:
        """
        Erstelle alle verfügbaren Strategien mit optimierten Parametern
        
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
            
            'MA Crossover (10/30)': MACrossoverStrategy({
                'short_window': 10,
                'long_window': 30
            }),
            
            'RSI Mean Reversion': RSIStrategy({
                'window': 14,
                'oversold_threshold': 35,
                'overbought_threshold': 65
            }),
            
            'RSI Conservative': RSIStrategy({
                'window': 14,
                'oversold_threshold': 30,
                'overbought_threshold': 70
            }),
            
            'EMA Crossover (9/21)': EMACrossoverStrategy({
                'short_window': 9,
                'long_window': 21
            }),
            
            'EMA Crossover (12/26)': EMACrossoverStrategy({
                'short_window': 12,
                'long_window': 26
            }),
            
            'Bollinger Bands': BollingerBandsStrategy({
                'window': 20,
                'std_dev': 2.0
            }),
            
            'Bollinger Bands Wide': BollingerBandsStrategy({
                'window': 20,
                'std_dev': 2.5
            })
        }
        
        logger.info(f"✓ {len(strategies)} Strategien geladen für Auswahl")
        return strategies
    
    def calculate_score(self, metrics: Dict[str, float]) -> float:
        """
        Berechne gewichteten Score für eine Strategie
        
        Args:
            metrics: Performance-Metriken der Strategie
        
        Returns:
            Gewichteter Score (0-100)
        """
        # Normalisiere Metriken (0-100 Skala)
        
        # ROI: 0-100% -> 0-100 Punkte
        roi_score = min(max(metrics['roi'], -50), 100)
        
        # Sharpe Ratio: 0-3 -> 0-100 Punkte (>3 ist exzellent)
        sharpe_score = min(max(metrics['sharpe_ratio'] / 3.0 * 100, 0), 100)
        
        # Calmar Ratio: 0-3 -> 0-100 Punkte
        calmar_score = min(max(metrics.get('calmar_ratio', 0) / 3.0 * 100, 0), 100)
        
        # Win Rate: 0-100% direkt übernehmen
        win_rate_score = metrics['win_rate']
        
        # Max Drawdown: Invertiert (weniger ist besser)
        # -50% DD = 0 Punkte, 0% DD = 100 Punkte
        max_dd = abs(metrics['max_drawdown'])
        drawdown_score = max(100 - (max_dd / 50.0 * 100), 0)
        
        # Gewichteter Score
        score = (
            roi_score * self.weights['roi'] +
            sharpe_score * self.weights['sharpe_ratio'] +
            calmar_score * self.weights['calmar_ratio'] +
            win_rate_score * self.weights['win_rate'] +
            drawdown_score * self.weights['max_drawdown']
        )
        
        return round(score, 2)
    
    def run_selection(self, data: pd.DataFrame) -> Tuple[str, StrategyScore]:
        """
        Führe Strategie-Auswahl durch
        
        Args:
            data: OHLCV DataFrame für Backtest
        
        Returns:
            Tuple von (strategy_name, StrategyScore)
        """
        logger.info("\n" + "=" * 70)
        logger.info("🎯 AUTOMATISCHE STRATEGIE-AUSWAHL")
        logger.info("=" * 70)
        logger.info(f"Datenpunkte: {len(data)}")
        if 'timestamp' in data.columns:
            logger.info(f"Periode: {data['timestamp'].iloc[0]} bis {data['timestamp'].iloc[-1]}")
        logger.info(f"Mindestanzahl Trades: {self.min_trades}")
        logger.info("=" * 70)
        
        # Setup und add Strategien
        strategies = self.setup_strategies()
        for name, strategy in strategies.items():
            self.backtester.add_strategy(name, strategy)
        
        # Run batch backtest
        self.backtester.run_batch(data)
        
        # Analyse und Score-Berechnung
        logger.info("\n" + "=" * 70)
        logger.info("📊 STRATEGIE-RANKING")
        logger.info("=" * 70)
        
        for name, result in self.backtester.results.items():
            metrics = result['metrics']
            
            # Skip bei Fehler
            if 'error' in metrics:
                logger.warning(f"⚠️  {name}: {metrics['error']}")
                continue
            
            # Skip bei zu wenigen Trades
            if metrics['total_trades'] < self.min_trades:
                logger.warning(f"⚠️  {name}: Nur {metrics['total_trades']} Trades (min: {self.min_trades})")
                continue
            
            # Berechne Calmar Ratio falls nicht vorhanden
            if 'calmar_ratio' not in metrics or metrics['calmar_ratio'] == 0:
                total_return = metrics['roi']
                max_dd = abs(metrics['max_drawdown'])
                if max_dd > 0:
                    metrics['calmar_ratio'] = total_return / max_dd
                else:
                    metrics['calmar_ratio'] = 0
            
            # Berechne Score
            score = self.calculate_score(metrics)
            
            # Speichere Ergebnis
            self.results[name] = StrategyScore(
                name=name,
                score=score,
                roi=metrics['roi'],
                sharpe_ratio=metrics['sharpe_ratio'],
                calmar_ratio=metrics.get('calmar_ratio', 0),
                max_drawdown=metrics['max_drawdown'],
                win_rate=metrics['win_rate'],
                total_trades=metrics['total_trades'],
                avg_trade=metrics['avg_trade'],
                final_capital=metrics['final_capital'],
                metrics=metrics
            )
        
        # Ranking
        if not self.results:
            logger.error("❌ Keine Strategien erfüllen die Mindestanforderungen")
            raise ValueError("Keine gültigen Strategien gefunden")
        
        sorted_results = sorted(
            self.results.items(),
            key=lambda x: x[1].score,
            reverse=True
        )
        
        # Drucke Ranking
        self._print_ranking(sorted_results)
        
        # Beste Strategie
        best_name, best_score = sorted_results[0]
        
        logger.info("\n" + "=" * 70)
        logger.info("🏆 EMPFOHLENE STRATEGIE")
        logger.info("=" * 70)
        logger.info(f"✓ {best_name}")
        logger.info(f"  Score:        {best_score.score:.2f}/100")
        logger.info(f"  ROI:          {best_score.roi:+.2f}%")
        logger.info(f"  Sharpe:       {best_score.sharpe_ratio:.2f}")
        logger.info(f"  Calmar:       {best_score.calmar_ratio:.2f}")
        logger.info(f"  Max DD:       {best_score.max_drawdown:.2f}%")
        logger.info(f"  Win Rate:     {best_score.win_rate:.1f}%")
        logger.info(f"  Total Trades: {best_score.total_trades}")
        logger.info("=" * 70)
        
        return best_name, best_score
    
    def _print_ranking(self, sorted_results: List[Tuple[str, StrategyScore]]):
        """Drucke detailliertes Ranking"""
        
        print(f"\n{'Rank':<6}{'Strategy':<30}{'Score':<10}{'ROI':<12}{'Sharpe':<10}{'Win Rate':<12}")
        print("-" * 80)
        
        for rank, (name, result) in enumerate(sorted_results, 1):
            emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
            
            print(f"{emoji} #{rank:<3}{name:<30}"
                  f"{result.score:>6.2f}    "
                  f"{result.roi:>+9.2f}%  "
                  f"{result.sharpe_ratio:>7.2f}  "
                  f"{result.win_rate:>9.1f}%")
        
        print("-" * 80)
        
        # Details Top 3
        logger.info("\n📋 TOP 3 DETAILS:")
        for rank, (name, result) in enumerate(sorted_results[:3], 1):
            logger.info(f"\n{rank}. {name} (Score: {result.score:.2f})")
            logger.info(f"   ROI:          {result.roi:+.2f}%")
            logger.info(f"   Sharpe:       {result.sharpe_ratio:.2f}")
            logger.info(f"   Calmar:       {result.calmar_ratio:.2f}")
            logger.info(f"   Max DD:       {result.max_drawdown:.2f}%")
            logger.info(f"   Win Rate:     {result.win_rate:.1f}%")
            logger.info(f"   Avg Trade:    ${result.avg_trade:+.2f}")
            logger.info(f"   Total Trades: {result.total_trades}")
    
    def export_ranking(self, filepath: str = "data/strategy_ranking.csv"):
        """
        Exportiere Ranking als CSV
        
        Args:
            filepath: Ziel-Datei
        """
        if not self.results:
            logger.warning("Keine Ergebnisse zum Exportieren")
            return
        
        # Konvertiere zu Liste
        data = []
        for name, result in self.results.items():
            data.append({
                'strategy_name': name,
                'score': result.score,
                'roi': result.roi,
                'sharpe_ratio': result.sharpe_ratio,
                'calmar_ratio': result.calmar_ratio,
                'max_drawdown': result.max_drawdown,
                'win_rate': result.win_rate,
                'total_trades': result.total_trades,
                'avg_trade': result.avg_trade,
                'final_capital': result.final_capital
            })
        
        df = pd.DataFrame(data)
        df = df.sort_values('score', ascending=False)
        df.to_csv(filepath, index=False)
        
        logger.info(f"✓ Ranking exportiert: {filepath}")


def main():
    """Hauptfunktion für Kommandozeilen-Nutzung"""
    print("\n" + "=" * 70)
    print("  🎯 AUTOMATISCHE STRATEGIE-AUSWAHL")
    print("=" * 70)
    print("\nAnalysiert alle Strategien und empfiehlt die beste\n")
    
    # Datenquelle wählen
    print("Datenquelle wählen:")
    print("  [1] Simulierte Daten (1000 Kerzen)")
    print("  [2] Simulierte Daten (2000 Kerzen)")
    print("  [3] CSV-Datei laden")
    print()
    
    choice = input("Wahl (1-3): ").strip()
    
    # Lade Daten
    try:
        if choice == "1":
            data = generate_sample_data(n_bars=1000, start_price=30000)
            logger.info("✓ Simulierte Daten generiert (1000 Kerzen)")
        elif choice == "2":
            data = generate_sample_data(n_bars=2000, start_price=30000)
            logger.info("✓ Simulierte Daten generiert (2000 Kerzen)")
        elif choice == "3":
            filepath = input("Pfad zur CSV: ").strip()
            data = pd.read_csv(filepath)
            if 'timestamp' in data.columns:
                data['timestamp'] = pd.to_datetime(data['timestamp'])
            logger.info(f"✓ Daten geladen: {len(data)} Kerzen")
        else:
            print("❌ Ungültige Wahl")
            return
        
        # Validiere Daten
        is_valid, error = validate_ohlcv_data(data)
        if not is_valid:
            print(f"❌ Ungültige Daten: {error}")
            return
        
        # Parameter
        capital_input = input("\nInitial Capital ($) [10000]: ").strip() or "10000"
        capital = float(capital_input)
        
        trade_size_input = input("Trade Size [100]: ").strip() or "100"
        trade_size = float(trade_size_input)
        
        min_trades_input = input("Mindestanzahl Trades [10]: ").strip() or "10"
        min_trades = int(min_trades_input)
        
        # Erstelle Selector
        selector = StrategySelector(
            initial_capital=capital,
            trade_size=trade_size,
            min_trades=min_trades
        )
        
        # Führe Auswahl durch
        best_name, best_score = selector.run_selection(data)
        
        # Export?
        export = input("\nRanking als CSV exportieren? (j/n): ").strip().lower()
        if export == 'j':
            selector.export_ranking()
        
        print("\n✓ Strategie-Auswahl abgeschlossen!\n")
        print(f"🏆 Empfohlen: {best_name}")
        print(f"   Score: {best_score.score:.2f}/100\n")
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Abgebrochen")
    except Exception as e:
        logger.error(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
