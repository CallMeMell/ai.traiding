"""
demo_binance_testnet_adapter.py - Binance Testnet Adapter Demo
=============================================================
Demonstrates the Binance Testnet adapter functionality.

Features:
- Connection to Binance Testnet
- Health check
- Dry-run order placement
- Account balance retrieval
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from system.adapters import AdapterFactory, OrderSide, OrderType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Run Binance Testnet adapter demo."""
    print("=" * 70)
    print("  Binance Testnet Adapter - Demo")
    print("=" * 70)
    print()
    
    # Set DRY_RUN mode
    os.environ['DRY_RUN'] = 'true'
    
    # 1. Create adapter using factory
    print("1. Creating Binance Testnet adapter...")
    adapter = AdapterFactory.create('binance', testnet=True)
    print(f"✓ Adapter created: {adapter.__class__.__name__}")
    print()
    
    # 2. Connect to Binance Testnet
    print("2. Connecting to Binance Testnet...")
    if adapter.connect():
        print("✓ Connected successfully")
    else:
        print("❌ Connection failed")
        return
    print()
    
    # 3. Perform health check
    print("3. Performing health check...")
    if adapter.health_check():
        print("✓ Health check passed")
    else:
        print("⚠️ Health check failed")
    print()
    
    # 4. Get adapter info
    print("4. Adapter information:")
    info = adapter.get_adapter_info()
    for key, value in info.items():
        print(f"   {key}: {value}")
    print()
    
    # 5. Get market price (public API, no keys required)
    print("5. Getting market price for BTCUSDT...")
    try:
        price = adapter.get_market_price('BTCUSDT')
        print(f"✓ Current price: ${price:,.2f}")
    except Exception as e:
        print(f"⚠️ Could not get price: {e}")
    print()
    
    # 6. Place a dry-run order
    print("6. Placing dry-run order...")
    order = adapter.place_order(
        'BTCUSDT',
        OrderSide.BUY,
        OrderType.MARKET,
        0.001
    )
    
    if order.get('status') == 'filled':
        print(f"✓ Order placed (DRY-RUN)")
        print(f"   Order ID: {order.get('order_id')}")
        print(f"   Symbol: {order.get('symbol')}")
        print(f"   Side: {order.get('side')}")
        print(f"   Quantity: {order.get('quantity')}")
        print(f"   Price: ${order.get('price'):,.2f}")
        print(f"   Dry-run: {order.get('dry_run')}")
    else:
        print(f"⚠️ Order failed: {order.get('error', 'Unknown error')}")
    print()
    
    # 7. Check order status
    print("7. Checking order status...")
    if 'order_id' in order:
        status = adapter.get_order_status(order['order_id'])
        print(f"✓ Order status: {status.get('status')}")
    print()
    
    # 8. Get open orders (should be empty in dry-run)
    print("8. Getting open orders...")
    open_orders = adapter.get_open_orders()
    print(f"✓ Open orders: {len(open_orders)}")
    print()
    
    # 9. Disconnect
    print("9. Disconnecting...")
    if adapter.disconnect():
        print("✓ Disconnected successfully")
    print()
    
    print("=" * 70)
    print("  Demo completed successfully!")
    print("=" * 70)
    print()
    print("Note: All operations were performed in DRY-RUN mode.")
    print("No real orders were placed on the exchange.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        logger.exception("Demo failed")
        print(f"\n❌ Demo failed: {e}")
        sys.exit(1)
