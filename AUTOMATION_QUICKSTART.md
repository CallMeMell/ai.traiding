# Automation Quick Start Guide

## 🚀 Quick Start - Local Development

### One-Click Start in VS Code

1. Open VS Code
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
3. Type "Tasks: Run Task"
4. Select **"Dev: Start All"**

This will:
- ✅ Start Automation Runner in one terminal (DRY_RUN mode)
- ✅ Start View Session Dashboard in another terminal (port 8501)
- ✅ Auto-forward port 8501 in Codespaces

### Manual Script Usage

```bash
# Setup environment
python scripts/setup_env.py

# Run automation (60 seconds with validation)
python scripts/run_automation.py --duration 60 --enable-validation

# Start View Session dashboard
python scripts/run_view_session.py

# Validate session data
python scripts/validate_session.py
```

## 🔬 CI Smoke Testing - GitHub Actions

### Trigger Manually

1. Go to **Actions** tab in GitHub
2. Select **"Session Smoke Test"**
3. Click **"Run workflow"**
4. Configure:
   - `duration_secs`: 60 (default)
   - `mode`: dry_run (default)
5. Click **"Run workflow"**

### Automatic on PRs (Optional)

Uncomment these lines in `.github/workflows/session-smoke.yml`:

```yaml
pull_request:
  types: [opened, synchronize]
  paths:
    - 'automation/**'
    - 'core/**'
    - 'scripts/**'
```

## 📊 What Gets Created

After running automation, you'll see:

```
data/session/
├── events.jsonl      # All events (runner_start, phase_start, etc.)
└── summary.json      # Session summary with stats
```

### Sample Output

**Setup Environment:**
```
============================================================
Setting up environment...
============================================================
✓ Directory ready: data/session
✓ Directory ready: logs
✓ Directory ready: config
✓ .env file already exists
✓ Python output set to unbuffered mode
============================================================
✓ Environment setup complete!
============================================================
```

**Validation:**
```
======================================================================
Session Data Validation
======================================================================

Validating events: data/session/events.jsonl
✓ All events valid (24/24)

Validating summary: data/session/summary.json
✓ Summary valid

Session Summary Statistics:
  Session ID: 7cbd1480-7a5e-42e8-8bf2-3b7144f1e8c5
  Status: success
  Phases completed: 3/3
  Initial capital: $10000.00
  Current equity: $10150.00

Totals:
  Trades: 10
  Wins: 6
  Losses: 4

======================================================================
Validation PASSED
```

## 🔒 Safety Features

- ✅ **DRY_RUN=true by default** - No real trades
- ✅ **No API keys required** - Works in test mode
- ✅ **Schema validation** - Ensures data integrity
- ✅ **Cross-platform** - Works on Windows/macOS/Linux

## 🎯 VS Code Tasks Available

Access via `Terminal → Run Task...`:

1. **Install Dev Deps** - Setup virtual environment
2. **Run: Automation Runner (Dry-Run)** - Start runner
3. **Run: View Session (Streamlit)** - Start dashboard
4. **Dev: Start All** - ⭐ Start both runner + dashboard

## 📦 GitHub Actions Artifacts

After CI run completes:

1. Go to the workflow run
2. Scroll to **Artifacts** section
3. Download **session-data** artifact
4. Contains:
   - `events.jsonl` - All events
   - `summary.json` - Session summary
   - `README.txt` - Artifact info

## 🧪 Running Tests

```bash
# Test workflow syntax
python test_workflow_syntax.py

# Run integration tests
python test_automation_integration.py
```

Expected output:
```
✓ PASS: Setup Environment
✓ PASS: Run Automation
✓ PASS: Validate Session
✓ PASS: DRY_RUN Default
✓ PASS: No Secrets Required

Total: 5/5 tests passed
```

## 🛠️ Troubleshooting

### "streamlit not found"

```bash
pip install streamlit plotly
```

Or let the script auto-install:
```bash
python scripts/run_view_session.py
```

### "pydantic not found"

```bash
pip install pydantic
```

### View Session not loading

Check that:
1. Port 8501 is not in use
2. Streamlit is installed
3. `tools/view_session_app.py` exists

### Validation fails

Check that automation has run at least once:
```bash
ls -la data/session/
```

Should show `events.jsonl` and `summary.json`.

## 📚 Documentation

- **scripts/README.md** - Detailed script documentation
- **AUTOMATION_SETUP_VERIFICATION.md** - Requirements verification
- **README.md** - Main project documentation
- **PROGRESS.md** - Project progress tracker

## 🎉 Example Workflow

Complete workflow from start to finish:

```bash
# 1. Setup environment
python scripts/setup_env.py

# 2. Run automation for 30 seconds
python scripts/run_automation.py --duration 30 --enable-validation

# 3. Validate results
python scripts/validate_session.py

# 4. Start dashboard (in separate terminal)
python scripts/run_view_session.py
# Visit http://localhost:8501
```

Or in VS Code:
1. Run Task: "Dev: Start All"
2. Watch both terminals
3. Open http://localhost:8501

That's it! 🎉
