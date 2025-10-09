"""
Generate sample trades for dashboard testing
"""
import csv
import os
from datetime import datetime, timedelta
import random

def generate_sample_trades(filename="data/trades.csv", num_trades=50):
    """Generate sample trading data for testing"""
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Configuration
    initial_capital = 10000.0
    trade_size = 0.1
    starting_price = 30000.0
    
    strategies = ['RSI', 'MACD', 'EMA_Cross', 'Bollinger', 'Volume_Spike']
    
    trades = []
    current_capital = initial_capital
    current_price = starting_price
    position_price = None
    position_quantity = None
    
    start_date = datetime.now() - timedelta(days=30)
    
    for i in range(num_trades):
        # Simulate time progression
        timestamp = start_date + timedelta(hours=i * 12)
        
        # Simulate price movement
        price_change = random.uniform(-500, 500)
        current_price += price_change
        current_price = max(25000, min(35000, current_price))  # Keep in range
        
        # Determine order type
        if position_price is None:
            # BUY order
            order_type = 'BUY'
            quantity = trade_size
            position_price = current_price
            position_quantity = quantity
            pnl = 0
            
            # Random strategies
            num_strategies = random.randint(1, 3)
            triggering_strategies = ','.join(random.sample(strategies, num_strategies))
        else:
            # SELL order
            order_type = 'SELL'
            quantity = position_quantity
            
            # Calculate P&L
            pnl = (current_price - position_price) * quantity
            current_capital += pnl
            
            # Random strategies
            num_strategies = random.randint(1, 3)
            triggering_strategies = ','.join(random.sample(strategies, num_strategies))
            
            # Reset position
            position_price = None
            position_quantity = None
        
        trade = {
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'order_type': order_type,
            'price': f'{current_price:.2f}',
            'quantity': f'{quantity:.6f}',
            'pnl': f'{pnl:.2f}',
            'capital': f'{current_capital:.2f}',
            'triggering_strategies': triggering_strategies,
            'strategy_signals': 'test_signals'
        }
        
        trades.append(trade)
    
    # Write to CSV
    fieldnames = ['timestamp', 'order_type', 'price', 'quantity', 'pnl', 'capital', 
                  'triggering_strategies', 'strategy_signals']
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(trades)
    
    print(f"✅ Generated {len(trades)} sample trades")
    print(f"📁 Saved to: {filename}")
    print(f"💰 Final Capital: ${current_capital:.2f}")
    print(f"📈 P&L: ${current_capital - initial_capital:.2f}")
    
    return filename


if __name__ == '__main__':
    generate_sample_trades()
