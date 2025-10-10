#!/bin/bash
# start_automated_workflow.sh - Start Automated Workflow System
# ================================================================

echo ""
echo "======================================================================"
echo "  AUTOMATED TRADING BOT WORKFLOW"
echo "======================================================================"
echo "  Preparing AI trading bot for real money deployment"
echo "======================================================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if dependencies are installed
echo "Checking dependencies..."
python3 -c "import pandas, numpy, flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "WARNING: Some dependencies missing. Installing..."
    pip3 install -r requirements.txt
fi

echo ""
echo "Starting automated workflow..."
echo ""

# Start the workflow
python3 automated_workflow.py

echo ""
echo "======================================================================"
echo "  Workflow execution completed"
echo "======================================================================"
echo ""
