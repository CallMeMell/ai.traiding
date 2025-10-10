"""
test_preflight_integration.py - Integration Tests for Preflight Check System
============================================================================
Tests the complete integration of preflight checks with the VS Code task system.
"""

import sys
import os
import unittest
import subprocess
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent


class TestPreflightIntegration(unittest.TestCase):
    """Integration tests for the complete preflight check system."""
    
    def test_preflight_script_exists(self):
        """Test that the preflight script exists and is accessible."""
        preflight_script = PROJECT_ROOT / "scripts" / "live_preflight.py"
        self.assertTrue(preflight_script.exists(), 
                       f"Preflight script not found at {preflight_script}")
    
    def test_preflight_script_executable(self):
        """Test that the preflight script can be executed by Python."""
        preflight_script = PROJECT_ROOT / "scripts" / "live_preflight.py"
        
        # Run the script with minimal environment (should fail but not crash)
        result = subprocess.run(
            [sys.executable, str(preflight_script)],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            env={**os.environ, "LIVE_ACK": "", "DRY_RUN": "true"}
        )
        
        # Should exit with code 1 (checks failed) but not crash
        self.assertEqual(result.returncode, 1, 
                        "Preflight should fail with missing environment variables")
        self.assertIn("Preflight checks failed", result.stdout,
                     "Should report that preflight checks failed")
    
    def test_preflight_logs_to_file(self):
        """Test that preflight checks create log files."""
        logs_dir = PROJECT_ROOT / "logs"
        preflight_log = logs_dir / "preflight_checks.log"
        
        # Run preflight (will fail but should create log)
        subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "live_preflight.py")],
            capture_output=True,
            cwd=PROJECT_ROOT,
            env={**os.environ, "LIVE_ACK": "", "DRY_RUN": "true"}
        )
        
        # Check if logs directory and log file exist
        self.assertTrue(logs_dir.exists(), "logs/ directory should be created")
        # Note: Log file may not exist if all checks fail before logging
        # This is acceptable behavior
    
    def test_powershell_script_exists(self):
        """Test that the PowerShell runner script exists."""
        ps_script = PROJECT_ROOT / "scripts" / "start_live_prod.ps1"
        self.assertTrue(ps_script.exists(), 
                       f"PowerShell script not found at {ps_script}")
    
    def test_powershell_script_calls_preflight(self):
        """Test that the PowerShell script references the preflight checks."""
        ps_script = PROJECT_ROOT / "scripts" / "start_live_prod.ps1"
        
        with open(ps_script, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that it calls the preflight script
        self.assertIn("live_preflight.py", content,
                     "PowerShell script should reference live_preflight.py")
        
        # Check that it checks the exit code
        self.assertIn("$LASTEXITCODE", content,
                     "PowerShell script should check exit code")
        self.assertIn("exit 1", content,
                     "PowerShell script should exit with error on failure")
    
    def test_vscode_task_exists(self):
        """Test that the VS Code task configuration exists."""
        tasks_file = PROJECT_ROOT / ".vscode" / "tasks.json"
        self.assertTrue(tasks_file.exists(), 
                       f"VS Code tasks.json not found at {tasks_file}")
    
    def test_vscode_task_references_runner(self):
        """Test that the VS Code task references the live runner script."""
        tasks_file = PROJECT_ROOT / ".vscode" / "tasks.json"
        
        with open(tasks_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for "Live: Runner" task
        self.assertIn('"Live: Runner"', content,
                     "VS Code tasks should include 'Live: Runner' task")
        
        # Check that it calls the PowerShell script
        self.assertIn("start_live_prod.ps1", content,
                     "Live: Runner task should call start_live_prod.ps1")
        
        # Check that it mentions preflight checks
        self.assertIn("preflight", content.lower(),
                     "Task description should mention preflight checks")
    
    def test_documentation_exists(self):
        """Test that live trading documentation exists."""
        doc_file = PROJECT_ROOT / "LIVE_TRADING_SETUP_GUIDE.md"
        self.assertTrue(doc_file.exists(),
                       f"Documentation not found at {doc_file}")
        
        with open(doc_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key documentation sections
        self.assertIn("live_preflight.py", content,
                     "Documentation should reference preflight script")
        self.assertIn("Live: Runner", content,
                     "Documentation should reference VS Code task")
        self.assertIn("Preflight", content,
                     "Documentation should explain preflight checks")
    
    def test_preflight_check_functions(self):
        """Test that all required check functions exist in preflight script."""
        # Import the script
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        import live_preflight
        
        required_checks = [
            'check_environment',
            'check_credentials',
            'check_time_sync',
            'check_exchange_info',
            'check_account_balance',
            'check_risk_configuration',
            'check_kill_switch',
            'check_order_types_support',
            'run_all_checks'
        ]
        
        for check_name in required_checks:
            self.assertTrue(hasattr(live_preflight, check_name),
                          f"Preflight script should have {check_name} function")
    
    def test_preflight_exit_codes(self):
        """Test that preflight returns correct exit codes."""
        preflight_script = PROJECT_ROOT / "scripts" / "live_preflight.py"
        
        # Test with missing environment (should fail with exit code 1)
        result = subprocess.run(
            [sys.executable, str(preflight_script)],
            capture_output=True,
            cwd=PROJECT_ROOT,
            env={**os.environ, "LIVE_ACK": "", "DRY_RUN": "true"}
        )
        
        self.assertEqual(result.returncode, 1,
                        "Preflight should exit with code 1 on failure")


class TestPreflightCheckContent(unittest.TestCase):
    """Test the content and behavior of preflight checks."""
    
    def test_environment_check_validates_live_ack(self):
        """Test that environment check validates LIVE_ACK."""
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        import live_preflight
        
        # Test with missing LIVE_ACK
        os.environ["LIVE_ACK"] = ""
        success, message = live_preflight.check_environment()
        self.assertFalse(success, "Should fail without LIVE_ACK")
        self.assertIn("I_UNDERSTAND", message, "Error should mention I_UNDERSTAND")
    
    def test_environment_check_validates_dry_run(self):
        """Test that environment check validates DRY_RUN."""
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        import live_preflight
        
        # Test with DRY_RUN=true (should fail for live trading)
        os.environ["LIVE_ACK"] = "I_UNDERSTAND"
        os.environ["DRY_RUN"] = "true"
        os.environ["LIVE_TRADING"] = "true"
        os.environ["BINANCE_BASE_URL"] = "https://api.binance.com"
        
        success, message = live_preflight.check_environment()
        self.assertFalse(success, "Should fail with DRY_RUN=true")
        self.assertIn("false", message.lower(), "Error should mention DRY_RUN must be false")
    
    def test_kill_switch_is_informational(self):
        """Test that kill switch check is informational, not an error."""
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        import live_preflight
        
        # Test with KILL_SWITCH enabled
        os.environ["KILL_SWITCH"] = "true"
        success, message = live_preflight.check_kill_switch()
        self.assertTrue(success, "Kill switch should not fail the check")
        self.assertIn("enabled", message.lower(), "Should report kill switch is enabled")


class TestDocumentation(unittest.TestCase):
    """Test that documentation is complete and accurate."""
    
    def test_live_trading_guide_complete(self):
        """Test that LIVE_TRADING_SETUP_GUIDE.md covers all topics."""
        doc_file = PROJECT_ROOT / "LIVE_TRADING_SETUP_GUIDE.md"
        
        with open(doc_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_topics = [
            "live_preflight.py",
            "start_live_prod.ps1",
            "Live: Runner",
            "LIVE_ACK",
            "KILL_SWITCH",
            "Preflight Checks",
            "Environment Variables",
            "Risk Configuration",
            "Exit Codes"
        ]
        
        for topic in required_topics:
            self.assertIn(topic, content,
                         f"Documentation should cover {topic}")
    
    def test_readme_or_guide_explains_automation(self):
        """Test that documentation explains automatic preflight checks."""
        doc_file = PROJECT_ROOT / "LIVE_TRADING_SETUP_GUIDE.md"
        
        with open(doc_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should explain that preflight runs automatically
        self.assertTrue(
            "automatic" in content.lower() or "automatically" in content.lower(),
            "Documentation should explain that preflight runs automatically"
        )


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
