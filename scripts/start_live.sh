#!/bin/bash
# start_live.sh - One-click Dev Live Session Launcher
# Starts Automation Runner (Dry-Run) + Streamlit View Session

set -e

echo "=========================================="
echo "🚀 Starting Dev Live Session"
echo "=========================================="

# Pre-flight checks
echo "🔍 Running pre-flight checks..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed!"
    echo "   Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python $PYTHON_VERSION detected"

# Set working directory to project root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"
echo "📁 Project root: $PROJECT_ROOT"

# Verify we're in the correct directory
if [ ! -f "automation/runner.py" ]; then
    echo "❌ Error: Cannot find automation/runner.py"
    echo "   Please run this script from the project root or scripts directory"
    exit 1
fi
echo "✅ Project structure validated"

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to create virtual environment"
        echo "   Please ensure python3-venv is installed"
        echo "   Ubuntu/Debian: sudo apt-get install python3-venv"
        exit 1
    fi
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate venv
echo "🔧 Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to activate virtual environment"
    exit 1
fi
echo "✅ Virtual environment activated"

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip --quiet 2>&1 | grep -v "WARNING: There was an error checking" || true

# Install dependencies
echo "📦 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet 2>&1 | grep -v "WARNING: There was an error checking" || echo "⚠️  Some requirements.txt packages may have failed (non-critical)"
fi

# Install Streamlit and required packages
echo "📦 Installing Streamlit and visualization packages..."
pip install streamlit plotly pandas requests python-dotenv pydantic jsonschema --quiet 2>&1 | grep -v "WARNING: There was an error checking" || true
echo "✅ All packages installed"

# Set environment variables for DRY_RUN
export DRY_RUN=true
export BROKER_NAME=binance
export BINANCE_BASE_URL=https://testnet.binance.vision

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo "=========================================="
echo ""
echo "ℹ️  Configuration:"
echo "   - DRY_RUN: true (no real trading)"
echo "   - BROKER: binance (testnet)"
echo "   - Events: data/session/events.jsonl"
echo ""
echo "Starting processes in parallel..."
echo "- Automation Runner (Dry-Run mode)"
echo "- Streamlit View Session (http://localhost:8501)"
echo ""
echo "💡 Tip: Wait 5-10 seconds for processes to start"
echo "🛑 Press Ctrl+C to stop all processes"
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
