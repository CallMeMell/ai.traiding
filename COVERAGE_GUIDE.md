# Coverage Testing Guide

## Quick Start

### Run Coverage Tests Locally

**Windows (PowerShell):**
```powershell
# Set environment variables
$env:DRY_RUN = "true"
$env:BROKER_NAME = "binance"
$env:BINANCE_BASE_URL = "https://testnet.binance.vision"

# Run tests with coverage
.\venv\Scripts\python.exe -m pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=xml --cov-report=html

# Check coverage percentage
.\venv\Scripts\python.exe -c "import xml.etree.ElementTree as ET; tree = ET.parse('coverage.xml'); coverage = float(tree.getroot().attrib['line-rate']) * 100; print(f'Coverage: {coverage:.1f}%')"
```

**Linux/macOS (Bash):**
```bash
# Set environment variables
export DRY_RUN=true
export BROKER_NAME=binance
export BINANCE_BASE_URL=https://testnet.binance.vision

# Run tests with coverage
python -m pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=xml --cov-report=html

# Check coverage percentage
python -c "import xml.etree.ElementTree as ET; tree = ET.parse('coverage.xml'); coverage = float(tree.getroot().attrib['line-rate']) * 100; print(f'Coverage: {coverage:.1f}%')"
```

### View HTML Coverage Report

After running tests:
```powershell
# Windows
start htmlcov/index.html

# Linux/macOS
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Coverage Configuration

### What's Measured
- **Core system modules** (`system/`)
- **Trading logic** (`binance_integration.py`, `broker_api.py`, `strategy.py`)
- **Configuration** (`config.py`, `utils.py`)
- **Automation core** (`automation/brokers/`, `automation/scheduler.py`, `automation/schemas.py`)
- **RL environment** (production components)

### What's Excluded (via `.coveragerc`)
- Demo and example files (`demo_*.py`, `example_*.py`)
- Test files themselves (`test_*.py`, `*/tests/*`)
- Verification scripts (`verify_*.py`)
- Standalone tools (`backtester.py`, `generate_*.py`)
- Optional features:
  - Machine Learning pipelines (`ml_*.py`, `rl_agent.py`)
  - Dashboards (`dashboard*.py`)
  - Alert system (`alerts/`)
  - Database layer (`db/`)
- Complex orchestration (`automation/runner.py`)

## Coverage Thresholds

### Current Requirements (as of 2025-10-15)
- **Overall Coverage:** ≥ 78%
- **Critical Modules:** ≥ 78%
  - `utils.py`
  - `binance_integration.py`
  - `broker_api.py`

### Why 78%?
- Realistic for current test suite
- Focuses on core production code
- Excludes optional features and demos
- Maintains high quality without being unrealistic

## CI Coverage Checks

The CI runs coverage checks on:
- **Ubuntu-latest** with Python 3.12
- **Windows-latest** with Python 3.12

### Workflow File
`.github/workflows/feature-pr-coverage.yml`

### Jobs
1. **coverage-check**: Runs tests and validates thresholds
2. **test-quality-check**: Validates test count and quality indicators
3. **policy-compliance**: Runs after both checks pass

## Updating Coverage Configuration

### Adding Files to Exclude
Edit `.coveragerc` and add patterns to the `omit` list:
```ini
[run]
omit =
    # Add new pattern here
    new_pattern_*.py
```

### Adjusting Thresholds
If coverage consistently exceeds current thresholds, consider raising them:
1. Edit `.github/workflows/feature-pr-coverage.yml`
2. Update threshold values in:
   - "Check coverage threshold" step
   - "Check critical modules coverage" step
   - "Generate coverage summary" step
   - "Policy compliance summary" step

## Troubleshooting

### Coverage Lower Than Expected
1. Check if new files are included that should be excluded
2. Review `.coveragerc` omit patterns
3. Run `coverage report` to see detailed breakdown
4. Check `coverage.xml` for full details

### Tests Not Discovered
1. Verify test files are in `tests/` directory
2. Check test files follow naming convention (`test_*.py`)
3. Ensure test functions start with `test_`
4. Review `pytest.ini` configuration

### Coverage Not Generated
1. Ensure `pytest-cov` is installed
2. Check `--cov=.` flag is used
3. Verify `.coveragerc` file is present
4. Look for syntax errors in `.coveragerc`

## Best Practices

### Writing Tests
- **Focus on core functionality** over edge cases
- **Use fixtures** for common test setup (see `tests/conftest.py`)
- **Mock external dependencies** (API calls, file I/O)
- **Test error handling** as well as happy paths

### Maintaining Coverage
- Add tests when adding new features
- Update tests when modifying existing code
- Review coverage reports before submitting PRs
- Don't artificially inflate coverage with meaningless tests

### Excluding Code from Coverage
Use `# pragma: no cover` for code that's intentionally not tested:
```python
if __name__ == "__main__":  # pragma: no cover
    main()
```

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [coverage.py documentation](https://coverage.readthedocs.io/)
- Project-specific: `CI_COVERAGE_FIX_SUMMARY.md`
