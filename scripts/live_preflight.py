"""
live_preflight.py - Live Trading Preflight Checks
=================================================
Validates environment, connectivity, and account before live trading.

SECURITY: No secrets are printed to output.
"""

import sys
import os
import time
import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

# Machine-readable status codes
STATUS_OK = "OK"
STATUS_ERROR = "ERR"

def print_status(status: str, message: str, level: str = "info"):
    """
    Print machine-readable status with human message.
    
    Args:
        status: STATUS_OK or STATUS_ERROR
        message: Human-readable message
        level: Message level (info, warning, error)
    """
    icon = "✅" if status == STATUS_OK else "❌"
    color_code = "\033[92m" if status == STATUS_OK else "\033[91m"  # Green or Red
    reset_code = "\033[0m"
    
    print(f"{color_code}[{status}]{reset_code} {icon} {message}")

def check_environment() -> Tuple[bool, str]:
    """
    Check required environment variables.
    
    Returns:
        Tuple of (success, message)
    """
    print("\n🔍 Checking environment variables...")
    
    # Check LIVE_ACK
    live_ack = os.getenv("LIVE_ACK", "")
    if live_ack != "I_UNDERSTAND":
        return False, "LIVE_ACK must be set to 'I_UNDERSTAND'"
    print_status(STATUS_OK, "LIVE_ACK is set correctly")
    
    # Check DRY_RUN
    dry_run = os.getenv("DRY_RUN", "true").lower()
    if dry_run != "false":
        return False, "DRY_RUN must be set to 'false' for live trading"
    print_status(STATUS_OK, "DRY_RUN is set to false")
    
    # Check LIVE_TRADING
    live_trading = os.getenv("LIVE_TRADING", "false").lower()
    if live_trading != "true":
        return False, "LIVE_TRADING must be set to 'true'"
    print_status(STATUS_OK, "LIVE_TRADING is set to true")
    
    # Check production endpoint
    base_url = os.getenv("BINANCE_BASE_URL", "")
    if not base_url.startswith("https://api.binance.com"):
        return False, f"BINANCE_BASE_URL must be production endpoint (https://api.binance.com), got: {base_url}"
    print_status(STATUS_OK, "Production endpoint configured")
    
    return True, "Environment variables validated"

def check_credentials() -> Tuple[bool, str]:
    """
    Check that API credentials are available (without printing them).
    
    Returns:
        Tuple of (success, message)
    """
    print("\n🔑 Checking API credentials...")
    
    api_key = os.getenv("BINANCE_API_KEY", "")
    api_secret = os.getenv("BINANCE_API_SECRET", "")
    
    if not api_key:
        return False, "BINANCE_API_KEY not found in environment"
    
    if not api_secret:
        return False, "BINANCE_API_SECRET not found in environment"
    
    # Verify key format (should be non-empty strings)
    if len(api_key) < 10:
        return False, "BINANCE_API_KEY appears invalid (too short)"
    
    if len(api_secret) < 10:
        return False, "BINANCE_API_SECRET appears invalid (too short)"
    
    print_status(STATUS_OK, "API credentials present (keys not displayed)")
    return True, "Credentials validated"

def check_time_sync() -> Tuple[bool, str]:
    """
    Check time synchronization with Binance server.
    Binance requires timestamps within 1000ms.
    
    Returns:
        Tuple of (success, message)
    """
    print("\n⏰ Checking time synchronization...")
    
    try:
        base_url = os.getenv("BINANCE_BASE_URL", "https://api.binance.com")
        response = requests.get(f"{base_url}/api/v3/time", timeout=5)
        response.raise_for_status()
        
        server_time = response.json()["serverTime"]
        local_time = int(time.time() * 1000)
        time_diff = abs(server_time - local_time)
        
        if time_diff > 1000:
            return False, f"Time drift too large: {time_diff}ms (max 1000ms)"
        
        print_status(STATUS_OK, f"Time sync OK (drift: {time_diff}ms)")
        return True, "Time synchronized"
        
    except Exception as e:
        return False, f"Failed to check time sync: {str(e)}"

def check_exchange_info(symbols: Optional[list] = None) -> Tuple[bool, str]:
    """
    Validate exchange info for trading symbols.
    
    Args:
        symbols: List of symbols to check (default: ["BTCUSDT"])
        
    Returns:
        Tuple of (success, message)
    """
    print("\n📊 Checking exchange information...")
    
    if symbols is None:
        symbols = ["BTCUSDT"]
    
    try:
        base_url = os.getenv("BINANCE_BASE_URL", "https://api.binance.com")
        response = requests.get(f"{base_url}/api/v3/exchangeInfo", timeout=10)
        response.raise_for_status()
        
        exchange_info = response.json()
        symbol_map = {s["symbol"]: s for s in exchange_info.get("symbols", [])}
        
        for symbol in symbols:
            if symbol not in symbol_map:
                return False, f"Symbol {symbol} not found on exchange"
            
            info = symbol_map[symbol]
            if info["status"] != "TRADING":
                return False, f"Symbol {symbol} is not trading (status: {info['status']})"
            
            # Check for required filters
            filters = {f["filterType"]: f for f in info.get("filters", [])}
            required_filters = ["PRICE_FILTER", "LOT_SIZE", "MIN_NOTIONAL"]
            
            for filter_type in required_filters:
                if filter_type not in filters:
                    return False, f"Symbol {symbol} missing {filter_type} filter"
            
            print_status(STATUS_OK, f"Symbol {symbol} validated (status: TRADING)")
        
        return True, "Exchange info validated"
        
    except Exception as e:
        return False, f"Failed to check exchange info: {str(e)}"

def check_account_balance() -> Tuple[bool, str]:
    """
    Check account balances meet minimum requirements.
    
    Returns:
        Tuple of (success, message)
    """
    print("\n💰 Checking account balance...")
    
    try:
        import hmac
        import hashlib
        from urllib.parse import urlencode
        
        base_url = os.getenv("BINANCE_BASE_URL", "https://api.binance.com")
        api_key = os.getenv("BINANCE_API_KEY", "")
        api_secret = os.getenv("BINANCE_API_SECRET", "")
        
        # Create signed request
        timestamp = int(time.time() * 1000)
        params = {
            "timestamp": timestamp,
            "recvWindow": 5000
        }
        
        query_string = urlencode(params)
        signature = hmac.new(
            api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        url = f"{base_url}/api/v3/account?{query_string}&signature={signature}"
        headers = {"X-MBX-APIKEY": api_key}
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        account_info = response.json()
        balances = account_info.get("balances", [])
        
        # Check for USDT balance (or other quote assets)
        usdt_balance = 0.0
        for balance in balances:
            if balance["asset"] == "USDT":
                usdt_balance = float(balance["free"]) + float(balance["locked"])
                break
        
        # Minimum balance check (e.g., 10 USDT minimum)
        min_balance = 10.0
        if usdt_balance < min_balance:
            return False, f"USDT balance too low: {usdt_balance:.2f} (minimum: {min_balance})"
        
        print_status(STATUS_OK, f"Account balance sufficient (USDT: {usdt_balance:.2f})")
        return True, "Account balance validated"
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return False, "Authentication failed - check API keys"
        return False, f"HTTP error: {e.response.status_code}"
    except Exception as e:
        return False, f"Failed to check account balance: {str(e)}"

def run_all_checks() -> int:
    """
    Run all preflight checks.
    
    Returns:
        0 if all checks pass, 1 otherwise
    """
    print("=" * 60)
    print("🚀 Live Trading Preflight Checks")
    print("=" * 60)
    
    # Load config/live_risk.yaml if available
    symbols = None
    try:
        import yaml
        if os.path.exists("config/live_risk.yaml"):
            with open("config/live_risk.yaml", 'r') as f:
                config = yaml.safe_load(f)
                pairs = config.get("pairs", "BTCUSDT")
                symbols = [s.strip() for s in pairs.split(",")]
                print(f"\n📋 Trading pairs from config: {', '.join(symbols)}")
    except Exception as e:
        print(f"\n⚠️  Warning: Could not load config/live_risk.yaml: {e}")
        print("   Using default symbol: BTCUSDT")
    
    all_passed = True
    
    # Run checks
    checks = [
        ("Environment", check_environment),
        ("Credentials", check_credentials),
        ("Time Sync", check_time_sync),
        ("Exchange Info", lambda: check_exchange_info(symbols)),
        ("Account Balance", check_account_balance),
    ]
    
    for check_name, check_func in checks:
        try:
            success, message = check_func()
            if not success:
                print_status(STATUS_ERROR, f"{check_name}: {message}")
                all_passed = False
        except Exception as e:
            print_status(STATUS_ERROR, f"{check_name}: Unexpected error: {str(e)}")
            all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print_status(STATUS_OK, "All preflight checks passed")
        print("=" * 60)
        print("\n✅ Ready for live trading")
        print("\n⚠️  FINAL WARNINGS:")
        print("   - You are about to trade with REAL MONEY")
        print("   - Monitor your positions closely")
        print("   - Set up alerts for large losses")
        print("   - Have an emergency stop plan")
        print("\n🚀 Starting live trading runner...")
        return 0
    else:
        print_status(STATUS_ERROR, "Preflight checks failed")
        print("=" * 60)
        print("\n❌ Cannot start live trading")
        print("   Fix the errors above and try again")
        return 1

def main():
    """Main entry point."""
    return run_all_checks()

if __name__ == "__main__":
    sys.exit(main())
