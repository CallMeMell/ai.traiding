"""
demo_strategy_core.py - Demo der Reversal-Trailing-Stop Strategie
===================================================================
Zeigt die Integration der Kernstrategie mit simulierten Daten
"""
import sys
import pandas as pd
import numpy as np
from strategy_core import ReversalTrailingStopStrategy


def generate_trending_market(n_bars: int = 500) -> pd.DataFrame:
    """
    Generiert einen trendenden Markt mit Volatilität
    
    Args:
        n_bars: Anzahl der Kerzen
    
    Returns:
        DataFrame mit OHLCV-Daten
    """
    dates = pd.date_range(end=pd.Timestamp.now(), periods=n_bars, freq='15min')
    
    # Simuliere einen Aufwärtstrend mit Pullbacks
    np.random.seed(42)
    price = 30000
    prices = [price]
    
    trend_strength = 0.5  # Aufwärts-Bias
    
    for i in range(n_bars - 1):
        # Trend + Noise
        trend = trend_strength * (1 + np.sin(i / 50) * 0.5)
        noise = np.random.normal(0, 100)
        
        price += trend + noise
        price = max(price, 1000)
        prices.append(price)
    
    prices = np.array(prices)
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': prices + np.random.normal(0, 50, n_bars),
        'high': prices + abs(np.random.normal(50, 30, n_bars)),
        'low': prices - abs(np.random.normal(50, 30, n_bars)),
        'close': prices,
        'volume': np.random.uniform(100, 1000, n_bars)
    })
    
    return df


def run_demo():
    """Führt Demo-Backtest durch"""
    print("=" * 70)
    print("🔄 REVERSAL-TRAILING-STOP STRATEGIE - DEMO")
    print("=" * 70)
    print()
    
    # Erstelle Strategie mit optimierten Parametern
    strategy = ReversalTrailingStopStrategy({
        'lookback_period': 20,
        'trailing_stop_pct': 2.5,
        'take_profit_pct': 6.0,
        'reversal_threshold': 0.5,
        'atr_multiplier': 2.5
    })
    
    print(f"✓ Strategie: {strategy.name}")
    print(f"✓ Parameter:")
    for key, value in strategy.params.items():
        print(f"  - {key}: {value}")
    print()
    
    # Generiere Test-Daten
    print("📊 Generiere Markt-Daten...")
    data = generate_trending_market(n_bars=500)
    print(f"✓ {len(data)} Kerzen generiert")
    print(f"✓ Start-Preis: ${data.iloc[0]['close']:.2f}")
    print(f"✓ End-Preis: ${data.iloc[-1]['close']:.2f}")
    print(f"✓ Markt-Return: {((data.iloc[-1]['close'] / data.iloc[0]['close']) - 1) * 100:.2f}%")
    print()
    
    # Simuliere Trading
    print("🚀 Starte Backtesting...")
    print("-" * 70)
    
    results = []
    position = 0
    entry_price = 0
    trades_count = 0
    
    # Start nach Warmup-Periode
    warmup = strategy.params['lookback_period'] + 20
    
    for i in range(warmup, len(data)):
        window = data.iloc[:i+1]
        signal = strategy.generate_signal(window)
        
        current_price = window.iloc[-1]['close']
        timestamp = window.iloc[-1]['timestamp']
        
        # Trade-Logik
        if signal != 0 and signal != position:
            if position != 0:
                # Close existing position
                pnl = (current_price - entry_price) * position
                pnl_pct = (pnl / entry_price) * 100
                
                results.append({
                    'entry': entry_price,
                    'exit': current_price,
                    'side': 'LONG' if position == 1 else 'SHORT',
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'timestamp': timestamp
                })
                
                emoji = "✅" if pnl > 0 else "❌"
                side_emoji = "📈" if position == 1 else "📉"
                print(f"{emoji} {side_emoji} EXIT @ ${current_price:.2f} | P&L: ${pnl:+.2f} ({pnl_pct:+.2f}%)")
            
            # Open new position
            if signal != 0:
                position = signal
                entry_price = current_price
                trades_count += 1
                side_emoji = "📈" if signal == 1 else "📉"
                print(f"🔔 {side_emoji} ENTRY #{trades_count} @ ${entry_price:.2f}")
    
    # Close final position if open
    if position != 0:
        current_price = data.iloc[-1]['close']
        pnl = (current_price - entry_price) * position
        pnl_pct = (pnl / entry_price) * 100
        
        results.append({
            'entry': entry_price,
            'exit': current_price,
            'side': 'LONG' if position == 1 else 'SHORT',
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'timestamp': data.iloc[-1]['timestamp']
        })
        
        emoji = "✅" if pnl > 0 else "❌"
        side_emoji = "📈" if position == 1 else "📉"
        print(f"{emoji} {side_emoji} FINAL EXIT @ ${current_price:.2f} | P&L: ${pnl:+.2f} ({pnl_pct:+.2f}%)")
    
    print("-" * 70)
    print()
    
    # Statistiken
    if results:
        total_trades = len(results)
        winning_trades = [r for r in results if r['pnl'] > 0]
        losing_trades = [r for r in results if r['pnl'] <= 0]
        
        total_pnl = sum(r['pnl'] for r in results)
        avg_win = sum(r['pnl'] for r in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(r['pnl'] for r in losing_trades) / len(losing_trades) if losing_trades else 0
        win_rate = len(winning_trades) / total_trades * 100
        
        best_trade = max(results, key=lambda x: x['pnl'])
        worst_trade = min(results, key=lambda x: x['pnl'])
        
        print("=" * 70)
        print("📊 BACKTEST ERGEBNISSE")
        print("=" * 70)
        print()
        print("💰 PERFORMANCE:")
        print(f"  Total Trades:     {total_trades}")
        print(f"  Winning Trades:   {len(winning_trades)} ({win_rate:.1f}%)")
        print(f"  Losing Trades:    {len(losing_trades)} ({100-win_rate:.1f}%)")
        print()
        print(f"  Total P&L:        ${total_pnl:+,.2f}")
        print(f"  Average Win:      ${avg_win:+,.2f}")
        print(f"  Average Loss:     ${avg_loss:+,.2f}")
        print()
        print(f"  Best Trade:       ${best_trade['pnl']:+,.2f} ({best_trade['pnl_pct']:+.2f}%)")
        print(f"  Worst Trade:      ${worst_trade['pnl']:+,.2f} ({worst_trade['pnl_pct']:+.2f}%)")
        print()
        
        # Profit Factor
        gross_profit = sum(r['pnl'] for r in winning_trades) if winning_trades else 0
        gross_loss = abs(sum(r['pnl'] for r in losing_trades)) if losing_trades else 1
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        print(f"  Profit Factor:    {profit_factor:.2f}")
        print()
        
        # Consecutive Wins/Losses
        max_win_streak = 0
        max_loss_streak = 0
        current_win_streak = 0
        current_loss_streak = 0
        
        for r in results:
            if r['pnl'] > 0:
                current_win_streak += 1
                current_loss_streak = 0
                max_win_streak = max(max_win_streak, current_win_streak)
            else:
                current_loss_streak += 1
                current_win_streak = 0
                max_loss_streak = max(max_loss_streak, current_loss_streak)
        
        print(f"  Max Win Streak:   {max_win_streak}")
        print(f"  Max Loss Streak:  {max_loss_streak}")
        print()
        print("=" * 70)
        print()
        print("✨ ZUSAMMENFASSUNG:")
        
        if total_pnl > 0:
            print(f"  ✅ Profitable Strategie mit ${total_pnl:,.2f} Gewinn")
        else:
            print(f"  ⚠️ Verlust-Strategie mit ${total_pnl:,.2f} Verlust")
        
        if win_rate > 50:
            print(f"  ✅ Gute Win-Rate von {win_rate:.1f}%")
        else:
            print(f"  ⚠️ Niedrige Win-Rate von {win_rate:.1f}%")
        
        if profit_factor > 1.5:
            print(f"  ✅ Starker Profit-Factor von {profit_factor:.2f}")
        elif profit_factor > 1.0:
            print(f"  ⚠️ Moderater Profit-Factor von {profit_factor:.2f}")
        else:
            print(f"  ❌ Schwacher Profit-Factor von {profit_factor:.2f}")
        
        print()
        print("=" * 70)
        
    else:
        print("⚠️ Keine Trades ausgeführt")
        print("Tipp: Versuche andere Parameter oder mehr Daten")
        print()


if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo abgebrochen")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
