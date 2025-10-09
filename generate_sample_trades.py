"""
generate_sample_trades.py - Generate sample trades for dashboard demo
"""
import csv
from datetime import datetime, timedelta
import random

# Generate sample trades
trades = []
capital = 10000.0
timestamp = datetime.now() - timedelta(days=5)

strategies = ['rsi', 'ema_crossover', 'ma_crossover', 'bollinger_bands']

for i in range(30):
    # Alternate between BUY and SELL
    if i % 2 == 0:
        # BUY
        price = 30000 + random.uniform(-1000, 1000)
        trade = {
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'symbol': 'BTC/USDT',
            'order_type': 'BUY',
            'price': f'{price:.2f}',
            'quantity': '100',
            'triggering_strategies': random.choice(strategies),
            'capital': f'{capital:.2f}',
            'pnl': '0.00'
        }
    else:
        # SELL
        buy_price = trades[-1]['price']
        price = float(buy_price) + random.uniform(-500, 800)
        pnl = (price - float(buy_price)) * 100
        capital += pnl
        
        trade = {
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'symbol': 'BTC/USDT',
            'order_type': 'SELL',
            'price': f'{price:.2f}',
            'quantity': '100',
            'triggering_strategies': ','.join(random.sample(strategies, random.randint(1, 2))),
            'capital': f'{capital:.2f}',
            'pnl': f'{pnl:.2f}'
        }
    
    trades.append(trade)
    timestamp += timedelta(hours=random.randint(1, 6))

# Save to CSV
with open('data/trades.csv', 'w', newline='', encoding='utf-8') as f:
    fieldnames = ['timestamp', 'symbol', 'order_type', 'price', 'quantity', 'triggering_strategies', 'capital', 'pnl']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(trades)

print(f"✓ Generated {len(trades)} sample trades")
print(f"  Final Capital: ${capital:.2f}")
print(f"  Total P&L: ${capital - 10000:.2f}")
print(f"  Saved to: data/trades.csv")
