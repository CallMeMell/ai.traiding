#!/bin/bash
# setup_live.sh - Live Trading Setup Wizard Wrapper (Bash)
# Note: Windows Credential Manager is not available on Linux/macOS
# This script uses keyring with system keychain

set -e

echo "=========================================="
echo "🔐 Live Trading Setup Wizard"
echo "=========================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed!"
    echo "   Please install Python 3.8+ from your package manager"
    exit 1
fi

# Set working directory to project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$PROJECT_ROOT"

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Upgrade pip
echo "📦 Upgrading pip..."
./venv/bin/python -m pip install --upgrade pip --quiet

# Install required packages
echo "📦 Installing required packages (keyring, pyyaml, python-dotenv)..."
./venv/bin/python -m pip install keyring pyyaml python-dotenv requests --quiet

if [ $? -ne 0 ]; then
    echo "❌ Failed to install required packages"
    exit 1
fi

echo ""
echo "✅ Environment ready"
echo ""

# Run setup wizard
echo "Starting setup wizard..."
echo ""
./venv/bin/python scripts/setup_live.py

exit_code=$?
echo ""

if [ $exit_code -eq 0 ]; then
    echo "=========================================="
    echo "✅ Setup wizard completed successfully"
    echo "=========================================="
else
    echo "=========================================="
    echo "❌ Setup wizard failed or was cancelled"
    echo "=========================================="
fi

exit $exit_code
