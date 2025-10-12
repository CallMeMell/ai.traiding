# 🧪 Tests Directory

This directory contains the test suite for the AI Trading Bot.

## Quick Start

```powershell
# Run all tests
python -m pytest tests/ -v

# Run without Binance tests (no API keys needed)
python -m pytest tests/ -k "not binance" -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

## Test Files

- **test_config.py** - Configuration manager tests (10 tests)
- **test_adapters.py** - Adapter base tests (9 tests)
- **test_binance_adapter.py** - Binance adapter tests (21 tests)
- **test_runner_smoke.py** - Runner smoke tests (7 tests) ⭐
- **test_view_session_smoke.py** - View session smoke tests (10 tests) ⭐
- **test_schema_validators.py** - Schema validation tests (17 tests) ⭐
- **test_logger.py** - Logger system tests (17 tests) ⭐
- **test_integration.py** - System integration tests (8 tests)
- **test_monitoring.py** - SLO monitoring tests (15 tests)
- **test_orchestrator.py** - Orchestrator tests (13 tests)

## Coverage

**106+ tests covering:**
- ✅ Configuration Management
- ✅ Automation Runner
- ✅ Session Store & View
- ✅ Schema Validation
- ✅ Logging System
- ✅ Adapters
- ✅ Integration
- ✅ Orchestration
- ✅ Monitoring

## Full Documentation

See **[TESTING_GUIDE.md](../TESTING_GUIDE.md)** for complete testing documentation.
