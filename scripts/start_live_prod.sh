#!/bin/bash
# start_live_prod.sh - Live Production Trading Runner (Bash)
# Loads secrets from system keychain and starts live trading

set -e

echo "=========================================="
echo "🚨 LIVE PRODUCTION TRADING"
echo "=========================================="
echo ""
echo "⚠️  WARNING: This will trade with REAL MONEY"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed!"
    exit 1
fi

# Set working directory to project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$PROJECT_ROOT"

# Verify venv exists
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found!"
    echo "   Run: ./scripts/setup_live.sh first"
    exit 1
fi

# Upgrade pip and install required packages
echo "📦 Ensuring dependencies..."
./venv/bin/python -m pip install --upgrade pip --quiet
./venv/bin/python -m pip install python-dotenv keyring requests pyyaml --quiet

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check LIVE_ACK
if [ "$LIVE_ACK" != "I_UNDERSTAND" ]; then
    echo "❌ Error: LIVE_ACK not set correctly"
    echo ""
    echo "You must explicitly acknowledge live trading by setting:"
    echo "  export LIVE_ACK=I_UNDERSTAND"
    echo ""
    echo "Example:"
    echo "  export LIVE_ACK=I_UNDERSTAND"
    echo "  ./scripts/start_live_prod.sh"
    echo ""
    exit 1
fi

echo "✅ LIVE_ACK acknowledged"
echo ""

# Load secrets from system keychain via keyring
echo "🔐 Loading API keys from system keychain..."

keys_output=$(./venv/bin/python -c "
import keyring
import sys

SERVICE_NAME = 'ai.traiding'
try:
    api_key = keyring.get_password(SERVICE_NAME, 'binance_api_key')
    api_secret = keyring.get_password(SERVICE_NAME, 'binance_api_secret')
    
    if not api_key or not api_secret:
        print('ERROR: Credentials not found', file=sys.stderr)
        sys.exit(1)
    
    # Print keys on separate lines (will be read by bash)
    print(api_key)
    print(api_secret)
    sys.exit(0)
except Exception as e:
    print(f'ERROR: {e}', file=sys.stderr)
    sys.exit(1)
" 2>&1)

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to load credentials from system keychain"
    echo "   $keys_output"
    echo ""
    echo "Did you run the setup wizard?"
    echo "  Run: ./scripts/setup_live.sh"
    echo ""
    exit 1
fi

# Parse keys (split by newline)
export BINANCE_API_KEY=$(echo "$keys_output" | sed -n '1p')
export BINANCE_API_SECRET=$(echo "$keys_output" | sed -n '2p')

if [ -z "$BINANCE_API_KEY" ] || [ -z "$BINANCE_API_SECRET" ]; then
    echo "❌ Error: Failed to parse credentials"
    exit 1
fi

echo "✅ API keys loaded (keys not displayed)"

# Set production flags
export DRY_RUN=false
export LIVE_TRADING=true
export BINANCE_BASE_URL=https://api.binance.com
export BROKER_NAME=binance

echo ""
echo "Configuration:"
echo "  LIVE_ACK: $LIVE_ACK"
echo "  DRY_RUN: $DRY_RUN"
echo "  LIVE_TRADING: $LIVE_TRADING"
echo "  BINANCE_BASE_URL: $BINANCE_BASE_URL"
echo "  BROKER_NAME: $BROKER_NAME"
echo ""

# Check KILL_SWITCH
if [ "$KILL_SWITCH" = "true" ]; then
    echo "🛑 KILL_SWITCH ENABLED"
    echo "   Preflight will pass but live orders will be blocked"
    echo "   Open orders will be cancelled (if implemented)"
    echo ""
fi

# Run preflight checks
echo "🚀 Running preflight checks..."
echo ""

./venv/bin/python scripts/live_preflight.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Preflight checks failed!"
    echo "   Cannot start live trading"
    echo ""
    exit 1
fi

# If KILL_SWITCH is enabled, stop here
if [ "$KILL_SWITCH" = "true" ]; then
    echo ""
    echo "🛑 KILL_SWITCH is enabled - not starting runner"
    echo "   To disable: unset KILL_SWITCH or export KILL_SWITCH=false"
    echo ""
    exit 0
fi

# Start live trading
echo ""
echo "=========================================="
echo "🚀 Starting Live Trading Runner"
echo "=========================================="
echo ""
echo "⚠️  LIVE TRADING IN PROGRESS"
echo "   Press Ctrl+C to stop"
echo ""

# Start automation runner with production flags
./venv/bin/python automation/runner.py

echo ""
echo "🛑 Live trading stopped"
