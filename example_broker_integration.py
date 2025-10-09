"""
example_broker_integration.py - Broker API Integration Examples
===============================================================

Demonstrates how to use the broker API for automated trading with
different strategies and configurations.
"""

import logging
import time
import pandas as pd
from datetime import datetime
from broker_api import BrokerFactory
from utils import setup_logging

# Setup logging
logger = setup_logging(
    log_level="INFO",
    log_file="logs/broker_integration_example.log"
)


def example_1_paper_trading_basics():
    """Example 1: Basic Paper Trading"""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Paper Trading")
    print("=" * 70)
    
    # Create paper trading broker
    broker = BrokerFactory.create_broker('paper', initial_capital=10000)
    logger.info("✓ Paper trading broker created")
    
    # Check initial balance
    balance = broker.get_account_balance('USDT')
    print(f"\n📊 Initial Balance: ${balance['total']:,.2f}")
    
    # Place a market buy order
    print("\n📈 Placing BUY order...")
    buy_order = broker.place_market_order(
        symbol='BTCUSDT',
        quantity=0.1,
        side='BUY',
        current_price=50000
    )
    print(f"✓ Order ID: {buy_order['order_id']}")
    print(f"✓ Bought {buy_order['quantity']} BTC at ${buy_order['avg_price']:,.2f}")
    
    # Check position
    positions = broker.get_positions()
    print(f"\n📋 Current Positions: {len(positions)}")
    for pos in positions:
        print(f"  • {pos['symbol']}: {pos['quantity']} @ ${pos['entry_price']:,.2f}")
    
    # Check balance after buy
    balance = broker.get_account_balance('USDT')
    print(f"\n💰 Balance After Buy: ${balance['total']:,.2f}")
    
    # Wait (simulated)
    print("\n⏳ Holding position...")
    time.sleep(1)
    
    # Place a market sell order (at profit)
    print("\n📉 Placing SELL order...")
    sell_order = broker.place_market_order(
        symbol='BTCUSDT',
        quantity=0.1,
        side='SELL',
        current_price=51000
    )
    print(f"✓ Order ID: {sell_order['order_id']}")
    print(f"✓ Sold {sell_order['quantity']} BTC at ${sell_order['avg_price']:,.2f}")
    
    # Check final balance
    balance = broker.get_account_balance('USDT')
    profit = balance['total'] - 10000
    print(f"\n💰 Final Balance: ${balance['total']:,.2f}")
    print(f"📊 Profit: ${profit:,.2f} ({(profit/10000)*100:.2f}%)")
    
    print("\n" + "=" * 70)


def example_2_limit_orders():
    """Example 2: Using Limit Orders"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Limit Orders")
    print("=" * 70)
    
    broker = BrokerFactory.create_broker('paper', initial_capital=10000)
    
    # Place limit buy orders at different price levels
    print("\n📋 Placing limit buy orders...")
    buy_prices = [48000, 47000, 46000]
    
    for price in buy_prices:
        order = broker.place_limit_order(
            symbol='BTCUSDT',
            quantity=0.05,
            side='BUY',
            price=price
        )
        print(f"✓ Limit BUY order: 0.05 BTC @ ${price:,.2f} (ID: {order['order_id']})")
    
    # Check open orders
    open_orders = broker.get_open_orders('BTCUSDT')
    print(f"\n📊 Open Orders: {len(open_orders)}")
    for order in open_orders:
        print(f"  • {order['order_id']}: {order['side']} {order['quantity']} @ ${order['price']:,.2f}")
    
    # Cancel one order
    if open_orders:
        cancel_order = open_orders[0]
        print(f"\n❌ Cancelling order {cancel_order['order_id']}...")
        broker.cancel_order('BTCUSDT', cancel_order['order_id'])
        print("✓ Order cancelled")
    
    # Check remaining open orders
    open_orders = broker.get_open_orders('BTCUSDT')
    print(f"\n📊 Remaining Open Orders: {len(open_orders)}")
    
    print("\n" + "=" * 70)


def example_3_multi_asset_portfolio():
    """Example 3: Multi-Asset Portfolio Management"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Multi-Asset Portfolio")
    print("=" * 70)
    
    broker = BrokerFactory.create_broker('paper', initial_capital=10000)
    
    # Portfolio allocation (adjusted to fit within $10,000 capital)
    portfolio = [
        {'symbol': 'BTCUSDT', 'quantity': 0.05, 'price': 50000},  # $2,500
        {'symbol': 'ETHUSDT', 'quantity': 1.0, 'price': 3000},     # $3,000
        {'symbol': 'BNBUSDT', 'quantity': 5.0, 'price': 400}       # $2,000
    ]
    
    print("\n📊 Building Portfolio...")
    total_cost = 0
    
    for asset in portfolio:
        order = broker.place_market_order(
            symbol=asset['symbol'],
            quantity=asset['quantity'],
            side='BUY',
            current_price=asset['price']
        )
        cost = asset['quantity'] * asset['price']
        total_cost += cost
        print(f"✓ Bought {asset['quantity']} {asset['symbol']} @ ${asset['price']:,.2f} (Cost: ${cost:,.2f})")
    
    print(f"\n💰 Total Investment: ${total_cost:,.2f}")
    
    # Check all positions
    positions = broker.get_positions()
    print(f"\n📋 Portfolio Positions: {len(positions)}")
    for pos in positions:
        print(f"  • {pos['symbol']}: {pos['quantity']} (Entry: ${pos['entry_price']:,.2f})")
    
    # Check remaining balance
    balance = broker.get_account_balance('USDT')
    print(f"\n💰 Remaining Balance: ${balance['total']:,.2f}")
    
    # Simulate price movements and close positions at profit
    print("\n⏳ Market moves... Prices increase!")
    time.sleep(1)
    
    print("\n📉 Closing all positions...")
    for asset in portfolio:
        # Simulate 5% profit
        exit_price = asset['price'] * 1.05
        broker.place_market_order(
            symbol=asset['symbol'],
            quantity=asset['quantity'],
            side='SELL',
            current_price=exit_price
        )
        print(f"✓ Sold {asset['quantity']} {asset['symbol']} @ ${exit_price:,.2f}")
    
    # Final balance
    balance = broker.get_account_balance('USDT')
    profit = balance['total'] - 10000
    print(f"\n💰 Final Balance: ${balance['total']:,.2f}")
    print(f"📊 Total Profit: ${profit:,.2f} ({(profit/10000)*100:.2f}%)")
    
    print("\n" + "=" * 70)


def example_4_strategy_integration():
    """Example 4: Integration with Trading Strategy"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Strategy Integration")
    print("=" * 70)
    
    broker = BrokerFactory.create_broker('paper', initial_capital=10000)
    
    # Simple momentum strategy
    class SimpleMomentumStrategy:
        def __init__(self, broker):
            self.broker = broker
            self.position = None
        
        def analyze(self, price, momentum):
            """Analyze market conditions"""
            if momentum > 0.02 and not self.position:
                return 'BUY'
            elif momentum < -0.02 and self.position:
                return 'SELL'
            return 'HOLD'
        
        def execute(self, signal, symbol, price):
            """Execute trading signal"""
            if signal == 'BUY':
                order = self.broker.place_market_order(
                    symbol=symbol,
                    quantity=0.1,
                    side='BUY',
                    current_price=price
                )
                self.position = {'symbol': symbol, 'quantity': 0.1, 'entry_price': price}
                logger.info(f"✓ BOUGHT {symbol} @ ${price:,.2f}")
                return order
            
            elif signal == 'SELL' and self.position:
                order = self.broker.place_market_order(
                    symbol=self.position['symbol'],
                    quantity=self.position['quantity'],
                    side='SELL',
                    current_price=price
                )
                pnl = (price - self.position['entry_price']) * self.position['quantity']
                logger.info(f"✓ SOLD {symbol} @ ${price:,.2f} | P&L: ${pnl:,.2f}")
                self.position = None
                return order
            
            return None
    
    # Initialize strategy
    strategy = SimpleMomentumStrategy(broker)
    print("✓ Strategy initialized")
    
    # Simulate market data
    print("\n📊 Running strategy on simulated market data...")
    market_data = [
        {'price': 50000, 'momentum': 0.01},   # HOLD
        {'price': 51000, 'momentum': 0.025},  # BUY
        {'price': 51500, 'momentum': 0.015},  # HOLD
        {'price': 52000, 'momentum': 0.01},   # HOLD
        {'price': 51000, 'momentum': -0.025}, # SELL
        {'price': 50500, 'momentum': -0.01},  # HOLD
    ]
    
    for i, data in enumerate(market_data):
        print(f"\n--- Candle {i+1} ---")
        print(f"Price: ${data['price']:,.2f} | Momentum: {data['momentum']:.2%}")
        
        signal = strategy.analyze(data['price'], data['momentum'])
        print(f"Signal: {signal}")
        
        if signal != 'HOLD':
            strategy.execute(signal, 'BTCUSDT', data['price'])
        
        time.sleep(0.5)
    
    # Final report
    balance = broker.get_account_balance('USDT')
    profit = balance['total'] - 10000
    print(f"\n💰 Final Balance: ${balance['total']:,.2f}")
    print(f"📊 Total Profit: ${profit:,.2f} ({(profit/10000)*100:.2f}%)")
    
    print("\n" + "=" * 70)


def example_5_risk_management():
    """Example 5: Risk Management"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Risk Management")
    print("=" * 70)
    
    broker = BrokerFactory.create_broker('paper', initial_capital=10000)
    
    # Risk management parameters
    RISK_PER_TRADE = 0.02  # 2% risk per trade
    STOP_LOSS_PERCENT = 0.05  # 5% stop loss
    
    def calculate_position_size(balance, risk_percent, stop_loss_percent):
        """Calculate position size based on risk management"""
        risk_amount = balance * risk_percent
        position_size = risk_amount / stop_loss_percent
        return position_size
    
    print("\n📊 Risk Management Parameters:")
    print(f"  • Risk per trade: {RISK_PER_TRADE*100}%")
    print(f"  • Stop loss: {STOP_LOSS_PERCENT*100}%")
    
    # Get current balance
    balance = broker.get_account_balance('USDT')
    print(f"\n💰 Current Balance: ${balance['total']:,.2f}")
    
    # Calculate position size
    position_size = calculate_position_size(
        balance['total'],
        RISK_PER_TRADE,
        STOP_LOSS_PERCENT
    )
    
    print(f"\n📐 Calculated Position Size: ${position_size:,.2f}")
    
    # Current BTC price
    btc_price = 50000
    btc_quantity = position_size / btc_price
    
    print(f"📊 BTC Quantity to Buy: {btc_quantity:.4f} BTC")
    
    # Place order
    print("\n📈 Placing position-sized order...")
    order = broker.place_market_order(
        symbol='BTCUSDT',
        quantity=btc_quantity,
        side='BUY',
        current_price=btc_price
    )
    print(f"✓ Bought {btc_quantity:.4f} BTC @ ${btc_price:,.2f}")
    
    # Calculate stop loss price
    stop_loss_price = btc_price * (1 - STOP_LOSS_PERCENT)
    take_profit_price = btc_price * (1 + STOP_LOSS_PERCENT * 2)  # 2:1 reward/risk
    
    print(f"\n🛡️ Risk Management Levels:")
    print(f"  • Entry: ${btc_price:,.2f}")
    print(f"  • Stop Loss: ${stop_loss_price:,.2f}")
    print(f"  • Take Profit: ${take_profit_price:,.2f}")
    print(f"  • Risk Amount: ${balance['total'] * RISK_PER_TRADE:,.2f}")
    print(f"  • Potential Reward: ${balance['total'] * RISK_PER_TRADE * 2:,.2f}")
    
    # Simulate stop loss hit
    print("\n⚠️ Price drops to stop loss level...")
    time.sleep(1)
    
    sell_order = broker.place_market_order(
        symbol='BTCUSDT',
        quantity=btc_quantity,
        side='SELL',
        current_price=stop_loss_price
    )
    
    loss = (stop_loss_price - btc_price) * btc_quantity
    print(f"❌ Stop loss hit! Sold @ ${stop_loss_price:,.2f}")
    print(f"📉 Loss: ${loss:,.2f} ({(loss/balance['total'])*100:.2f}% of capital)")
    
    # Final balance
    final_balance = broker.get_account_balance('USDT')
    print(f"\n💰 Final Balance: ${final_balance['total']:,.2f}")
    print(f"📊 Actual Loss: ${final_balance['total'] - 10000:,.2f}")
    
    print("\n" + "=" * 70)


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("🚀 BROKER API INTEGRATION EXAMPLES")
    print("=" * 70)
    print("\nThis script demonstrates various use cases of the broker API:")
    print("1. Basic paper trading operations")
    print("2. Using limit orders")
    print("3. Multi-asset portfolio management")
    print("4. Integration with trading strategies")
    print("5. Risk management implementation")
    print("\n" + "=" * 70)
    
    try:
        # Run examples
        example_1_paper_trading_basics()
        time.sleep(2)
        
        example_2_limit_orders()
        time.sleep(2)
        
        example_3_multi_asset_portfolio()
        time.sleep(2)
        
        example_4_strategy_integration()
        time.sleep(2)
        
        example_5_risk_management()
        
        print("\n" + "=" * 70)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print("\nNext Steps:")
        print("1. Review the examples above")
        print("2. Check BROKER_API_GUIDE.md for detailed documentation")
        print("3. Test with your own strategies")
        print("4. Use Binance testnet for live testing")
        print("\n" + "=" * 70)
        
    except Exception as e:
        logger.error(f"Error running examples: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
