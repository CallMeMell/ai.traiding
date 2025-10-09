#!/bin/bash
# Start Flask Web Dashboard for Trading Bot
# Linux/Mac Shell Script

echo "============================================================"
echo "Starting Trading Bot Web Dashboard..."
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "Error: Python is not installed"
    echo "Please install Python from https://www.python.org/"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Check if Flask is installed
if ! $PYTHON_CMD -c "import flask" &> /dev/null; then
    echo "Error: Flask is not installed"
    echo "Installing Flask..."
    pip install Flask || pip3 install Flask
    if [ $? -ne 0 ]; then
        echo "Failed to install Flask"
        exit 1
    fi
fi

# Start the dashboard
echo "Starting web dashboard on http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""
$PYTHON_CMD dashboard.py --web
