"""
setup_live.py - Secure Live Trading Setup Wizard
================================================
Prompts for Binance API keys and risk parameters.
Stores secrets in Windows Credential Manager via keyring.
Writes config/live_risk.yaml (no secrets inside).

SECURITY: This script does NOT print or persist secrets to disk.
"""

import sys
import os
import keyring
import yaml
from getpass import getpass
from typing import Optional

# Service name for keyring
SERVICE_NAME = "ai.traiding"
KEY_API_KEY = "binance_api_key"
KEY_API_SECRET = "binance_api_secret"

def print_banner():
    """Print setup wizard banner."""
    print("=" * 60)
    print("🔐 Live Trading Setup Wizard")
    print("=" * 60)
    print()
    print("⚠️  WARNING: Live trading involves REAL MONEY")
    print("   - Only use API keys with TRADING permissions")
    print("   - NEVER enable withdrawal permissions")
    print("   - Use IP restrictions on your API keys")
    print("   - Start with minimal capital you can afford to lose")
    print()
    print("This wizard will:")
    print("  1. Securely store API keys in Windows Credential Manager")
    print("  2. Configure risk management parameters")
    print("  3. Create config/live_risk.yaml (no secrets)")
    print()
    print("=" * 60)
    print()

def prompt_api_keys():
    """
    Prompt user for Binance API keys.
    
    Returns:
        Tuple of (api_key, api_secret) or (None, None) if cancelled
    """
    print("📝 Enter your Binance API credentials")
    print("   (Keys will be stored securely and never displayed)")
    print()
    
    api_key = input("BINANCE_API_KEY: ").strip()
    if not api_key:
        print("❌ API key is required")
        return None, None
    
    api_secret = getpass("BINANCE_API_SECRET (hidden): ").strip()
    if not api_secret:
        print("❌ API secret is required")
        return None, None
    
    return api_key, api_secret

def store_credentials(api_key, api_secret):
    """
    Store credentials in Windows Credential Manager via keyring.
    
    Args:
        api_key: Binance API key
        api_secret: Binance API secret
        
    Returns:
        True if successful, False otherwise
    """
    try:
        keyring.set_password(SERVICE_NAME, KEY_API_KEY, api_key)
        keyring.set_password(SERVICE_NAME, KEY_API_SECRET, api_secret)
        print("✅ Credentials stored securely in Windows Credential Manager")
        return True
    except Exception as e:
        print(f"❌ Failed to store credentials: {e}")
        return False

def run_strategy_selection(auto_mode: bool = False) -> Optional[str]:
    """
    Führe automatische Strategie-Auswahl durch
    
    Args:
        auto_mode: Wenn True, wird die Auswahl ohne Benutzeraufforderung durchgeführt
    
    Returns:
        Name der empfohlenen Strategie oder None bei Fehler
    """
    print()
    print("=" * 60)
    print("🎯 Automatische Strategie-Auswahl")
    print("=" * 60)
    print()
    print("Analysiere alle Strategien mittels Backtest...")
    print("Dies kann einige Minuten dauern.")
    print()
    
    if not auto_mode:
        choice = input("Strategie-Auswahl durchführen? (j/n) [j]: ").strip().lower()
        if choice == 'n':
            print("⏭️  Strategie-Auswahl übersprungen")
            return None
    else:
        print("🤖 Automatischer Modus: Strategie-Auswahl wird durchgeführt...")
        print()
    
    try:
        # Import hier um Startup zu beschleunigen
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from strategy_selector import StrategySelector
        from utils import generate_sample_data
        
        # Generiere Test-Daten
        print("✓ Generiere historische Daten...")
        data = generate_sample_data(n_bars=2000, start_price=30000)
        
        # Erstelle Selector
        selector = StrategySelector(
            initial_capital=10000.0,
            trade_size=100.0,
            min_trades=10
        )
        
        # Führe Auswahl durch
        print("✓ Führe Backtest für alle Strategien durch...")
        best_name, best_score = selector.run_selection(data)
        
        # Export Ranking
        selector.export_ranking("data/strategy_ranking.csv")
        
        print()
        print("=" * 60)
        print("🏆 Empfohlene Strategie")
        print("=" * 60)
        print(f"  {best_name}")
        print(f"  Score: {best_score.score:.2f}/100")
        print(f"  ROI:   {best_score.roi:+.2f}%")
        print("=" * 60)
        
        return best_name
    
    except ImportError as e:
        print(f"⚠️  Fehler beim Import: {e}")
        print("   Strategie-Auswahl nicht verfügbar")
        return None
    except Exception as e:
        print(f"⚠️  Fehler bei Strategie-Auswahl: {e}")
        print("   Sie können die Strategie später manuell auswählen")
        return None


def prompt_risk_params(recommended_strategy: Optional[str] = None):
    """
    Prompt user for risk management parameters.
    
    Args:
        recommended_strategy: Empfohlene Strategie (optional)
    
    Returns:
        Dictionary of risk parameters or None if cancelled
    """
    print()
    print("📊 Configure Risk Management Parameters")
    print("   (Press Enter to accept defaults)")
    print()
    
    # Trading pairs
    pairs_input = input("Trading pairs [BTCUSDT]: ").strip()
    pairs = pairs_input if pairs_input else "BTCUSDT"
    
    # Strategy selection
    if recommended_strategy:
        print()
        print(f"💡 Empfohlene Strategie: {recommended_strategy}")
        strategy_input = input(f"Strategie [{recommended_strategy}]: ").strip()
        strategy = strategy_input if strategy_input else recommended_strategy
    else:
        print()
        print("Verfügbare Strategien:")
        print("  - Golden Cross (50/200)")
        print("  - MA Crossover (20/50)")
        print("  - RSI Mean Reversion")
        print("  - EMA Crossover (9/21)")
        print("  - Bollinger Bands")
        strategy_input = input("Strategie [Golden Cross (50/200)]: ").strip()
        strategy = strategy_input if strategy_input else "Golden Cross (50/200)"
    
    # Max risk per trade
    max_risk_input = input("Max risk per trade (0.005 = 0.5%) [0.005]: ").strip()
    try:
        max_risk = float(max_risk_input) if max_risk_input else 0.005
        if max_risk <= 0 or max_risk > 0.1:
            print("⚠️  Risk should be between 0 and 0.1 (10%), using default 0.005")
            max_risk = 0.005
    except ValueError:
        print("⚠️  Invalid value, using default 0.005")
        max_risk = 0.005
    
    # Daily loss limit
    daily_loss_input = input("Daily loss limit (0.01 = 1%) [0.01]: ").strip()
    try:
        daily_loss = float(daily_loss_input) if daily_loss_input else 0.01
        if daily_loss <= 0 or daily_loss > 0.2:
            print("⚠️  Daily loss should be between 0 and 0.2 (20%), using default 0.01")
            daily_loss = 0.01
    except ValueError:
        print("⚠️  Invalid value, using default 0.01")
        daily_loss = 0.01
    
    # Max open exposure
    max_exposure_input = input("Max open exposure (0.05 = 5%) [0.05]: ").strip()
    try:
        max_exposure = float(max_exposure_input) if max_exposure_input else 0.05
        if max_exposure <= 0 or max_exposure > 1.0:
            print("⚠️  Exposure should be between 0 and 1.0 (100%), using default 0.05")
            max_exposure = 0.05
    except ValueError:
        print("⚠️  Invalid value, using default 0.05")
        max_exposure = 0.05
    
    # Order types
    print()
    print("Allowed order types:")
    print("  1. LIMIT_ONLY (safer, may miss fills)")
    print("  2. LIMIT_AND_MARKET (faster execution, more slippage)")
    order_choice = input("Choose [1]: ").strip()
    order_types = "LIMIT_AND_MARKET" if order_choice == "2" else "LIMIT_ONLY"
    
    # Max slippage
    slippage_input = input("Max slippage (0.003 = 0.3%) [0.003]: ").strip()
    try:
        slippage = float(slippage_input) if slippage_input else 0.003
        if slippage < 0 or slippage > 0.05:
            print("⚠️  Slippage should be between 0 and 0.05 (5%), using default 0.003")
            slippage = 0.003
    except ValueError:
        print("⚠️  Invalid value, using default 0.003")
        slippage = 0.003
    
    return {
        "pairs": pairs,
        "strategy": strategy,
        "max_risk_per_trade": max_risk,
        "daily_loss_limit": daily_loss,
        "max_open_exposure": max_exposure,
        "allowed_order_types": order_types,
        "max_slippage": slippage
    }

def write_risk_config(risk_params):
    """
    Write risk configuration to config/live_risk.yaml.
    
    Args:
        risk_params: Dictionary of risk parameters
        
    Returns:
        True if successful, False otherwise
    """
    try:
        config_path = "config/live_risk.yaml"
        
        # Create config directory if it doesn't exist
        os.makedirs("config", exist_ok=True)
        
        # Write YAML file
        with open(config_path, 'w') as f:
            yaml.dump(risk_params, f, default_flow_style=False, sort_keys=False)
        
        print(f"✅ Risk configuration written to {config_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to write risk configuration: {e}")
        return False

def update_strategy_in_config(strategy_name: str) -> bool:
    """
    Update strategy in existing config/live_risk.yaml
    
    Args:
        strategy_name: Name of the strategy to set
        
    Returns:
        True if successful, False otherwise
    """
    try:
        config_path = "config/live_risk.yaml"
        
        if not os.path.exists(config_path):
            print(f"⚠️  Config file {config_path} not found")
            return False
        
        # Read existing config
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f) or {}
        
        # Update strategy
        config['strategy'] = strategy_name
        
        # Write back
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        print(f"✅ Strategy updated in {config_path}: {strategy_name}")
        return True
    except Exception as e:
        print(f"❌ Failed to update strategy in config: {e}")
        return False

def verify_storage():
    """
    Verify that credentials can be retrieved from keyring.
    
    Returns:
        True if credentials are accessible, False otherwise
    """
    try:
        api_key = keyring.get_password(SERVICE_NAME, KEY_API_KEY)
        api_secret = keyring.get_password(SERVICE_NAME, KEY_API_SECRET)
        
        if api_key and api_secret:
            print("✅ Credentials verified in Windows Credential Manager")
            return True
        else:
            print("❌ Credentials not found in Credential Manager")
            return False
    except Exception as e:
        print(f"❌ Failed to verify credentials: {e}")
        return False

def main():
    """Main setup wizard flow."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Live Trading Setup Wizard')
    parser.add_argument('--auto-strategy', action='store_true',
                        help='Automatically select and set the best strategy without prompting')
    parser.add_argument('--strategy-only', action='store_true',
                        help='Only run strategy selection and update config (skip API key setup)')
    args = parser.parse_args()
    
    # Strategy-only mode: Just run selection and update config
    if args.strategy_only:
        print_banner()
        print("🎯 Strategie-Auswahl Modus")
        print("=" * 60)
        print()
        
        recommended_strategy = run_strategy_selection(auto_mode=args.auto_strategy)
        
        if recommended_strategy:
            # Update strategy in existing config
            if update_strategy_in_config(recommended_strategy):
                print()
                print("=" * 60)
                print("✅ Strategy Selection Complete!")
                print("=" * 60)
                print(f"   Selected Strategy: {recommended_strategy}")
                print(f"   Updated in: config/live_risk.yaml")
                print("=" * 60)
                return 0
            else:
                print("⚠️  Strategy selected but config update failed")
                return 1
        else:
            print("⚠️  No strategy selected")
            return 1
    
    # Normal setup flow
    print_banner()
    
    # Prompt for API keys
    api_key, api_secret = prompt_api_keys()
    if not api_key or not api_secret:
        print("❌ Setup cancelled")
        return 1
    
    # Store credentials
    if not store_credentials(api_key, api_secret):
        return 1
    
    # Verify storage
    if not verify_storage():
        return 1
    
    # Run strategy selection
    recommended_strategy = run_strategy_selection(auto_mode=args.auto_strategy)
    
    # Prompt for risk parameters
    risk_params = prompt_risk_params(recommended_strategy)
    if not risk_params:
        print("❌ Setup cancelled")
        return 1
    
    # Write risk configuration
    if not write_risk_config(risk_params):
        return 1
    
    # Success message
    print()
    print("=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Review config/live_risk.yaml")
    print("  2. Set LIVE_ACK=I_UNDERSTAND in your environment")
    print("  3. Run: scripts/start_live_prod.ps1")
    print()
    print("⚠️  IMPORTANT:")
    print("   - Revoke any API keys that were previously exposed")
    print("   - Enable IP restrictions on your API keys")
    print("   - Start with minimal capital")
    print("   - Monitor closely during first trades")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
