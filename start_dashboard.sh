#!/bin/bash
# Start Trading Bot Dashboard
# ===========================

echo "======================================================================"
echo "  Trading Bot Dashboard Starter"
echo "======================================================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 not found!"
    echo "Please install Python3 or activate your virtual environment."
    exit 1
fi

# Install Flask if not installed
if ! python3 -c "import flask" &> /dev/null; then
    echo "Flask is being installed..."
    pip3 install Flask
fi

echo ""
echo "Starting Dashboard Server..."
echo "Dashboard URL: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "======================================================================"
echo ""

python3 dashboard.py
