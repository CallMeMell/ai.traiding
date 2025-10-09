# Installation Guide

This guide will help you install the Multi-Strategy Trading Bot and all its dependencies.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Internet connection for downloading packages

## Quick Start

### Option 1: Using Quick Start Scripts

#### Windows
```batch
quick_start.bat
```

#### Linux/Mac
```bash
chmod +x quick_start.sh
./quick_start.sh
```

### Option 2: Manual Installation

#### 1. Create a Virtual Environment (Recommended)

**Windows:**
```batch
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages:
- **pandas** - Data manipulation and analysis
- **numpy** - Numerical computing
- **python-dotenv** - Environment variable management
- **python-binance** - Binance API integration
- **yfinance** - Yahoo Finance data fetching
- **requests** - HTTP library
- **Flask** - Web dashboard framework
- **matplotlib** - Data visualization
- **plotly** - Interactive charts
- **pytest** - Testing framework

#### 3. Verify Installation

```bash
python3 -c "import pandas, numpy, flask, plotly; print('✓ All core dependencies installed!')"
```

## Troubleshooting

### Error: "Invalid requirement"

If you see an error like:
```
ERROR: Invalid requirement: '```'
```

This means your requirements.txt file is corrupted. Download a fresh copy or ensure the file contains only valid package specifications without markdown code blocks.

### Error: "No module named 'X'"

If you get a module not found error:
1. Ensure you activated the virtual environment
2. Re-run: `pip install -r requirements.txt`
3. Check your Python version: `python --version` (should be 3.8+)

### Network/Timeout Issues

If installation times out:
1. Check your internet connection
2. Try with a longer timeout: `pip install --timeout=300 -r requirements.txt`
3. Use a different PyPI mirror if needed

### Permission Errors

On Linux/Mac, if you get permission errors:
- Use a virtual environment (recommended)
- OR use `pip install --user -r requirements.txt`

## Optional Dependencies

Some features require additional packages. Uncomment the relevant lines in `requirements.txt`:

### Advanced Visualization
```
seaborn>=0.12.0
```

### Alternative Crypto Exchange APIs
```
ccxt>=4.2.0
```

### Advanced Technical Analysis
```
pandas-ta>=0.3.14b
```

### Notifications
```
python-telegram-bot>=20.0
discord-webhook>=1.3.0
```

### Database Support
```
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
```

### Statistical Analysis
```
scipy>=1.10.0
```

## Running the Bot

After successful installation:

### Basic Trading Bot
```bash
python main.py
```

### With Dashboard
```bash
python main_with_dashboard.py
```

### Golden Cross Strategy
```bash
python golden_cross_bot.py
```

### Backtesting
```bash
python backtester.py
```

## For Developers

### Running Tests
```bash
pytest
```

### Install Development Dependencies
If you need to add more packages, edit `requirements.txt` and run:
```bash
pip install -r requirements.txt
```

## Support

If you encounter any issues:
1. Check the [README.md](README.md) for general information
2. Review the [FAQ.md](FAQ.md) for common questions
3. Ensure all dependencies are correctly installed
4. Check the logs in the `logs/` directory

---

**Happy Trading! 🚀📈**
