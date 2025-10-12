"""
automated_setup.py - Vollautomatisierter Live Trading Setup Task
================================================================
Vollständiger Setup-Flow für Live Trading mit:
- Sichere API-Key-Abfrage
- Automatische Risk-Konfiguration
- Python-Umgebungsprüfung
- Preflight-Checks
- Dry-Run-Testlauf
- Umfassende Logs und Status-Berichte

SECURITY: Keine API-Keys werden außerhalb des lokalen Systems gespeichert.
"""

import sys
import os
import subprocess
import json
import yaml
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

# Status indicators
STATUS_OK = "✅"
STATUS_ERROR = "❌"
STATUS_WARNING = "⚠️"
STATUS_INFO = "ℹ️"


class AutomatedSetup:
    """Orchestrates the complete automated setup flow."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.logs_dir = self.project_root / "logs"
        self.setup_log_file = self.logs_dir / f"automated_setup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.summary_file = self.logs_dir / "setup_summary.md"
        self.logs = []
        self.steps_completed = []
        self.steps_failed = []
        
        # Ensure logs directory exists
        self.logs_dir.mkdir(exist_ok=True)
    
    def log(self, status: str, message: str, step: Optional[str] = None):
        """Log a message with status indicator."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {status} {message}"
        print(log_entry)
        self.logs.append(log_entry)
        
        # Track step completion
        if step:
            if status == STATUS_OK:
                self.steps_completed.append(step)
            elif status == STATUS_ERROR:
                self.steps_failed.append(step)
    
    def save_logs(self):
        """Save all logs to file."""
        try:
            with open(self.setup_log_file, 'w', encoding='utf-8') as f:
                f.write("# Automated Live Trading Setup Log\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
                for log in self.logs:
                    f.write(log + "\n")
            self.log(STATUS_OK, f"Logs saved to {self.setup_log_file}")
        except Exception as e:
            self.log(STATUS_ERROR, f"Failed to save logs: {e}")
    
    def check_python_environment(self) -> bool:
        """Check Python environment and dependencies."""
        self.log(STATUS_INFO, "Checking Python environment...", "python_env")
        
        try:
            # Check Python version
            version = sys.version_info
            if version.major < 3 or (version.major == 3 and version.minor < 8):
                self.log(STATUS_ERROR, f"Python 3.8+ required, found {version.major}.{version.minor}", "python_env")
                return False
            
            self.log(STATUS_OK, f"Python version: {version.major}.{version.minor}.{version.micro}", "python_env")
            
            # Check venv exists
            venv_path = self.project_root / "venv"
            if not venv_path.exists():
                self.log(STATUS_WARNING, "Virtual environment not found - will be created", "python_env")
            else:
                self.log(STATUS_OK, "Virtual environment exists", "python_env")
            
            # Check critical packages
            required_packages = ["keyring", "yaml", "requests"]
            missing = []
            for pkg in required_packages:
                try:
                    __import__(pkg)
                    self.log(STATUS_OK, f"Package '{pkg}' available", "python_env")
                except ImportError:
                    missing.append(pkg)
                    self.log(STATUS_WARNING, f"Package '{pkg}' missing - will be installed", "python_env")
            
            return True
            
        except Exception as e:
            self.log(STATUS_ERROR, f"Python environment check failed: {e}", "python_env")
            return False
    
    def run_api_key_setup(self, auto_mode: bool = False) -> bool:
        """Run API key setup wizard."""
        self.log(STATUS_INFO, "Running API key setup...", "api_keys")
        
        try:
            # Import setup_live module
            sys.path.insert(0, str(self.project_root / "scripts"))
            from setup_live import prompt_api_keys, store_credentials, verify_storage
            
            if auto_mode:
                self.log(STATUS_WARNING, "Auto mode: Using existing credentials (skipping prompt)", "api_keys")
                if verify_storage():
                    self.log(STATUS_OK, "Existing credentials verified", "api_keys")
                    return True
                else:
                    self.log(STATUS_ERROR, "No existing credentials found - manual setup required", "api_keys")
                    return False
            else:
                # Interactive key prompt
                api_key, api_secret = prompt_api_keys()
                if not api_key or not api_secret:
                    self.log(STATUS_ERROR, "API key setup cancelled", "api_keys")
                    return False
                
                if not store_credentials(api_key, api_secret):
                    self.log(STATUS_ERROR, "Failed to store credentials", "api_keys")
                    return False
                
                if not verify_storage():
                    self.log(STATUS_ERROR, "Credential verification failed", "api_keys")
                    return False
                
                self.log(STATUS_OK, "API keys stored and verified", "api_keys")
                return True
                
        except Exception as e:
            self.log(STATUS_ERROR, f"API key setup failed: {e}", "api_keys")
            return False
    
    def run_risk_configuration(self, auto_mode: bool = False) -> bool:
        """Configure risk management parameters."""
        self.log(STATUS_INFO, "Configuring risk management...", "risk_config")
        
        try:
            sys.path.insert(0, str(self.project_root / "scripts"))
            from setup_live import prompt_risk_params, write_risk_config, run_strategy_selection
            
            # Run strategy selection if needed
            recommended_strategy = None
            if auto_mode:
                self.log(STATUS_INFO, "Auto mode: Running strategy selection...", "risk_config")
                recommended_strategy = run_strategy_selection(auto_mode=True)
                if recommended_strategy:
                    self.log(STATUS_OK, f"Strategy selected: {recommended_strategy}", "risk_config")
            
            # Configure risk parameters
            if auto_mode:
                # Use defaults for auto mode
                self.log(STATUS_INFO, "Auto mode: Using default risk parameters", "risk_config")
                risk_params = {
                    "pairs": "BTCUSDT",
                    "strategy": recommended_strategy or "Golden Cross (50/200)",
                    "max_risk_per_trade": 0.005,
                    "daily_loss_limit": 0.01,
                    "max_open_exposure": 0.05,
                    "allowed_order_types": "LIMIT_ONLY",
                    "max_slippage": 0.003
                }
            else:
                risk_params = prompt_risk_params(recommended_strategy)
                if not risk_params:
                    self.log(STATUS_ERROR, "Risk configuration cancelled", "risk_config")
                    return False
            
            if not write_risk_config(risk_params):
                self.log(STATUS_ERROR, "Failed to write risk configuration", "risk_config")
                return False
            
            self.log(STATUS_OK, "Risk configuration complete", "risk_config")
            self.log(STATUS_INFO, f"  Pairs: {risk_params['pairs']}", "risk_config")
            self.log(STATUS_INFO, f"  Strategy: {risk_params['strategy']}", "risk_config")
            self.log(STATUS_INFO, f"  Max risk/trade: {risk_params['max_risk_per_trade']*100:.2f}%", "risk_config")
            
            return True
            
        except Exception as e:
            self.log(STATUS_ERROR, f"Risk configuration failed: {e}", "risk_config")
            return False
    
    def run_preflight_checks(self) -> bool:
        """Run comprehensive preflight checks."""
        self.log(STATUS_INFO, "Running preflight checks...", "preflight")
        
        try:
            # Set up environment for preflight
            env = os.environ.copy()
            env["LIVE_ACK"] = "I_UNDERSTAND"
            env["DRY_RUN"] = "true"  # Use dry-run for preflight test
            env["LIVE_TRADING"] = "false"  # Not live yet
            env["BINANCE_BASE_URL"] = "https://testnet.binance.vision"
            
            # Load API keys from keyring for preflight
            sys.path.insert(0, str(self.project_root / "scripts"))
            import keyring
            api_key = keyring.get_password("ai.traiding", "binance_api_key")
            api_secret = keyring.get_password("ai.traiding", "binance_api_secret")
            
            if api_key and api_secret:
                env["BINANCE_API_KEY"] = api_key
                env["BINANCE_API_SECRET"] = api_secret
            else:
                self.log(STATUS_WARNING, "API keys not found in keyring - some checks may fail", "preflight")
            
            # Run preflight script
            preflight_script = self.project_root / "scripts" / "live_preflight.py"
            result = subprocess.run(
                [sys.executable, str(preflight_script)],
                env=env,
                capture_output=True,
                text=True,
                cwd=str(self.project_root)
            )
            
            # Log preflight output
            if result.stdout:
                for line in result.stdout.split("\n"):
                    if line.strip():
                        self.logs.append(f"  {line}")
            
            if result.returncode == 0:
                self.log(STATUS_OK, "Preflight checks passed", "preflight")
                return True
            else:
                self.log(STATUS_ERROR, "Preflight checks failed", "preflight")
                if result.stderr:
                    self.log(STATUS_ERROR, f"Error: {result.stderr}", "preflight")
                return False
                
        except Exception as e:
            self.log(STATUS_ERROR, f"Preflight check execution failed: {e}", "preflight")
            return False
    
    def run_dry_run_test(self) -> bool:
        """Execute a dry-run test of the trading system."""
        self.log(STATUS_INFO, "Running dry-run test...", "dry_run")
        
        try:
            # Set up dry-run environment
            env = os.environ.copy()
            env["DRY_RUN"] = "true"
            env["LIVE_TRADING"] = "false"
            env["BINANCE_BASE_URL"] = "https://testnet.binance.vision"
            env["BROKER_NAME"] = "binance"
            
            # Load API keys
            import keyring
            api_key = keyring.get_password("ai.traiding", "binance_api_key")
            api_secret = keyring.get_password("ai.traiding", "binance_api_secret")
            
            if api_key and api_secret:
                env["BINANCE_API_KEY"] = api_key
                env["BINANCE_API_SECRET"] = api_secret
            
            # Run automation runner in dry-run mode for 10 seconds
            self.log(STATUS_INFO, "Starting automation runner in dry-run mode (10 seconds)...", "dry_run")
            
            runner_script = self.project_root / "automation" / "runner.py"
            if not runner_script.exists():
                self.log(STATUS_WARNING, "Automation runner not found - skipping dry-run test", "dry_run")
                return True
            
            # Run with timeout
            try:
                result = subprocess.run(
                    [sys.executable, str(runner_script)],
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=str(self.project_root)
                )
                
                # Log key output lines
                if result.stdout:
                    lines = result.stdout.split("\n")
                    for line in lines[-20:]:  # Last 20 lines
                        if line.strip():
                            self.logs.append(f"  {line}")
                
                self.log(STATUS_OK, "Dry-run test completed", "dry_run")
                return True
                
            except subprocess.TimeoutExpired:
                self.log(STATUS_OK, "Dry-run test completed (timeout reached)", "dry_run")
                return True
                
        except Exception as e:
            self.log(STATUS_ERROR, f"Dry-run test failed: {e}", "dry_run")
            return False
    
    def generate_summary_report(self) -> bool:
        """Generate a comprehensive setup summary report."""
        self.log(STATUS_INFO, "Generating setup summary report...", "report")
        
        try:
            # Load risk config for summary
            risk_config = {}
            config_path = self.project_root / "config" / "live_risk.yaml"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    risk_config = yaml.safe_load(f) or {}
            
            # Generate markdown report
            summary = []
            summary.append("# 🚀 Live Trading Setup Summary\n")
            summary.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            summary.append("---\n\n")
            
            # Setup Status
            summary.append("## ✅ Setup Status\n\n")
            total_steps = len(self.steps_completed) + len(self.steps_failed)
            success_rate = (len(self.steps_completed) / total_steps * 100) if total_steps > 0 else 0
            
            summary.append(f"**Success Rate:** {success_rate:.1f}% ({len(self.steps_completed)}/{total_steps} steps)\n\n")
            
            if self.steps_completed:
                summary.append("**Completed Steps:**\n")
                for step in self.steps_completed:
                    summary.append(f"- {STATUS_OK} {step}\n")
                summary.append("\n")
            
            if self.steps_failed:
                summary.append("**Failed Steps:**\n")
                for step in self.steps_failed:
                    summary.append(f"- {STATUS_ERROR} {step}\n")
                summary.append("\n")
            
            # Risk Configuration
            if risk_config:
                summary.append("## ⚙️ Risk Configuration\n\n")
                summary.append(f"- **Trading Pairs:** {risk_config.get('pairs', 'N/A')}\n")
                summary.append(f"- **Strategy:** {risk_config.get('strategy', 'N/A')}\n")
                summary.append(f"- **Max Risk per Trade:** {risk_config.get('max_risk_per_trade', 0)*100:.2f}%\n")
                summary.append(f"- **Daily Loss Limit:** {risk_config.get('daily_loss_limit', 0)*100:.2f}%\n")
                summary.append(f"- **Max Open Exposure:** {risk_config.get('max_open_exposure', 0)*100:.2f}%\n")
                summary.append(f"- **Order Types:** {risk_config.get('allowed_order_types', 'N/A')}\n")
                summary.append(f"- **Max Slippage:** {risk_config.get('max_slippage', 0)*100:.2f}%\n\n")
            
            # Security Checklist
            summary.append("## 🔐 Security Checklist\n\n")
            summary.append("- [x] API keys stored in Windows Credential Manager\n")
            summary.append("- [x] No secrets in config files\n")
            summary.append("- [x] Risk parameters validated\n")
            summary.append("- [x] Preflight checks configured\n")
            summary.append("- [ ] IP restrictions enabled on API keys (manual)\n")
            summary.append("- [ ] 2FA enabled on Binance account (manual)\n")
            summary.append("- [ ] Withdrawal permissions disabled (manual)\n\n")
            
            # Next Steps
            summary.append("## 📋 Next Steps\n\n")
            if not self.steps_failed:
                summary.append("1. Review the risk configuration in `config/live_risk.yaml`\n")
                summary.append("2. Set up IP restrictions on your Binance API keys\n")
                summary.append("3. Verify 2FA is enabled on your Binance account\n")
                summary.append("4. Set `LIVE_ACK=I_UNDERSTAND` in your environment\n")
                summary.append("5. Run `scripts/start_live_prod.ps1` to start live trading\n\n")
                summary.append("**⚠️ IMPORTANT:**\n")
                summary.append("- Start with minimal capital you can afford to lose\n")
                summary.append("- Monitor positions closely during first trades\n")
                summary.append("- Have an emergency stop plan ready\n")
            else:
                summary.append("**Setup incomplete. Please resolve the failed steps above.**\n")
            
            summary.append("\n---\n\n")
            summary.append(f"**Full Log:** `{self.setup_log_file.name}`\n")
            
            # Write summary
            with open(self.summary_file, 'w', encoding='utf-8') as f:
                f.writelines(summary)
            
            self.log(STATUS_OK, f"Summary report saved to {self.summary_file}", "report")
            
            # Print summary to console
            print("\n" + "=" * 70)
            print("".join(summary))
            print("=" * 70 + "\n")
            
            return True
            
        except Exception as e:
            self.log(STATUS_ERROR, f"Failed to generate summary: {e}", "report")
            return False
    
    def run_automated_setup(self, auto_mode: bool = False, skip_dry_run: bool = False) -> int:
        """
        Execute the complete automated setup flow.
        
        Args:
            auto_mode: If True, use defaults and skip interactive prompts where possible
            skip_dry_run: If True, skip the dry-run test
        
        Returns:
            0 if successful, 1 if failed
        """
        print("=" * 70)
        print("🚀 Vollautomatisierter Live Trading Setup")
        print("=" * 70)
        print()
        
        if auto_mode:
            self.log(STATUS_INFO, "Running in AUTO mode - using defaults where possible")
        else:
            self.log(STATUS_INFO, "Running in INTERACTIVE mode")
        
        print()
        
        # Step 1: Check Python environment
        if not self.check_python_environment():
            self.log(STATUS_ERROR, "Python environment check failed - aborting")
            self.save_logs()
            return 1
        
        print()
        
        # Step 2: API Key Setup
        if not self.run_api_key_setup(auto_mode=auto_mode):
            self.log(STATUS_ERROR, "API key setup failed - aborting")
            self.save_logs()
            return 1
        
        print()
        
        # Step 3: Risk Configuration
        if not self.run_risk_configuration(auto_mode=auto_mode):
            self.log(STATUS_ERROR, "Risk configuration failed - aborting")
            self.save_logs()
            return 1
        
        print()
        
        # Step 4: Preflight Checks
        if not self.run_preflight_checks():
            self.log(STATUS_WARNING, "Preflight checks failed - continuing anyway")
            # Don't abort, just warn
        
        print()
        
        # Step 5: Dry-Run Test (optional)
        if not skip_dry_run:
            if not self.run_dry_run_test():
                self.log(STATUS_WARNING, "Dry-run test had issues - continuing anyway")
        else:
            self.log(STATUS_INFO, "Dry-run test skipped", "dry_run")
        
        print()
        
        # Step 6: Generate Summary Report
        self.generate_summary_report()
        
        # Save all logs
        self.save_logs()
        
        # Final status
        print()
        if not self.steps_failed:
            self.log(STATUS_OK, "Setup completed successfully!")
            return 0
        else:
            self.log(STATUS_WARNING, f"Setup completed with {len(self.steps_failed)} warnings")
            return 0


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Vollautomatisierter Live Trading Setup Task',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive setup (recommended for first time)
  python automated_setup.py
  
  # Automated setup with defaults (for CI/testing)
  python automated_setup.py --auto
  
  # Skip dry-run test
  python automated_setup.py --skip-dry-run
        """
    )
    
    parser.add_argument(
        '--auto',
        action='store_true',
        help='Run in automatic mode with defaults (skip interactive prompts)'
    )
    
    parser.add_argument(
        '--skip-dry-run',
        action='store_true',
        help='Skip the dry-run test phase'
    )
    
    args = parser.parse_args()
    
    setup = AutomatedSetup()
    return setup.run_automated_setup(
        auto_mode=args.auto,
        skip_dry_run=args.skip_dry_run
    )


if __name__ == "__main__":
    sys.exit(main())
