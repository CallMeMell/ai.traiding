"""
auto_select_strategy.py - Automated Strategy Selection Script
==============================================================

Automatisch die beste Trading-Strategie auswählen und in der
Live-Konfiguration setzen. Kann als Standalone-Tool oder als
Teil eines Cron-Jobs verwendet werden.

Usage:
    python scripts/auto_select_strategy.py [--data-file PATH] [--min-trades N]
    
    Optionen:
    --data-file PATH     CSV-Datei mit historischen OHLCV-Daten (optional)
    --min-trades N       Mindestanzahl Trades (default: 10)
    --initial-capital N  Startkapital für Backtest (default: 10000)
    --trade-size N       Handelsgröße (default: 100)
    --export-csv PATH    Export Ranking als CSV (default: data/strategy_ranking.csv)
    --no-update-config   Strategie nicht automatisch in config schreiben
    --quiet              Weniger Ausgaben
"""

import sys
import os
import argparse
import yaml
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategy_selector import StrategySelector
from utils import generate_sample_data, validate_ohlcv_data
import pandas as pd


def setup_logging(quiet: bool = False):
    """Setup logging für das Script"""
    level = logging.WARNING if quiet else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


def load_data(data_file: str = None, quiet: bool = False) -> pd.DataFrame:
    """
    Lade Daten für Backtest
    
    Args:
        data_file: Pfad zu CSV-Datei (optional)
        quiet: Weniger Ausgaben
    
    Returns:
        DataFrame mit OHLCV-Daten
    """
    if data_file and os.path.exists(data_file):
        if not quiet:
            print(f"📁 Lade Daten aus: {data_file}")
        
        data = pd.read_csv(data_file)
        
        # Konvertiere timestamp falls vorhanden
        if 'timestamp' in data.columns:
            data['timestamp'] = pd.to_datetime(data['timestamp'])
        
        # Validiere Daten
        is_valid, error = validate_ohlcv_data(data)
        if not is_valid:
            raise ValueError(f"Ungültige OHLCV-Daten: {error}")
        
        if not quiet:
            print(f"✓ {len(data)} Datenpunkte geladen")
        
        return data
    else:
        if not quiet:
            print("🔢 Generiere simulierte Marktdaten...")
        
        data = generate_sample_data(n_bars=2000, start_price=30000)
        
        if not quiet:
            print(f"✓ {len(data)} Datenpunkte generiert")
        
        return data


def update_config_strategy(strategy_name: str, config_path: str = "config/live_risk.yaml") -> bool:
    """
    Aktualisiere Strategie in config/live_risk.yaml
    
    Args:
        strategy_name: Name der Strategie
        config_path: Pfad zur Config-Datei
    
    Returns:
        True wenn erfolgreich
    """
    try:
        # Erstelle config directory falls nicht vorhanden
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # Lade existierende Config oder erstelle neue
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f) or {}
        else:
            # Erstelle Default-Config
            config = {
                'pairs': 'BTCUSDT',
                'max_risk_per_trade': 0.005,
                'daily_loss_limit': 0.01,
                'max_open_exposure': 0.05,
                'allowed_order_types': 'LIMIT_ONLY',
                'max_slippage': 0.003
            }
        
        # Aktualisiere Strategie
        config['strategy'] = strategy_name
        
        # Schreibe zurück
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        print(f"✅ Strategie in {config_path} aktualisiert: {strategy_name}")
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Aktualisieren der Config: {e}")
        return False


def main():
    """Hauptfunktion"""
    parser = argparse.ArgumentParser(
        description='Automatische Strategie-Auswahl für Live-Trading',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  # Mit generierten Daten
  python scripts/auto_select_strategy.py
  
  # Mit CSV-Datei
  python scripts/auto_select_strategy.py --data-file data/historical_btc.csv
  
  # Mit benutzerdefinierten Parametern
  python scripts/auto_select_strategy.py --min-trades 15 --initial-capital 50000
  
  # Ohne Config-Update (nur Analyse)
  python scripts/auto_select_strategy.py --no-update-config
        """
    )
    
    parser.add_argument('--data-file', type=str, default=None,
                        help='CSV-Datei mit historischen OHLCV-Daten')
    parser.add_argument('--min-trades', type=int, default=10,
                        help='Mindestanzahl Trades (default: 10)')
    parser.add_argument('--initial-capital', type=float, default=10000.0,
                        help='Startkapital für Backtest (default: 10000)')
    parser.add_argument('--trade-size', type=float, default=100.0,
                        help='Handelsgröße (default: 100)')
    parser.add_argument('--export-csv', type=str, default='data/strategy_ranking.csv',
                        help='Export Ranking als CSV (default: data/strategy_ranking.csv)')
    parser.add_argument('--no-update-config', action='store_true',
                        help='Strategie nicht automatisch in config schreiben')
    parser.add_argument('--quiet', action='store_true',
                        help='Weniger Ausgaben')
    
    args = parser.parse_args()
    
    # Setup Logging
    logger = setup_logging(args.quiet)
    
    try:
        if not args.quiet:
            print()
            print("=" * 70)
            print("🎯 AUTOMATISCHE STRATEGIE-AUSWAHL")
            print("=" * 70)
            print()
        
        # Lade Daten
        data = load_data(args.data_file, args.quiet)
        
        # Erstelle Selector
        if not args.quiet:
            print()
            print(f"⚙️  Parameter:")
            print(f"   Initial Capital: ${args.initial_capital:,.2f}")
            print(f"   Trade Size: {args.trade_size}")
            print(f"   Min Trades: {args.min_trades}")
            print()
        
        selector = StrategySelector(
            initial_capital=args.initial_capital,
            trade_size=args.trade_size,
            min_trades=args.min_trades
        )
        
        # Führe Auswahl durch
        if not args.quiet:
            print("🔍 Analysiere Strategien...")
            print()
        
        best_name, best_score = selector.run_selection(data)
        
        # Export Ranking
        if args.export_csv:
            selector.export_ranking(args.export_csv)
        
        # Aktualisiere Config
        if not args.no_update_config:
            if not args.quiet:
                print()
            
            success = update_config_strategy(best_name)
            
            if not success:
                logger.warning("Config konnte nicht aktualisiert werden")
                return 1
        
        # Zusammenfassung
        if not args.quiet:
            print()
            print("=" * 70)
            print("✅ STRATEGIE-AUSWAHL ABGESCHLOSSEN")
            print("=" * 70)
            print()
            print(f"🏆 Empfohlene Strategie: {best_name}")
            print(f"   Score:        {best_score.score:.2f}/100")
            print(f"   ROI:          {best_score.roi:+.2f}%")
            print(f"   Sharpe Ratio: {best_score.sharpe_ratio:.2f}")
            print(f"   Calmar Ratio: {best_score.calmar_ratio:.2f}")
            print(f"   Max Drawdown: {best_score.max_drawdown:.2f}%")
            print(f"   Win Rate:     {best_score.win_rate:.1f}%")
            print(f"   Total Trades: {best_score.total_trades}")
            print()
            
            if not args.no_update_config:
                print(f"📝 Konfiguration aktualisiert: config/live_risk.yaml")
            
            if args.export_csv:
                print(f"📊 Ranking exportiert: {args.export_csv}")
            
            print()
            print("=" * 70)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Abgebrochen durch Benutzer")
        return 130
        
    except Exception as e:
        logger.error(f"Fehler bei Strategie-Auswahl: {e}")
        if not args.quiet:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
