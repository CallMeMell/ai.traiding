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
    Validate exchange info for trading symbols with detailed filter information.
    
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
            
            # Extract and display MIN_NOTIONAL details
            min_notional_filter = filters.get("MIN_NOTIONAL", {})
            if "minNotional" in min_notional_filter:
                min_notional = float(min_notional_filter["minNotional"])
                print_status(STATUS_OK, f"Symbol {symbol} validated (status: TRADING, min notional: {min_notional:.2f} USDT)")
            else:
                print_status(STATUS_OK, f"Symbol {symbol} validated (status: TRADING)")
            
            # Display LOT_SIZE details for reference
            lot_size_filter = filters.get("LOT_SIZE", {})
            if "minQty" in lot_size_filter:
                min_qty = lot_size_filter["minQty"]
                print_status(STATUS_OK, f"  Min quantity: {min_qty}, Step size: {lot_size_filter.get('stepSize', 'N/A')}")
        
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

def check_risk_configuration() -> Tuple[bool, str]:
    """
    Check risk management configuration from config/live_risk.yaml.
    
    Returns:
        Tuple of (success, message)
    """
    print("\n⚙️  Checking risk configuration...")
    
    try:
        import yaml
        
        config_path = "config/live_risk.yaml"
        if not os.path.exists(config_path):
            return False, f"Risk configuration file not found: {config_path}"
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Validate required fields
        required_fields = {
            "pairs": str,
            "max_risk_per_trade": (int, float),
            "daily_loss_limit": (int, float),
            "max_open_exposure": (int, float),
            "allowed_order_types": str,
            "max_slippage": (int, float)
        }
        
        for field, expected_type in required_fields.items():
            if field not in config:
                return False, f"Missing required field: {field}"
            
            if not isinstance(config[field], expected_type):
                return False, f"Field '{field}' has wrong type (expected {expected_type.__name__})"
        
        # Validate ranges
        max_risk = float(config["max_risk_per_trade"])
        if max_risk <= 0 or max_risk > 0.1:
            return False, f"max_risk_per_trade must be between 0 and 0.1 (10%), got: {max_risk}"
        
        daily_loss = float(config["daily_loss_limit"])
        if daily_loss <= 0 or daily_loss > 0.2:
            return False, f"daily_loss_limit must be between 0 and 0.2 (20%), got: {daily_loss}"
        
        max_exposure = float(config["max_open_exposure"])
        if max_exposure <= 0 or max_exposure > 1.0:
            return False, f"max_open_exposure must be between 0 and 1.0 (100%), got: {max_exposure}"
        
        max_slippage = float(config["max_slippage"])
        if max_slippage < 0 or max_slippage > 0.05:
            return False, f"max_slippage must be between 0 and 0.05 (5%), got: {max_slippage}"
        
        # Validate order types
        allowed_order_types = config["allowed_order_types"]
        valid_order_types = ["LIMIT_ONLY", "LIMIT_AND_MARKET"]
        if allowed_order_types not in valid_order_types:
            return False, f"allowed_order_types must be one of {valid_order_types}, got: {allowed_order_types}"
        
        print_status(STATUS_OK, f"Risk config validated (pairs: {config['pairs']})")
        print_status(STATUS_OK, f"  Max risk/trade: {max_risk*100:.2f}%, Daily loss limit: {daily_loss*100:.2f}%")
        print_status(STATUS_OK, f"  Max exposure: {max_exposure*100:.2f}%, Order types: {allowed_order_types}")
        print_status(STATUS_OK, f"  Max slippage: {max_slippage*100:.2f}%")
        
        return True, "Risk configuration validated"
        
    except yaml.YAMLError as e:
        return False, f"Invalid YAML in {config_path}: {str(e)}"
    except Exception as e:
        return False, f"Failed to check risk configuration: {str(e)}"

def check_kill_switch() -> Tuple[bool, str]:
    """
    Check KILL_SWITCH status and report it.
    This is informational - KILL_SWITCH enabled is not an error.
    
    Returns:
        Tuple of (success, message)
    """
    print("\n🛑 Checking kill switch status...")
    
    kill_switch = os.getenv("KILL_SWITCH", "false").lower()
    
    if kill_switch == "true":
        print_status(STATUS_OK, "KILL_SWITCH is ENABLED - no orders will be placed")
        return True, "Kill switch enabled (orders blocked)"
    else:
        print_status(STATUS_OK, "KILL_SWITCH is disabled - normal trading mode")
        return True, "Kill switch disabled"

def check_order_types_support(symbols: Optional[list] = None) -> Tuple[bool, str]:
    """
    Check that configured order types are supported by exchange for all symbols.
    
    Args:
        symbols: List of symbols to check (default: ["BTCUSDT"])
        
    Returns:
        Tuple of (success, message)
    """
    print("\n📝 Checking order types support...")
    
    if symbols is None:
        symbols = ["BTCUSDT"]
    
    try:
        import yaml
        
        # Load config to get allowed order types
        config_path = "config/live_risk.yaml"
        if not os.path.exists(config_path):
            # If no config, skip this check
            print_status(STATUS_OK, "No risk config found - skipping order type validation")
            return True, "Order type check skipped (no config)"
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        allowed_order_types = config.get("allowed_order_types", "LIMIT_ONLY")
        
        base_url = os.getenv("BINANCE_BASE_URL", "https://api.binance.com")
        response = requests.get(f"{base_url}/api/v3/exchangeInfo", timeout=10)
        response.raise_for_status()
        
        exchange_info = response.json()
        symbol_map = {s["symbol"]: s for s in exchange_info.get("symbols", [])}
        
        for symbol in symbols:
            if symbol not in symbol_map:
                return False, f"Symbol {symbol} not found on exchange"
            
            info = symbol_map[symbol]
            supported_order_types = info.get("orderTypes", [])
            
            # Check if required order types are supported
            if allowed_order_types == "LIMIT_ONLY":
                if "LIMIT" not in supported_order_types:
                    return False, f"Symbol {symbol} does not support LIMIT orders"
            elif allowed_order_types == "LIMIT_AND_MARKET":
                if "LIMIT" not in supported_order_types or "MARKET" not in supported_order_types:
                    return False, f"Symbol {symbol} does not support required order types"
            
            print_status(STATUS_OK, f"Symbol {symbol} supports {allowed_order_types}")
        
        return True, "Order types validated"
        
    except Exception as e:
        return False, f"Failed to check order types: {str(e)}"

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
        ("Risk Configuration", check_risk_configuration),
        ("Order Types", lambda: check_order_types_support(symbols)),
        ("Kill Switch", check_kill_switch),
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
        
        # Log success to file
        try:
            os.makedirs("logs", exist_ok=True)
            with open("logs/preflight_checks.log", "a") as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"[{datetime.now().isoformat()}] Preflight checks PASSED\n")
                f.write(f"  Symbols: {', '.join(symbols) if symbols else 'BTCUSDT'}\n")
                f.write(f"  KILL_SWITCH: {os.getenv('KILL_SWITCH', 'false')}\n")
                f.write(f"{'='*60}\n")
        except Exception as e:
            print(f"\n⚠️  Warning: Could not write to log file: {e}")
        
        print("\n🚀 Starting live trading runner...")
        return 0
    else:
        print_status(STATUS_ERROR, "Preflight checks failed")
        print("=" * 60)
        print("\n❌ Cannot start live trading")
        print("   Fix the errors above and try again")
        
        # Log failure to file
        try:
            os.makedirs("logs", exist_ok=True)
            with open("logs/preflight_checks.log", "a") as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"[{datetime.now().isoformat()}] Preflight checks FAILED\n")
                f.write(f"  Symbols: {', '.join(symbols) if symbols else 'BTCUSDT'}\n")
                f.write(f"  KILL_SWITCH: {os.getenv('KILL_SWITCH', 'false')}\n")
                f.write(f"  Check output above for details\n")
                f.write(f"{'='*60}\n")
        except Exception as e:
            print(f"\n⚠️  Warning: Could not write to log file: {e}")
        
        return 1

def main():
    """Main entry point."""
    return run_all_checks()

if __name__ == "__main__":
    sys.exit(main())
