#!/bin/bash
# start_live.sh - One-click Dev Live Session Launcher
# Starts Automation Runner (Dry-Run) + Streamlit View Session

set -e

echo "=========================================="
echo "🚀 Starting Dev Live Session"
echo "=========================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed!"
    exit 1
fi

# Set working directory to project root
cd "$(dirname "$0")/.."

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "📦 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet || echo "⚠️  Warning: Some requirements.txt packages failed"
fi

# Install Streamlit and required packages
echo "📦 Installing Streamlit and visualization packages..."
pip install streamlit plotly pandas requests python-dotenv pydantic jsonschema --quiet

# Set environment variables for DRY_RUN
export DRY_RUN=true
export BROKER_NAME=binance
export BINANCE_BASE_URL=https://testnet.binance.vision

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo "=========================================="
echo ""
echo "Starting processes in parallel..."
echo "- Automation Runner (Dry-Run mode)"
echo "- Streamlit View Session (http://localhost:8501)"
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
streamlit run tools/view_session_app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true &
STREAMLIT_PID=$!

echo ""
echo "✅ Both processes started!"
echo "   - Automation Runner PID: $RUNNER_PID"
echo "   - Streamlit PID: $STREAMLIT_PID"
echo ""
echo "🌐 View Session available at:"
echo "   http://localhost:8501"
echo ""
echo "📊 Events are being generated and can be viewed in real-time"
echo "🛑 Press Ctrl+C to stop"
echo ""

# Wait for both processes
wait
