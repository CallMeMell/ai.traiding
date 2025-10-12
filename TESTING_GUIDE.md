# 🧪 Testing Guide - AI Trading Bot

**Comprehensive testing documentation for the AI Trading Bot**

This guide documents the test structure, how to run tests, and what is covered.

---

## 📊 Test Overview

The AI Trading Bot has a comprehensive test suite with **100+ unit, smoke, and integration tests** covering all core modules.

### Test Statistics

- **Total Tests**: 106+ tests
- **Test Framework**: pytest
- **Code Coverage**: Core modules
- **Test Types**: Unit, Smoke, Integration, E2E

### Test Files

```
tests/
├── conftest.py                      # Pytest configuration & fixtures
├── test_config.py                   # Configuration manager tests (10 tests)
├── test_adapters.py                 # Adapter base tests (9 tests)
├── test_binance_adapter.py          # Binance adapter tests (21 tests)
├── test_runner_smoke.py             # Runner smoke tests (7 tests) ⭐ NEW
├── test_view_session_smoke.py       # View session smoke tests (10 tests) ⭐ NEW
├── test_schema_validators.py        # Schema validation tests (17 tests) ⭐ NEW
├── test_logger.py                   # Logger system tests (17 tests) ⭐ NEW
├── test_integration.py              # System integration tests (8 tests)
├── test_monitoring.py               # SLO monitoring tests (15 tests)
└── test_orchestrator.py             # Orchestrator tests (13 tests)
```

---

## 🚀 Running Tests

### Prerequisites

1. **Install pytest**:
   ```powershell
   pip install pytest pytest-cov
   ```

2. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

### Run All Tests

```powershell
# Run all tests in tests/ directory
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ --cov=. --cov-report=html

# Run without Binance tests (no API keys required)
python -m pytest tests/ -k "not binance" -v
```

### Run Specific Test Files

```powershell
# Run runner smoke tests
python -m pytest tests/test_runner_smoke.py -v

# Run view session tests
python -m pytest tests/test_view_session_smoke.py -v

# Run schema validator tests
python -m pytest tests/test_schema_validators.py -v

# Run logger tests
python -m pytest tests/test_logger.py -v
```

### Run by Test Category

```powershell
# Run only unit tests
python -m pytest tests/ -m unit -v

# Run only integration tests
python -m pytest tests/ -m integration -v

# Run slow tests
python -m pytest tests/ -m slow -v
```

### Windows PowerShell Examples

```powershell
# Using venv directly (Windows-first approach)
.\venv\Scripts\python.exe -m pytest tests/ -v

# With python-dotenv for .env loading
dotenv -f .env --override run python -m pytest tests/ -v

# In VS Code: Ctrl+Shift+P -> "Tasks: Run Task" -> "Test: All Tests"
```

---

## 📚 Test Categories

### 1. Unit Tests ✅

**Purpose**: Test individual components in isolation

- **test_config.py**: Configuration management
  - Loading from environment variables
  - Loading from JSON files
  - Validation and type conversion
  
- **test_logger.py**: Logging system
  - Log level configuration
  - File rotation
  - Structured JSON logging
  - Multiple handlers
  
- **test_schema_validators.py**: Schema validation
  - Event schema validation
  - Summary schema validation
  - Lenient vs strict validation
  - Pydantic model validation

### 2. Smoke Tests 🔥

**Purpose**: Verify critical functionality works end-to-end

- **test_runner_smoke.py**: Automation runner
  - Initialization without errors
  - DRY_RUN mode execution
  - Event generation
  - Summary generation
  - No API keys required
  
- **test_view_session_smoke.py**: Session viewing
  - Reading events from session store
  - Reading summaries
  - Calculating metrics (ROI, win rate)
  - Filtering by type and phase
  - Empty data handling

### 3. Integration Tests 🔗

**Purpose**: Test component interactions

- **test_integration.py**: Full system integration
  - Config with orchestrator
  - Monitoring with orchestrator
  - Error recovery
  - End-to-end scenarios
  
- **test_adapters.py**: Adapter system
  - Adapter factory
  - Adapter registration
  - Mock adapters

### 4. System Tests 🏗️

**Purpose**: Test entire subsystems

- **test_orchestrator.py**: System orchestration
  - Phase execution
  - Health checks
  - DRY_RUN mode
  - Cleanup
  
- **test_monitoring.py**: SLO monitoring
  - SLO definitions
  - Metric collection
  - SLO status tracking
  - Breach detection

---

## 🎯 Test Coverage

### Core Modules Covered

✅ **Configuration Management** (`system/config/`)
- Environment variable loading
- File-based configuration
- Validation and type conversion

✅ **Automation Runner** (`automation/runner.py`)
- Phase execution (data, strategy, API)
- Event generation
- DRY_RUN mode
- Heartbeat monitoring

✅ **Session Store** (`core/session_store.py`)
- Event appending and reading
- Summary writing and reading
- ROI calculation
- File operations

✅ **Schema Validation** (`automation/schemas.py`, `automation/validate.py`)
- Event schema (Pydantic)
- Summary schema
- Lenient/strict validation
- Metrics and order data

✅ **Logging System** (`system/log_system/`)
- Multi-level logging
- File rotation
- JSON structured logs
- Multiple handlers

✅ **Adapters** (`system/adapters/`)
- Base adapter interface
- Adapter factory
- Binance adapter (testnet)

✅ **Orchestration** (`system/orchestrator.py`)
- Phase management
- Health checks
- Error recovery

✅ **Monitoring** (`system/monitoring/`)
- SLO definitions
- Metric collection
- Compliance tracking

---

## 🔧 Writing Tests

### Test Structure

Tests follow pytest conventions:

```python
"""
test_my_module.py - My Module Tests
================================
Unit tests for my module.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from my_module import MyClass


class TestMyClass:
    """Test MyClass functionality."""
    
    @pytest.fixture
    def my_fixture(self):
        """Set up test fixture."""
        # Setup code
        yield resource
        # Teardown code
    
    def test_my_feature(self, my_fixture):
        """Test my feature."""
        # Arrange
        obj = MyClass()
        
        # Act
        result = obj.do_something()
        
        # Assert
        assert result == expected_value
```

### Best Practices

1. **Use Descriptive Names**: `test_runner_generates_events_in_dry_run_mode`
2. **Follow AAA Pattern**: Arrange, Act, Assert
3. **One Assertion Per Test** (when possible)
4. **Use Fixtures for Setup/Teardown**
5. **Mock External Dependencies**
6. **Test Both Success and Failure Cases**
7. **Use Parametrize for Multiple Inputs**

### Example: Parametrized Test

```python
@pytest.mark.parametrize("initial,current,expected_roi", [
    (10000, 10500, 5.0),
    (10000, 9500, -5.0),
    (10000, 10000, 0.0),
])
def test_roi_calculation(initial, current, expected_roi):
    """Test ROI calculation with various inputs."""
    store = SessionStore()
    roi = store.calculate_roi(initial, current)
    assert abs(roi - expected_roi) < 0.01
```

---

## 🐛 Debugging Tests

### Run Single Test

```powershell
# Run specific test by name
python -m pytest tests/test_runner_smoke.py::TestRunnerSmoke::test_runner_initialization -v

# Run with full output
python -m pytest tests/test_runner_smoke.py::TestRunnerSmoke::test_runner_initialization -v -s
```

### View Test Output

```powershell
# Show print statements
python -m pytest tests/ -v -s

# Show full error traceback
python -m pytest tests/ --tb=long

# Stop at first failure
python -m pytest tests/ -x
```

### Debug with pdb

```python
def test_my_feature():
    """Test my feature."""
    import pdb; pdb.set_trace()  # Add breakpoint
    result = my_function()
    assert result == expected
```

---

## ✅ Continuous Integration

Tests run automatically on:
- Pull requests
- Commits to main branch
- Manual triggers

### CI Configuration

Tests are configured in `.github/workflows/` for automated testing on GitHub Actions.

---

## 📈 Test Metrics

### Current Coverage

- **Config Manager**: 100% (10/10 tests passing)
- **Automation Runner**: 100% (7/7 smoke tests passing)
- **Session Store/View**: 100% (10/10 smoke tests passing)
- **Schema Validation**: 100% (17/17 tests passing)
- **Logger System**: 100% (17/17 tests passing)
- **Adapters**: ~95% (Binance tests require API keys)
- **Integration**: 100% (8/8 tests passing)
- **Orchestrator**: 100% (13/13 tests passing)
- **Monitoring**: 100% (15/15 tests passing)

### Test Execution Time

- **Unit Tests**: ~5 seconds
- **Smoke Tests**: ~60 seconds (includes runner execution)
- **Integration Tests**: ~10 seconds
- **Full Suite**: ~75 seconds

---

## 🚨 Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'pytest'`
```powershell
# Solution: Install pytest
pip install pytest pytest-cov
```

**Issue**: `ModuleNotFoundError: No module named 'pydantic'`
```powershell
# Solution: Install dependencies
pip install -r requirements.txt
```

**Issue**: Tests fail with `python-binance not installed`
```powershell
# Solution: Skip binance tests OR install python-binance
python -m pytest tests/ -k "not binance" -v
# OR
pip install python-binance
```

**Issue**: Tests fail with missing `.env` file
```powershell
# Solution: Create .env file or set DRY_RUN=true
echo "DRY_RUN=true" > .env
```

---

## 📝 Test Documentation

Each test file includes:
- Module docstring explaining purpose
- Class docstrings for test groups
- Individual test docstrings
- Inline comments for complex logic

Example:
```python
"""
test_runner_smoke.py - Automation Runner Smoke Tests
===================================================
Smoke tests to verify automation runner works end-to-end in DRY_RUN mode.
"""

class TestRunnerSmoke:
    """Smoke tests for automation runner."""
    
    def test_runner_initialization(self):
        """Test runner initializes successfully."""
        # Test implementation
```

---

## 🎓 Further Reading

- [pytest Documentation](https://docs.pytest.org/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [Pydantic Validation](https://docs.pydantic.dev/)

---

## 📞 Support

For questions about testing:
1. Check existing test files for examples
2. Review pytest documentation
3. Open an issue with `[Testing]` tag

---

**Made for Windows ⭐ | PowerShell-First | DRY_RUN Default**
