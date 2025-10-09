#!/usr/bin/env python3
"""
demo_view_session.py - Demo of View Session Feature
==================================================
Demonstrates the View Session functionality with sample data
"""
import os
import sys
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def create_demo_session(session_id: str, profitable: bool = True):
    """
    Create a demo session log file
    
    Args:
        session_id: Session ID (YYYYMMDD_HHMMSS format)
        profitable: Whether the session should be profitable
    """
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    filepath = f"logs/simulated_trading_session_{session_id}.log"
    
    # Generate session data
    initial_capital = 10000.0
    if profitable:
        total_pnl = random.uniform(100, 500)
        win_rate = random.uniform(0.5, 0.7)
    else:
        total_pnl = -random.uniform(100, 300)
        win_rate = random.uniform(0.3, 0.45)
    
    final_equity = initial_capital + total_pnl
    total_trades = random.randint(10, 30)
    
    # Parse session ID to get timestamp
    date_str = session_id[:8]
    time_str = session_id[9:]
    year = date_str[:4]
    month = date_str[4:6]
    day = date_str[6:8]
    hour = time_str[:2]
    minute = time_str[2:4]
    second = time_str[4:6]
    
    session_start = f"{year}-{month}-{day} {hour}:{minute}:{second}"
    
    # Create log content
    content = f"""================================================================================
SIMULATED LIVE TRADING SESSION LOG
================================================================================
Session Start: {session_start}
Session End: {session_start} (demo)
Initial Capital: ${initial_capital:,.2f}
Final Equity: ${final_equity:,.2f}
Total P&L: ${total_pnl:,.2f}

================================================================================
PERFORMANCE METRICS
================================================================================
total_orders: {total_trades}
filled_orders: {total_trades - 1}
partially_filled_orders: 1
rejected_orders: 0
total_volume_traded: {random.uniform(20000, 50000):.1f}
total_fees_paid: {random.uniform(10, 30):.2f}
total_slippage: {random.uniform(5, 20):.2f}
avg_slippage_percent: {random.uniform(0.01, 0.05):.3f}
avg_execution_delay_ms: {random.uniform(100, 150):.1f}
total_pnl: {total_pnl:.2f}
win_rate: {win_rate:.2f}
sharpe_ratio: {random.uniform(-1, 2):.2f}

================================================================================
EXECUTION HISTORY
================================================================================
"""
    
    # Generate some sample trades
    symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT']
    sides = ['BUY', 'SELL']
    
    for i in range(min(5, total_trades)):
        symbol = random.choice(symbols)
        side = random.choice(sides)
        quantity = random.uniform(0.01, 1.0)
        price = random.uniform(1000, 50000)
        
        content += f"""
Order ID: SIM_{i+1}_{int(datetime.now().timestamp() * 1000)}
  Symbol: {symbol}
  Side: {side}
  Quantity: {quantity:.4f}/{quantity:.4f}
  Execution Price: ${price:.2f}
  Slippage: ${random.uniform(1, 15):.2f} ({random.uniform(0.01, 0.05):.3f}%)
  Fees: ${random.uniform(0.5, 5):.2f}
  Delay: {random.uniform(80, 150):.1f}ms
  Status: FILLED
  Timestamp: {session_start}
"""
    
    # Write to file
    with open(filepath, 'w') as f:
        f.write(content)
    
    return filepath


def print_separator(title: str):
    """Print a formatted separator"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demo_create_sessions():
    """Demo: Create sample sessions"""
    print_separator("DEMO: Creating Sample Sessions")
    
    # Create a mix of profitable and loss sessions
    sessions = [
        ("20240115_100000", True),   # Profitable
        ("20240115_140000", False),  # Loss
        ("20240116_093000", True),   # Profitable
        ("20240116_153000", True),   # Profitable
        ("20240117_110000", False),  # Loss
    ]
    
    print("Creating demo session logs...\n")
    
    for session_id, profitable in sessions:
        filepath = create_demo_session(session_id, profitable)
        status = "✅ Profitable" if profitable else "❌ Loss"
        print(f"  {status}  Created: {filepath}")
    
    print(f"\n✅ Created {len(sessions)} demo sessions")
    print("\n💡 TIP: Open the dashboard to view these sessions:")
    print("   python dashboard.py --web")


def demo_list_sessions():
    """Demo: List all sessions"""
    print_separator("DEMO: Listing All Sessions")
    
    from dashboard import _get_session_list
    
    sessions = _get_session_list()
    
    if not sessions:
        print("❌ No sessions found. Run demo_create_sessions() first.")
        return
    
    print(f"Found {len(sessions)} sessions:\n")
    
    for i, session in enumerate(sessions, 1):
        pnl_symbol = "📈" if session['total_pnl'] >= 0 else "📉"
        print(f"{i}. {pnl_symbol} Session {session['id']}")
        print(f"   Time: {session['timestamp']}")
        print(f"   P&L: ${session['total_pnl']:.2f}")
        print(f"   Trades: {session['total_trades']}")
        print(f"   Win Rate: {session['win_rate']:.1%}")
        print()


def demo_view_session_details():
    """Demo: View details of a specific session"""
    print_separator("DEMO: Viewing Session Details")
    
    from dashboard import _get_session_list, _get_session_details
    
    sessions = _get_session_list()
    
    if not sessions:
        print("❌ No sessions found. Run demo_create_sessions() first.")
        return
    
    # Get the first session
    session_id = sessions[0]['id']
    print(f"Loading details for session: {session_id}\n")
    
    details = _get_session_details(session_id)
    
    if not details:
        print("❌ Failed to load session details")
        return
    
    print("📊 Performance Metrics:")
    for key, value in list(details['metrics'].items())[:8]:
        print(f"   {key}: {value}")
    
    print(f"\n📝 Execution History:")
    print(f"   Total trades: {len(details['trades'])}")
    
    if details['trades']:
        print(f"\n   First trade:")
        first_trade = details['trades'][0]
        for key, value in first_trade.items():
            print(f"      {key}: {value}")


def demo_filter_sessions():
    """Demo: Filter sessions by profitability"""
    print_separator("DEMO: Filtering Sessions")
    
    from dashboard import _get_session_list
    
    sessions = _get_session_list()
    
    if not sessions:
        print("❌ No sessions found. Run demo_create_sessions() first.")
        return
    
    # Filter profitable sessions
    profitable = [s for s in sessions if s['total_pnl'] > 0]
    loss_sessions = [s for s in sessions if s['total_pnl'] < 0]
    
    print(f"📊 Session Statistics:")
    print(f"   Total Sessions: {len(sessions)}")
    print(f"   Profitable: {len(profitable)} ({len(profitable)/len(sessions)*100:.1f}%)")
    print(f"   Loss: {len(loss_sessions)} ({len(loss_sessions)/len(sessions)*100:.1f}%)")
    
    print(f"\n✅ Profitable Sessions:")
    for session in profitable:
        print(f"   - {session['id']}: ${session['total_pnl']:.2f}")
    
    print(f"\n❌ Loss Sessions:")
    for session in loss_sessions:
        print(f"   - {session['id']}: ${session['total_pnl']:.2f}")


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("  📊 VIEW SESSION FEATURE DEMO")
    print("=" * 70)
    
    try:
        # Demo 1: Create sessions
        demo_create_sessions()
        
        # Demo 2: List sessions
        demo_list_sessions()
        
        # Demo 3: View session details
        demo_view_session_details()
        
        # Demo 4: Filter sessions
        demo_filter_sessions()
        
        print_separator("DEMO COMPLETED")
        print("✅ All demos completed successfully!")
        print("\n📖 Next Steps:")
        print("  1. Start the web dashboard: python dashboard.py --web")
        print("  2. Navigate to 'View Sessions' in the dashboard")
        print("  3. Explore session details, filtering, and export features")
        print("  4. Read VIEW_SESSION_GUIDE.md for complete documentation")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
