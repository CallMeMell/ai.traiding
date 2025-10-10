# Changelog

All notable changes to the ai.traiding system will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- 🚀 **12h Pre-Execution System** - Complete system orchestration
  - Master orchestrator with health checks and recovery
  - Adapter system for broker API abstraction
  - Centralized logging with rotation (10MB, 5 backups)
  - Structured error handling with custom exceptions
  - CI/CD pipelines (GitHub Actions)
  - Nightly dry-run jobs
  - Comprehensive test suite (20+ tests)
  - System monitoring and health checks
  
- 📦 **System Module** (`system/`)
  - `orchestrator.py` - Master system orchestrator
  - `adapters/` - Broker adapter abstraction layer
  - `logging/` - Centralized logging system
  - `errors/` - Custom exception hierarchy
  - `monitoring/` - SLO and metrics (planned)
  - `config/` - Configuration management (planned)
  
- 🧪 **Test Infrastructure** (`tests/`)
  - Unit tests for orchestrator
  - Unit tests for adapters
  - Integration test fixtures
  - Pytest configuration
  - Coverage reporting
  
- 🔄 **CI/CD Workflows** (`.github/workflows/`)
  - `ci.yml` - Continuous integration (Windows + Linux matrix)
  - `nightly.yml` - Nightly dry-run jobs
  
- 📜 **Scripts**
  - `nightly_run.py` - Python nightly runner
  - `nightly_run.ps1` - PowerShell nightly runner (Windows-first)
  
- 📚 **Documentation**
  - `SYSTEM_12H_IMPLEMENTATION.md` - Implementation plan
  - `CHANGELOG.md` - This changelog
  - `CONTRIBUTING.md` - Complete contribution guidelines with QA processes
  - `RELEASE-NOTES.md` - Release versioning and notes
  - README.md: ENV variable reference table (40+ variables documented)
  - Inline code documentation

### Changed
- Enhanced `.gitignore` for better system file exclusion
- README.md: Added comprehensive ENV variable table with examples

### Fixed
- 🐛 **Nightly dry-run workflow** - Fixed `nightly_run.py` to properly generate `summary.json`
  - Changed from using `SystemOrchestrator` to `AutomationRunner` for actual workflow execution
  - Added explicit artifact upload for `summary.json` in GitHub Actions workflow
  - Verified end-to-end: summary.json is now properly generated and uploaded as artifact

### Fixed
- N/A

### Security
- DRY_RUN default to `true` for safety
- No secrets in code (use environment variables)

---

## [1.0.0] - 2025-10-10 (Baseline)

### Added
- Initial project structure
- Core automation system (`automation/`)
- Session store and event tracking (`core/`)
- View session dashboard (`tools/`)
- Binance API integration
- Multiple trading strategies
- Backtesting engine
- Live trading support with preflight checks
- PowerShell-first Windows development

---

## Release Types

- **Major (X.0.0)**: Breaking changes, major feature additions
- **Minor (0.X.0)**: New features, non-breaking changes
- **Patch (0.0.X)**: Bug fixes, minor improvements

---

**Made for Windows ⭐ | PowerShell-First | DRY_RUN Default**
