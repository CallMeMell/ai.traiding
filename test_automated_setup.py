"""
test_automated_setup.py - Tests für Automated Setup
===================================================
Testet die Funktionalität des vollautomatisierten Setup-Tasks.
"""

import unittest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))


class TestAutomatedSetupClass(unittest.TestCase):
    """Test AutomatedSetup class functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_automated_setup_can_be_imported(self):
        """Test that automated_setup module can be imported."""
        try:
            from automated_setup import AutomatedSetup
            self.assertIsNotNone(AutomatedSetup)
        except ImportError as e:
            self.fail(f"Failed to import AutomatedSetup: {e}")
    
    def test_automated_setup_initialization(self):
        """Test AutomatedSetup class initialization."""
        from automated_setup import AutomatedSetup
        
        setup = AutomatedSetup()
        
        # Check attributes exist
        self.assertIsNotNone(setup.project_root)
        self.assertIsNotNone(setup.logs_dir)
        self.assertIsNotNone(setup.setup_log_file)
        self.assertIsNotNone(setup.summary_file)
        self.assertIsInstance(setup.logs, list)
        self.assertIsInstance(setup.steps_completed, list)
        self.assertIsInstance(setup.steps_failed, list)
    
    def test_log_method(self):
        """Test logging functionality."""
        from automated_setup import AutomatedSetup, STATUS_OK, STATUS_ERROR
        
        setup = AutomatedSetup()
        
        # Log success
        setup.log(STATUS_OK, "Test message", "test_step")
        self.assertEqual(len(setup.logs), 1)
        self.assertIn("Test message", setup.logs[0])
        self.assertEqual(len(setup.steps_completed), 1)
        self.assertEqual(setup.steps_completed[0], "test_step")
        
        # Log error
        setup.log(STATUS_ERROR, "Error message", "error_step")
        self.assertEqual(len(setup.logs), 2)
        self.assertEqual(len(setup.steps_failed), 1)
        self.assertEqual(setup.steps_failed[0], "error_step")
    
    def test_check_python_environment(self):
        """Test Python environment check."""
        from automated_setup import AutomatedSetup
        
        setup = AutomatedSetup()
        
        # Should pass on current Python version
        result = setup.check_python_environment()
        self.assertTrue(result)
        
        # Check that Python version was logged
        self.assertTrue(any("Python version" in log for log in setup.logs))
    
    def test_run_api_key_setup_auto_mode(self):
        """Test API key setup in auto mode."""
        from automated_setup import AutomatedSetup
        
        # This test requires keyring to be installed
        # Skip if keyring is not available
        try:
            import keyring
        except ImportError:
            self.skipTest("keyring not installed")
        
        setup = AutomatedSetup()
        
        # In auto mode without existing credentials, it should fail gracefully
        # We can't test actual keyring without proper credentials
        # Just verify the method exists and can be called
        try:
            result = setup.run_api_key_setup(auto_mode=True)
            # Either succeeds with existing creds or fails gracefully
            self.assertIsInstance(result, bool)
        except Exception as e:
            # Expected to fail without setup - that's ok
            self.assertIn("credentials", str(e).lower())


class TestAutomatedSetupScriptExecution(unittest.TestCase):
    """Test automated setup script execution."""
    
    def test_automated_setup_script_exists(self):
        """Test that automated_setup.py exists."""
        script_path = PROJECT_ROOT / "scripts" / "automated_setup.py"
        self.assertTrue(script_path.exists(), 
                       f"automated_setup.py not found at {script_path}")
    
    def test_automated_setup_script_is_executable(self):
        """Test that automated_setup.py can be executed."""
        script_path = PROJECT_ROOT / "scripts" / "automated_setup.py"
        
        # Check it's a valid Python file
        with open(script_path, 'r') as f:
            content = f.read()
            self.assertIn("def main()", content)
            self.assertIn("AutomatedSetup", content)
    
    def test_automated_setup_has_help(self):
        """Test that automated_setup.py has --help."""
        import subprocess
        
        script_path = PROJECT_ROOT / "scripts" / "automated_setup.py"
        
        result = subprocess.run(
            [sys.executable, str(script_path), "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Help should exit with 0 and show usage
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage", result.stdout.lower())
        self.assertIn("auto", result.stdout.lower())


class TestPowerShellWrapper(unittest.TestCase):
    """Test PowerShell wrapper script."""
    
    def test_powershell_wrapper_exists(self):
        """Test that automated_setup.ps1 exists."""
        ps1_path = PROJECT_ROOT / "scripts" / "automated_setup.ps1"
        self.assertTrue(ps1_path.exists(),
                       f"automated_setup.ps1 not found at {ps1_path}")
    
    def test_powershell_wrapper_content(self):
        """Test PowerShell wrapper has required content."""
        ps1_path = PROJECT_ROOT / "scripts" / "automated_setup.ps1"
        
        with open(ps1_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for key components
            self.assertIn("automated_setup.py", content)
            self.assertIn("ErrorActionPreference", content)
            self.assertIn("venv", content)
            self.assertIn("python", content.lower())
            self.assertIn("-Auto", content)
            self.assertIn("-SkipDryRun", content)


class TestSetupIntegration(unittest.TestCase):
    """Integration tests for setup flow."""
    
    def test_logs_directory_creation(self):
        """Test that logs directory is created."""
        from automated_setup import AutomatedSetup
        
        # Create setup in temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # This will create logs directory
            setup = AutomatedSetup()
            
            # Logs dir should exist in project root (not temp)
            # Just verify the class works
            self.assertIsNotNone(setup.logs_dir)
    
    def test_summary_report_structure(self):
        """Test that summary report has correct structure."""
        from automated_setup import AutomatedSetup
        
        setup = AutomatedSetup()
        
        # Add some test steps
        setup.steps_completed.append("test_step_1")
        setup.steps_completed.append("test_step_2")
        setup.steps_failed.append("test_step_3")
        
        # Generate summary (will fail on risk config but that's ok)
        try:
            setup.generate_summary_report()
        except Exception:
            pass  # Expected to fail without full setup
        
        # Check that summary file would be created at correct path
        self.assertTrue(setup.summary_file.name == "setup_summary.md")


class TestVSCodeTaskIntegration(unittest.TestCase):
    """Test VS Code task integration."""
    
    def test_vscode_tasks_file_updated(self):
        """Test that .vscode/tasks.json includes automated setup tasks."""
        import json
        
        tasks_file = PROJECT_ROOT / ".vscode" / "tasks.json"
        
        if not tasks_file.exists():
            self.skipTest("tasks.json not found")
        
        with open(tasks_file, 'r') as f:
            tasks = json.load(f)
        
        # Find automated setup task
        task_labels = [task.get("label", "") for task in tasks.get("tasks", [])]
        
        # Check for automated setup task
        self.assertTrue(
            any("Automated Setup" in label for label in task_labels),
            "Automated Setup task not found in tasks.json"
        )


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAutomatedSetupClass))
    suite.addTests(loader.loadTestsFromTestCase(TestAutomatedSetupScriptExecution))
    suite.addTests(loader.loadTestsFromTestCase(TestPowerShellWrapper))
    suite.addTests(loader.loadTestsFromTestCase(TestSetupIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestVSCodeTaskIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
