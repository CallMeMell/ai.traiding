#!/bin/bash
# start_live.sh - One-click Dev Live Session Launcher
# Starts Automation Runner (Dry-Run) + Streamlit View Session
# With environment checks, dependency verification, and port finding

set -e

echo "=========================================="
echo "🚀 Starting Dev Live Session"
echo "=========================================="
echo ""

# Set working directory to project root
cd "$(dirname "$0")/.."

# Step 1: Run environment checks
echo "Step 1: Environment Check"
echo "--------------------------"
python3 scripts/env-check.py
ENV_CHECK_EXIT=$?

if [ $ENV_CHECK_EXIT -eq 1 ]; then
    echo ""
    echo "❌ Environment check failed with critical errors."
    echo "   Please fix the issues above before starting."
    exit 1
elif [ $ENV_CHECK_EXIT -eq 2 ]; then
    echo ""
    echo "⚠️  Environment check passed with warnings."
    echo "   Proceeding anyway..."
fi
echo ""

# Step 2: Verify dependencies
echo "Step 2: Dependency Verification"
echo "--------------------------------"
python3 scripts/verify-deps.py --install
DEPS_EXIT=$?

if [ $DEPS_EXIT -eq 2 ]; then
    echo ""
    echo "⚠️  Some dependencies failed to install."
    echo "   You may encounter issues. Proceeding anyway..."
fi
echo ""

# Step 3: Find a free port for Streamlit (8501-8510)
echo "Step 3: Finding Free Port"
echo "-------------------------"
STREAMLIT_PORT=8501
PORT_FOUND=0

for port in {8501..8510}; do
    if ! lsof -i:$port > /dev/null 2>&1; then
        STREAMLIT_PORT=$port
        PORT_FOUND=1
        echo "✅ Found free port: $STREAMLIT_PORT"
        break
    fi
done

if [ $PORT_FOUND -eq 0 ]; then
    echo "⚠️  All ports 8501-8510 are in use. Using 8501 anyway..."
    STREAMLIT_PORT=8501
fi
echo ""

# Step 4: Activate venv if present
echo "Step 4: Virtual Environment"
echo "---------------------------"
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "⚠️  No venv found. Using system Python."
fi
echo ""

# Load environment variables from .env file (if exists)
if [ -f ".env" ]; then
    echo "🔧 Loading environment variables from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set default environment variables for DRY_RUN (if not set in .env)
export DRY_RUN=${DRY_RUN:-true}
export BROKER_NAME=${BROKER_NAME:-binance}
export BINANCE_BASE_URL=${BINANCE_BASE_URL:-https://testnet.binance.vision}

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo "=========================================="
echo ""
echo "Configuration:"
echo "  DRY_RUN: $DRY_RUN"
echo "  BROKER_NAME: $BROKER_NAME"
echo "  BINANCE_BASE_URL: $BINANCE_BASE_URL"
echo "  STREAMLIT_PORT: $STREAMLIT_PORT"
echo ""
echo "Starting processes in parallel..."
echo "- Automation Runner (Dry-Run mode)"
echo "- Streamlit View Session (http://localhost:$STREAMLIT_PORT)"
echo ""
echo "Press Ctrl+C to stop all processes"
echo "=========================================="
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping all processes..."
    pkill -P $$ || true
    exit 0
}

trap cleanup INT TERM

# Start Automation Runner in background
echo "🤖 Starting Automation Runner..."
python automation/runner.py &
RUNNER_PID=$!

# Wait a moment for runner to start
sleep 2

# Start Streamlit in background
echo "📊 Starting Streamlit View Session..."
streamlit run tools/view_session_app.py --server.port $STREAMLIT_PORT --server.address 0.0.0.0 --server.headless true &
STREAMLIT_PID=$!

echo ""
echo "✅ Both processes started!"
echo "   - Automation Runner PID: $RUNNER_PID"
echo "   - Streamlit PID: $STREAMLIT_PID"
echo ""
echo "🌐 View Session available at:"
echo "   http://localhost:$STREAMLIT_PORT"
echo ""
echo "📊 Events are being generated and can be viewed in real-time"
echo "🛑 Press Ctrl+C to stop"
echo ""

# Wait for both processes
wait
