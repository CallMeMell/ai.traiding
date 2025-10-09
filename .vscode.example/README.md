# VSCode Configuration

This directory contains example VSCode configuration files for optimal development experience with the Trading Bot project.

## Setup

Copy these files to a `.vscode` directory in your project root:

```bash
# Linux/Mac
cp -r .vscode.example .vscode

# Windows
xcopy .vscode.example .vscode /E /I
```

Or manually create a `.vscode` directory and copy the files.

## Files

- **settings.json** - Python environment, linting, and editor settings
- **launch.json** - Debug configurations for dashboard, bot, and tests

## Debug Configurations

Available debug configurations in VSCode (F5):

1. **Python: Dashboard Demo** - Run programmatic dashboard demo
2. **Python: Web Dashboard** - Start Flask web dashboard
3. **Python: Main Trading Bot** - Run main trading bot
4. **Python: Generate Sample Trades** - Create test data
5. **Python: System Tests** - Run system validation tests

## Usage

1. Open the project in VSCode
2. Copy configuration files to `.vscode/`
3. Press F5 and select a configuration
4. Or use Run and Debug panel (Ctrl+Shift+D)

## Note

The `.vscode` directory is gitignored to allow for personal configurations.
These example files provide a good starting point.
