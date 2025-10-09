"""
demo_production_features.py - Demonstration of Production Features
===================================================================
Shows how to use the new security, monitoring, and alerting features.
"""
import os
import time
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def demo_security_features():
    """Demonstrate security manager features"""
    print("\n" + "=" * 70)
    print("🔒 SECURITY MANAGER DEMO")
    print("=" * 70 + "\n")
    
    from security_manager import SecurityManager
    
    # Initialize security manager
    security = SecurityManager(master_password="demo-password-change-me")
    
    # 1. API Key Encryption
    print("1. API Key Encryption")
    print("-" * 40)
    
    # Simulate API keys
    test_keys = {
        "BINANCE_API_KEY": "demo_api_key_12345",
        "BINANCE_SECRET_KEY": "demo_secret_key_67890"
    }
    
    # Encrypt and store
    security.store_encrypted_keys(test_keys, "config/demo_encrypted_keys.json")
    print("✓ API keys encrypted and stored")
    
    # Load and decrypt
    loaded_keys = security.load_encrypted_keys("config/demo_encrypted_keys.json")
    print(f"✓ Loaded {len(loaded_keys)} encrypted keys")
    
    # Verify
    for key_name in test_keys:
        if key_name in loaded_keys:
            original = test_keys[key_name]
            decrypted = loaded_keys[key_name]
            match = "✓" if original == decrypted else "✗"
            print(f"  {match} {key_name}: Encryption/Decryption {'Success' if original == decrypted else 'Failed'}")
    
    # 2. Rate Limiting
    print("\n2. Rate Limiting")
    print("-" * 40)
    
    limiter = security.create_rate_limiter(
        name="demo_api",
        max_calls=5,
        time_window=10
    )
    
    print(f"Rate Limiter: {limiter.max_calls} calls per {limiter.time_window}s")
    print("\nSimulating API calls:")
    
    for i in range(8):
        allowed = limiter.is_allowed()
        remaining = limiter.get_remaining_calls()
        status = "✓ Allowed" if allowed else "✗ Blocked"
        print(f"  Call {i+1}: {status} (Remaining: {remaining})")
        time.sleep(0.2)
    
    # 3. Request Validation
    print("\n3. Request Validation")
    print("-" * 40)
    
    test_requests = [
        {"symbol": "BTC/USDT", "amount": 0.1},  # Valid
        {"symbol": "ETH'; DROP TABLE users; --"},  # SQL injection
        {"symbol": "<script>alert('xss')</script>"}  # XSS attempt
    ]
    
    for i, request in enumerate(test_requests, 1):
        is_valid, error = security.validate_request(request)
        status = "✓ Valid" if is_valid else "✗ Invalid"
        print(f"  Request {i}: {status}")
        if error:
            print(f"    Error: {error}")
    
    # 4. Security Report
    print("\n4. Security Report")
    print("-" * 40)
    
    report = security.generate_security_report()
    print(f"  Timestamp: {report['timestamp']}")
    print(f"  Encrypted Keys: {report['encrypted_keys_count']}")
    print(f"  Rate Limiters: {len(report['rate_limiters'])}")
    
    # Cleanup demo files
    if os.path.exists("config/demo_encrypted_keys.json"):
        os.remove("config/demo_encrypted_keys.json")
    
    print("\n✓ Security Manager Demo Complete")


def demo_alert_system():
    """Demonstrate alert system features"""
    print("\n" + "=" * 70)
    print("🔔 ALERT SYSTEM DEMO")
    print("=" * 70 + "\n")
    
    from alert_system import AlertSystem, AlertType, AlertSeverity
    
    # Initialize alert system
    alerts = AlertSystem()
    
    # 1. Basic Alerts
    print("1. Sending Different Alert Types")
    print("-" * 40 + "\n")
    
    # Trade signal alert
    alerts.alert(
        AlertType.TRADE_SIGNAL,
        AlertSeverity.INFO,
        "BUY Signal Detected",
        "RSI and EMA strategies both indicate BUY for BTC/USDT at $50,234.50",
        data={"symbol": "BTC/USDT", "price": 50234.50, "strategies": ["RSI", "EMA"]}
    )
    
    time.sleep(0.5)
    
    # Warning alert
    alerts.alert(
        AlertType.LOSS_THRESHOLD,
        AlertSeverity.WARNING,
        "Daily Loss Threshold Approaching",
        "Current daily loss: -3.8%. Threshold: -5%",
        data={"current_loss": -3.8, "threshold": -5.0}
    )
    
    time.sleep(0.5)
    
    # Error alert
    alerts.alert(
        AlertType.API_ERROR,
        AlertSeverity.ERROR,
        "API Request Failed",
        "Failed to place order: Insufficient funds",
        data={"error_code": "INSUFFICIENT_FUNDS", "required": 100, "available": 50}
    )
    
    time.sleep(0.5)
    
    # Critical alert
    alerts.alert(
        AlertType.SYSTEM_ERROR,
        AlertSeverity.CRITICAL,
        "Connection Lost",
        "Lost connection to exchange. Attempting to reconnect...",
        data={"exchange": "Binance", "retry_count": 3}
    )
    
    # 2. Alert Statistics
    print("\n2. Alert Statistics")
    print("-" * 40)
    
    stats = alerts.get_alert_stats()
    print(f"  Total Alerts: {stats['total']}")
    print(f"  By Severity:")
    for severity, count in stats['by_severity'].items():
        print(f"    {severity}: {count}")
    print(f"  By Type:")
    for alert_type, count in stats['by_type'].items():
        print(f"    {alert_type}: {count}")
    
    # 3. Alert History
    print("\n3. Recent Alert History")
    print("-" * 40)
    
    history = alerts.get_alert_history(limit=3)
    for i, alert in enumerate(history, 1):
        print(f"  Alert {i}:")
        print(f"    Type: {alert.alert_type.value}")
        print(f"    Severity: {alert.severity.value}")
        print(f"    Title: {alert.title}")
        print(f"    Time: {alert.timestamp.strftime('%H:%M:%S')}")
    
    # 4. Custom Callback Example
    print("\n4. Custom Alert Callback")
    print("-" * 40)
    
    def custom_callback(alert):
        """Custom alert handler"""
        print(f"  📱 Custom Handler: {alert.title}")
        return True
    
    alerts.add_callback(custom_callback, name="custom_demo")
    
    alerts.alert(
        AlertType.PROFIT_TARGET,
        AlertSeverity.INFO,
        "Profit Target Reached",
        "BTC position reached 10% profit target",
        data={"symbol": "BTC/USDT", "profit": 10.5}
    )
    
    print("\n✓ Alert System Demo Complete")


def demo_integration_example():
    """Show how to integrate features in trading"""
    print("\n" + "=" * 70)
    print("🚀 INTEGRATION EXAMPLE")
    print("=" * 70 + "\n")
    
    from security_manager import SecurityManager
    from alert_system import AlertSystem, AlertType, AlertSeverity
    
    print("Example: Secure Trading Bot with Alerts")
    print("-" * 40 + "\n")
    
    # 1. Initialize components
    print("1. Initializing Components")
    security = SecurityManager()
    alerts = AlertSystem()
    print("   ✓ Security Manager initialized")
    print("   ✓ Alert System initialized")
    
    # 2. Setup rate limiter for API
    print("\n2. Setting Up Rate Limiters")
    api_limiter = security.create_rate_limiter(
        name="binance_api",
        max_calls=1200,  # 1200 calls per minute (Binance limit)
        time_window=60
    )
    order_limiter = security.create_rate_limiter(
        name="order_execution",
        max_calls=10,  # 10 orders per minute max
        time_window=60
    )
    print("   ✓ API rate limiter: 1200 calls/min")
    print("   ✓ Order rate limiter: 10 orders/min")
    
    # 3. Simulate trading workflow
    print("\n3. Simulating Trading Workflow")
    print("-" * 40)
    
    # Check API rate limit before making request
    if api_limiter.is_allowed():
        print("   ✓ API rate limit OK - Fetching market data")
        
        # Simulate trade signal
        signals = ["RSI", "EMA"]
        print(f"   📊 Signal detected: {', '.join(signals)}")
        
        # Send alert
        alerts.alert(
            AlertType.TRADE_SIGNAL,
            AlertSeverity.INFO,
            "BUY Signal Generated",
            f"Multiple strategies agree: {', '.join(signals)}",
            data={"strategies": signals, "confidence": 0.85}
        )
        
        # Check order rate limit
        if order_limiter.is_allowed():
            print("   ✓ Order rate limit OK - Placing order")
            
            # Validate order request
            order_request = {
                "symbol": "BTC/USDT",
                "side": "BUY",
                "amount": 0.001
            }
            
            is_valid, error = security.validate_request(order_request)
            if is_valid:
                print("   ✓ Order validation passed")
                print("   📈 Order placed: BUY 0.001 BTC")
                
                # Alert on successful order
                alerts.alert(
                    AlertType.TRADE_EXECUTED,
                    AlertSeverity.INFO,
                    "Order Executed Successfully",
                    "BUY 0.001 BTC at $50,234.50",
                    data=order_request
                )
            else:
                print(f"   ✗ Order validation failed: {error}")
                
                # Alert on validation failure
                alerts.alert(
                    AlertType.SYSTEM_ERROR,
                    AlertSeverity.ERROR,
                    "Order Validation Failed",
                    error,
                    data=order_request
                )
        else:
            print("   ⚠️ Order rate limit exceeded - Waiting")
            
            # Alert on rate limit
            alerts.alert(
                AlertType.SYSTEM_ERROR,
                AlertSeverity.WARNING,
                "Rate Limit Exceeded",
                "Too many orders in short time. Waiting before retry.",
                data={"limiter": "order_execution"}
            )
    
    # 4. Generate reports
    print("\n4. Generating Reports")
    print("-" * 40)
    
    security_report = security.generate_security_report()
    alert_stats = alerts.get_alert_stats()
    
    print(f"   Security Report:")
    print(f"     - Rate limiters active: {len(security_report['rate_limiters'])}")
    
    print(f"   Alert Statistics:")
    print(f"     - Total alerts: {alert_stats['total']}")
    print(f"     - Alert channels: {len(alert_stats['channels'])}")
    
    print("\n✓ Integration Example Complete")


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("🎯 PRODUCTION FEATURES DEMONSTRATION")
    print("=" * 70)
    
    try:
        # Run demos
        demo_security_features()
        demo_alert_system()
        demo_integration_example()
        
        # Summary
        print("\n" + "=" * 70)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print("\nKey Takeaways:")
        print("  1. 🔒 API keys can be encrypted for secure storage")
        print("  2. 🚦 Rate limiting prevents API abuse")
        print("  3. 🔔 Alert system provides real-time notifications")
        print("  4. 🔗 Easy integration with existing trading code")
        print("\nNext Steps:")
        print("  1. Review PRODUCTION_DEPLOYMENT_GUIDE.md")
        print("  2. Run production readiness tests: python test_production_readiness.py")
        print("  3. Configure your alert channels")
        print("  4. Start with testnet trading")
        print("\n⚠️  Remember: Always start small and monitor constantly!")
        print("=" * 70 + "\n")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\n❌ Demo failed: {e}")


if __name__ == "__main__":
    main()
