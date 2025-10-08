"""
demo.py - Interaktive Demo des Trading-Systems
==============================================
Zeigt alle Features in einer geführten Demo
"""
import time
from config import config
from strategy import TradingStrategy
from utils import setup_logging, generate_sample_data, calculate_performance_metrics


def print_header(text):
    """Drucke formatierten Header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def demo_configuration():
    """Demonstriere Konfiguration"""
    print_header("📋 DEMO 1: Konfiguration")
    
    print("\nAktuelle Konfiguration:")
    print(f"  Trading Symbol:       {config.trading_symbol}")
    print(f"  Initial Capital:      ${config.initial_capital:,.2f}")
    print(f"  Trade Size:           ${config.trade_size:,.2f}")
    print(f"  Active Strategies:    {', '.join(config.active_strategies)}")
    print(f"  Cooperation Logic:    {config.cooperation_logic}")
    
    print("\nStrategie-Parameter:")
    for strategy_name, params in config.strategies.items():
        active = "✓" if strategy_name in config.active_strategies else " "
        print(f"  [{active}] {strategy_name}:")
        for param, value in params.items():
            print(f"      {param}: {value}")


def demo_strategies():
    """Demonstriere Strategie-System"""
    print_header("🎯 DEMO 2: Strategie-System")
    
    print("\nGeneriere Test-Daten...")
    df = generate_sample_data(n_bars=200)
    print(f"✓ {len(df)} Kerzen generiert")
    print(f"  Preisspanne: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
    
    print("\nInitialisiere Trading-Strategy...")
    strategy = TradingStrategy(config.to_dict())
    print("✓ Strategy initialisiert")
    
    print("\nAnalysiere letzte 5 Kerzen:")
    for i in range(-5, 0):
        df_slice = df.iloc[:len(df) + i].copy()
        analysis = strategy.analyze(df_slice)
        
        price = analysis['current_price']
        signal = analysis['signal_text']
        strategies_list = analysis['triggering_strategies']
        
        signal_emoji = {
            'BUY': '📈',
            'SELL': '📉',
            'HOLD': '⏸️'
        }.get(signal, '❓')
        
        print(f"\n  Kerze {i+5}: ${price:.2f}")
        print(f"  Signal:     {signal_emoji} {signal}")
        if strategies_list:
            print(f"  Strategien: {', '.join(strategies_list)}")


def demo_backtest():
    """Demonstriere Backtesting"""
    print_header("📊 DEMO 3: Backtesting")
    
    print("\nSimuliere Mini-Backtest mit 500 Kerzen...")
    
    # Setup
    df = generate_sample_data(n_bars=500)
    strategy = TradingStrategy(config.to_dict())
    
    capital = config.initial_capital
    initial_capital = capital
    position = 0
    entry_price = 0
    trades = []
    
    print("Führe Backtest durch...")
    
    # Backtest Loop
    for i in range(100, len(df)):
        df_slice = df.iloc[:i+1].copy()
        analysis = strategy.analyze(df_slice)
        
        signal = analysis['signal']
        current_price = analysis['current_price']
        
        # BUY
        if signal == 1 and position == 0:
            position = 1
            entry_price = current_price
            trades.append({
                'type': 'BUY',
                'price': current_price,
                'pnl': '0'
            })
        
        # SELL
        elif signal == -1 and position == 1:
            pnl = (current_price - entry_price) * config.trade_size
            capital += pnl
            position = 0
            trades.append({
                'type': 'SELL',
                'price': current_price,
                'pnl': str(pnl)
            })
    
    # Results
    print(f"\n✓ Backtest abgeschlossen\n")
    
    print("📈 ERGEBNISSE:")
    print(f"  Initial Capital:  ${initial_capital:,.2f}")
    print(f"  Final Capital:    ${capital:,.2f}")
    print(f"  Total P&L:        ${capital - initial_capital:,.2f}")
    print(f"  ROI:              {((capital - initial_capital) / initial_capital * 100):.2f}%")
    print(f"  Total Trades:     {len([t for t in trades if t['type'] == 'SELL'])}")
    
    # Performance Metrics
    metrics = calculate_performance_metrics(trades)
    if metrics['total_trades'] > 0:
        print(f"\n💹 PERFORMANCE:")
        print(f"  Win Rate:         {metrics['win_rate']:.1f}%")
        print(f"  Best Trade:       ${metrics['best_trade']:.2f}")
        print(f"  Worst Trade:      ${metrics['worst_trade']:.2f}")


def demo_cooperation_logic():
    """Demonstriere AND vs OR Logic"""
    print_header("🔗 DEMO 4: Cooperation Logic (AND vs OR)")
    
    print("\nGeneriere Test-Daten...")
    df = generate_sample_data(n_bars=200)
    
    # Teste beide Logiken
    for logic in ['AND', 'OR']:
        print(f"\n--- Testing {logic} Logic ---")
        
        # Update Config
        config.cooperation_logic = logic
        strategy = TradingStrategy(config.to_dict())
        
        # Analysiere
        analysis = strategy.analyze(df)
        signal = analysis['signal_text']
        strategies_list = analysis['triggering_strategies']
        
        print(f"Signal: {signal}")
        if strategies_list:
            print(f"Strategien die Signal gaben: {', '.join(strategies_list)}")
        else:
            print("Keine Strategien gaben Signal")
    
    print("\n💡 UNTERSCHIED:")
    print("  AND Logic: Alle aktiven Strategien müssen zustimmen")
    print("            → Weniger Signale, höhere Genauigkeit")
    print("  OR Logic:  Mindestens eine Strategie reicht")
    print("            → Mehr Signale, höhere Aktivität")


def demo_logging():
    """Demonstriere Logging"""
    print_header("📝 DEMO 5: Logging-System")
    
    print("\nInitialisiere Logger...")
    logger = setup_logging(
        log_level="INFO",
        log_file="logs/demo.log"
    )
    
    print("✓ Logger erstellt")
    print(f"  Log-Datei: logs/demo.log")
    print(f"  Log-Level: INFO")
    
    print("\nSchreibe Test-Nachrichten...")
    logger.info("Demo Info Message")
    logger.warning("Demo Warning Message")
    logger.error("Demo Error Message")
    
    print("✓ Nachrichten geschrieben")
    print("\nÖffne logs/demo.log um die Nachrichten zu sehen!")


def interactive_menu():
    """Interaktives Demo-Menü"""
    print("\n" + "=" * 70)
    print("  🎯 INTERACTIVE DEMO - Trading Bot Master Version")
    print("=" * 70)
    
    demos = [
        ("Konfiguration anzeigen", demo_configuration),
        ("Strategie-System testen", demo_strategies),
        ("Mini-Backtest durchführen", demo_backtest),
        ("AND vs OR Logic vergleichen", demo_cooperation_logic),
        ("Logging-System demonstrieren", demo_logging),
    ]
    
    while True:
        print("\n📋 Wähle eine Demo:")
        print("  [0] Alle Demos nacheinander")
        for i, (name, _) in enumerate(demos, 1):
            print(f"  [{i}] {name}")
        print("  [q] Beenden")
        
        choice = input("\nDeine Wahl: ").strip().lower()
        
        if choice == 'q':
            print("\n👋 Demo beendet. Viel Erfolg mit dem Trading-Bot!")
            break
        
        elif choice == '0':
            print("\n🚀 Starte alle Demos...")
            for name, demo_func in demos:
                demo_func()
                time.sleep(1)
            print("\n✅ Alle Demos abgeschlossen!")
        
        elif choice.isdigit() and 1 <= int(choice) <= len(demos):
            idx = int(choice) - 1
            name, demo_func = demos[idx]
            demo_func()
        
        else:
            print("❌ Ungültige Wahl. Bitte nochmal versuchen.")


if __name__ == "__main__":
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo abgebrochen")
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
