#!/bin/bash
# start_live.sh - Start both Automation Runner (dry-run) and View Session
# This script runs both processes in parallel for live monitoring

set -e

echo "========================================="
echo " 🚀 Dev: Live Session Starter"
echo "========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python3 is not installed!"
    echo "Please install Python 3.8+ to continue."
    exit 1
fi

# Check if required files exist
if [ ! -f "automation/runner.py" ]; then
    echo "❌ ERROR: automation/runner.py not found!"
    echo "Make sure you're running this script from the project root."
    exit 1
fi

if [ ! -f "tools/view_session_app.py" ]; then
    echo "❌ ERROR: tools/view_session_app.py not found!"
    echo "Make sure you're running this script from the project root."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created!"
    echo ""
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip -q
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -q
fi
if [ -f "requirements/dev.txt" ]; then
    pip install -r requirements/dev.txt -q
fi
pip install streamlit plotly pandas requests python-dotenv -q
echo "✅ Dependencies installed!"
echo ""

# Load .env file if it exists (for additional environment variables)
if [ -f ".env" ]; then
    echo "📄 Loading .env file..."
    export $(grep -v '^#' .env | xargs)
fi

# Set default environment variables (dry-run mode by default)
export DRY_RUN=${DRY_RUN:-true}
export BROKER_NAME=${BROKER_NAME:-binance}
export BINANCE_BASE_URL=${BINANCE_BASE_URL:-https://testnet.binance.vision}

echo "========================================="
echo " ⚙️  Configuration:"
echo "   DRY_RUN: $DRY_RUN"
echo "   BROKER_NAME: $BROKER_NAME"
echo "   BINANCE_BASE_URL: $BINANCE_BASE_URL"
echo "========================================="
echo ""

# Create trap to kill both processes on exit
trap 'kill $(jobs -p) 2>/dev/null' EXIT

echo "🚀 Starting Automation Runner (Dry-Run)..."
python automation/runner.py &
RUNNER_PID=$!

echo "🌐 Starting View Session Dashboard on port 8501..."
streamlit run tools/view_session_app.py --server.port 8501 --server.address 0.0.0.0 &
STREAMLIT_PID=$!

echo ""
echo "========================================="
echo " ✅ Both processes started!"
echo "========================================="
echo ""
echo "📊 View Session Dashboard: http://localhost:8501"
echo "🤖 Runner PID: $RUNNER_PID"
echo "🌐 Streamlit PID: $STREAMLIT_PID"
echo ""
echo "Press Ctrl+C to stop both processes..."
echo ""

# Wait for both processes
wait
