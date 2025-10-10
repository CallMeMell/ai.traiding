#!/bin/bash
# validate_setup.sh - Validate Dev Live Session Setup
# Run this to check if your environment is ready for the one-click start

echo "=========================================="
echo "🔍 Dev Live Session Setup Validator"
echo "=========================================="
echo ""

ERRORS=0
WARNINGS=0

# Check Python
echo "1. Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo "   ✅ $PYTHON_VERSION"
else
    echo "   ❌ Python 3 not found"
    ERRORS=$((ERRORS + 1))
fi

# Check project structure
echo ""
echo "2. Checking project structure..."
REQUIRED_FILES=(
    "automation/runner.py"
    "tools/view_session_app.py"
    "core/session_store.py"
    ".vscode/tasks.json"
    ".vscode/settings.json"
    "scripts/start_live.sh"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ Missing: $file"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check virtual environment
echo ""
echo "3. Checking virtual environment..."
if [ -d "venv" ]; then
    echo "   ✅ venv exists"
    
    # Check if we can activate it
    if [ -f "venv/bin/activate" ]; then
        echo "   ✅ venv/bin/activate exists"
    else
        echo "   ❌ venv/bin/activate not found"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "   ⚠️  venv not found (will be created on first run)"
    WARNINGS=$((WARNINGS + 1))
fi

# Check data directory
echo ""
echo "4. Checking data directory..."
if [ -d "data" ]; then
    echo "   ✅ data directory exists"
else
    echo "   ⚠️  data directory not found (will be created on first run)"
    WARNINGS=$((WARNINGS + 1))
fi

# Check for conflicting processes
echo ""
echo "5. Checking for conflicting processes..."
if command -v lsof &> /dev/null; then
    if lsof -ti:8501 &> /dev/null; then
        echo "   ⚠️  Port 8501 is already in use"
        echo "      Run: pkill -f streamlit"
        WARNINGS=$((WARNINGS + 1))
    else
        echo "   ✅ Port 8501 is available"
    fi
else
    echo "   ⚠️  lsof not available, cannot check port 8501"
    WARNINGS=$((WARNINGS + 1))
fi

# Summary
echo ""
echo "=========================================="
echo "📊 Validation Summary"
echo "=========================================="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✅ All checks passed! Your setup is ready."
    echo ""
    echo "To start the dev live session, run:"
    echo "  ./scripts/start_live.sh"
    echo ""
    echo "Or use VS Code Task: 'Dev: Live Session'"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo "⚠️  Setup is mostly ready with $WARNINGS warning(s)"
    echo ""
    echo "You can proceed, but review the warnings above."
    exit 0
else
    echo "❌ Setup validation failed with $ERRORS error(s) and $WARNINGS warning(s)"
    echo ""
    echo "Please fix the errors above before running the live session."
    exit 1
fi
