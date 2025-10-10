# Scripts Directory

Cross-platform Python scripts for automation and development workflows.

## Scripts Overview

### `setup_env.py`
Environment setup script that ensures:
- Required directories exist (`data/session`, `logs`, `config`)
- `.env` file is created from `.env.example` (if not exists)
- Python output is unbuffered for live logs

**Usage:**
```bash
python scripts/setup_env.py
```

### `run_automation.py`
Wrapper for `automation/runner.py` with enhanced features:
- Automatic environment setup
- DRY_RUN=true by default (can be overridden)
- Duration limit support for smoke tests
- Schema validation toggle

**Usage:**
```bash
# Run with default settings (unlimited duration)
python scripts/run_automation.py

# Run for 60 seconds with validation
python scripts/run_automation.py --duration 60 --enable-validation

# Parameters:
#   --duration SECONDS     Duration limit in seconds (optional)
#   --enable-validation    Enable schema validation (optional)
```

### `run_view_session.py`
Wrapper for Streamlit View Session app that:
- Ensures environment is set up
- Auto-installs Streamlit if missing
- Starts Streamlit on port 8501

**Usage:**
```bash
python scripts/run_view_session.py
```

Streamlit will be accessible at `http://localhost:8501`

### `validate_session.py`
Validates session data against schemas:
- Validates all events in `data/session/events.jsonl`
- Validates summary in `data/session/summary.json`
- Prints validation results and statistics
- Returns exit code 0 if valid, non-zero if invalid

**Usage:**
```bash
python scripts/validate_session.py
```

## VS Code Integration

These scripts are integrated into VS Code tasks (`.vscode/tasks.json`):
- **Install Dev Deps** - Sets up virtual environment
- **Run: Automation Runner (Dry-Run)** - Uses `run_automation.py`
- **Run: View Session (Streamlit)** - Uses `run_view_session.py`
- **Dev: Start All** - Compound task that runs both Runner and View Session

Access via: `Ctrl+Shift+P` → "Tasks: Run Task"

## GitHub Actions Integration

The `session-smoke.yml` workflow uses these scripts:
1. **setup_env.py** - Implicit via imports
2. **run_automation.py** - Main smoke test runner
3. **validate_session.py** - Post-run validation

See `.github/workflows/session-smoke.yml` for workflow configuration.

## Design Principles

1. **Cross-platform**: Pure Python, works on Windows/macOS/Linux
2. **Self-contained**: Minimal external dependencies
3. **DRY_RUN by default**: Safe for CI/local testing
4. **No secrets required**: Works without API keys
5. **Schema validation**: Ensures data integrity
