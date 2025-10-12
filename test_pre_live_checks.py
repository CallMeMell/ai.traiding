"""
test_pre_live_checks.py - Tests for Pre-Live Checks
=================================================
Unit tests for automated pre-live checks in automation runner.
"""

import unittest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from automation.runner import AutomationRunner
from core.session_store import SessionStore


class TestPreLiveChecks(unittest.TestCase):
    """Test pre-live check functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.events_path = os.path.join(self.test_dir, "events.jsonl")
        self.summary_path = os.path.join(self.test_dir, "summary.json")
        
        # Create runner with custom session store
        self.store = SessionStore(self.events_path, self.summary_path)
        self.runner = AutomationRunner(
            data_phase_timeout=5,
            strategy_phase_timeout=5,
            api_phase_timeout=5,
            heartbeat_interval=2,
            enable_validation=False
        )
        self.runner.session_store = self.store
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_data_validation_success(self):
        """Test successful data validation."""
        result = self.runner._check_data_validation()
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('record_count', result['details'])
        self.assertGreater(result['details']['record_count'], 0)
    
    def test_strategy_validation_success(self):
        """Test successful strategy validation."""
        result = self.runner._check_strategy_validation()
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('win_rate', result['details'])
        self.assertGreater(result['details']['win_rate'], 0)
    
    def test_api_connectivity_success(self):
        """Test successful API connectivity check."""
        result = self.runner._check_api_connectivity()
        
        # Should pass with warning in DRY_RUN mode (no API keys required)
        self.assertIn(result['status'], ['success', 'warning'])
        self.assertIn('connectivity', result['details'])
    
    def test_pre_live_checks_all_pass(self):
        """Test that all pre-live checks pass."""
        result = self.runner._run_pre_live_checks()
        
        self.assertIn(result['status'], ['success', 'warning'])
        self.assertIn('data_validation', result['checks'])
        self.assertIn('strategy_validation', result['checks'])
        self.assertIn('api_connectivity', result['checks'])
        self.assertEqual(len(result['critical_failures']), 0)
    
    def test_pre_live_checks_generate_events(self):
        """Test that pre-live checks generate proper events."""
        self.runner._run_pre_live_checks()
        
        events = self.store.read_events()
        event_types = [e.get('type') for e in events]
        
        self.assertIn('pre_live_check_start', event_types)
        self.assertIn('pre_live_check_complete', event_types)
    
    def test_workflow_abort_on_critical_failure(self):
        """Test that workflow aborts on critical pre-live check failure."""
        # Mock data validation to return critical failure
        def mock_data_check():
            return {
                'status': 'critical',
                'message': 'Insufficient data records',
                'details': {}
            }
        
        with patch.object(self.runner, '_check_data_validation', side_effect=mock_data_check):
            result = self.runner.run()
        
        # Workflow should abort
        self.assertEqual(result['status'], 'aborted')
        self.assertEqual(result['abort_reason'], 'pre_live_checks_failed')
        self.assertIsNotNone(result['pre_live_checks'])
        self.assertGreater(len(result['pre_live_checks']['critical_failures']), 0)
    
    def test_workflow_continues_on_warnings(self):
        """Test that workflow continues with warnings."""
        # Mock strategy validation to return warning
        def mock_strategy_check():
            return {
                'status': 'warning',
                'message': 'Strategy drawdown high',
                'details': {'max_drawdown': 0.20}
            }
        
        with patch.object(self.runner, '_check_strategy_validation', side_effect=mock_strategy_check):
            result = self.runner.run()
        
        # Workflow should complete (with possible warnings)
        self.assertIn(result['status'], ['success', 'warning'])
        self.assertIsNotNone(result['pre_live_checks'])
        self.assertGreaterEqual(len(result['pre_live_checks']['warnings']), 1)
    
    def test_api_check_critical_in_production_mode(self):
        """Test that missing API keys are critical in production mode."""
        # Create runner in production mode
        with patch.dict(os.environ, {'DRY_RUN': 'false'}, clear=False):
            runner = AutomationRunner(
                data_phase_timeout=5,
                strategy_phase_timeout=5,
                api_phase_timeout=5,
                heartbeat_interval=2,
                enable_validation=False
            )
            runner.session_store = self.store
            
            # Mock API key validation to fail
            with patch('automation.runner.EnvHelper.validate_api_keys') as mock_validate:
                mock_validate.return_value = {
                    'valid': False,
                    'missing': ['binance_api_key', 'binance_api_secret'],
                    'present': []
                }
                
                result = runner._check_api_connectivity()
                
                # Should be critical in production mode
                self.assertEqual(result['status'], 'critical')
                self.assertIn('API keys missing', result['message'])
    
    def test_api_check_warning_in_dry_run_mode(self):
        """Test that missing API keys are warnings in DRY_RUN mode."""
        # Runner is in DRY_RUN mode by default
        
        # Mock API key validation to fail
        with patch('automation.runner.EnvHelper.validate_api_keys') as mock_validate:
            mock_validate.return_value = {
                'valid': False,
                'missing': ['binance_api_key', 'binance_api_secret'],
                'present': []
            }
            
            result = self.runner._check_api_connectivity()
            
            # Should be warning in DRY_RUN mode
            self.assertEqual(result['status'], 'warning')
            self.assertIn('OK in DRY_RUN', result['message'])
    
    def test_multiple_critical_failures(self):
        """Test handling of multiple critical failures."""
        # Mock multiple checks to fail
        def mock_data_check():
            return {
                'status': 'critical',
                'message': 'Data validation failed',
                'details': {}
            }
        
        def mock_strategy_check():
            return {
                'status': 'critical',
                'message': 'Strategy validation failed',
                'details': {}
            }
        
        with patch.object(self.runner, '_check_data_validation', side_effect=mock_data_check):
            with patch.object(self.runner, '_check_strategy_validation', side_effect=mock_strategy_check):
                result = self.runner._run_pre_live_checks()
        
        # Should have 2 critical failures
        self.assertEqual(result['status'], 'critical')
        self.assertEqual(len(result['critical_failures']), 2)
    
    def test_mixed_failures_and_warnings(self):
        """Test handling of mixed failures and warnings."""
        # Mock one critical failure and one warning
        def mock_data_check():
            return {
                'status': 'warning',
                'message': 'Data may be stale',
                'details': {}
            }
        
        def mock_api_check():
            return {
                'status': 'critical',
                'message': 'API connectivity failed',
                'details': {}
            }
        
        with patch.object(self.runner, '_check_data_validation', side_effect=mock_data_check):
            with patch.object(self.runner, '_check_api_connectivity', side_effect=mock_api_check):
                result = self.runner._run_pre_live_checks()
        
        # Should be critical overall
        self.assertEqual(result['status'], 'critical')
        self.assertEqual(len(result['critical_failures']), 1)
        self.assertEqual(len(result['warnings']), 1)
    
    def test_check_error_handling(self):
        """Test that errors in checks are handled properly."""
        # Mock check to raise exception
        def mock_data_check():
            raise ValueError("Simulated check error")
        
        with patch.object(self.runner, '_check_data_validation', side_effect=mock_data_check):
            result = self.runner._run_pre_live_checks()
        
        # Should catch exception and report as critical failure
        self.assertEqual(result['status'], 'critical')
        self.assertGreater(len(result['critical_failures']), 0)


class TestPreLiveCheckReporting(unittest.TestCase):
    """Test pre-live check reporting and event generation."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.events_path = os.path.join(self.test_dir, "events.jsonl")
        self.summary_path = os.path.join(self.test_dir, "summary.json")
        
        self.store = SessionStore(self.events_path, self.summary_path)
        self.runner = AutomationRunner(
            data_phase_timeout=5,
            strategy_phase_timeout=5,
            api_phase_timeout=5,
            heartbeat_interval=2,
            enable_validation=False
        )
        self.runner.session_store = self.store
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_pre_live_check_events_logged(self):
        """Test that pre-live check events are properly logged."""
        self.runner._run_pre_live_checks()
        
        events = self.store.read_events()
        
        # Find pre-live check events
        check_events = [e for e in events if 'pre_live_check' in e.get('type', '')]
        
        self.assertGreaterEqual(len(check_events), 2)  # At least start and complete
    
    def test_abort_event_on_critical_failure(self):
        """Test that workflow abort event is generated."""
        # Mock to force critical failure
        def mock_data_check():
            return {
                'status': 'critical',
                'message': 'Critical data failure',
                'details': {}
            }
        
        with patch.object(self.runner, '_check_data_validation', side_effect=mock_data_check):
            self.runner.run()
        
        events = self.store.read_events()
        event_types = [e.get('type') for e in events]
        
        # Should have workflow_aborted event
        self.assertIn('workflow_aborted', event_types)
    
    def test_check_details_in_events(self):
        """Test that check details are included in events."""
        self.runner._run_pre_live_checks()
        
        events = self.store.read_events()
        
        # Find pre_live_check_complete event
        complete_events = [e for e in events if e.get('type') == 'pre_live_check_complete']
        
        self.assertGreater(len(complete_events), 0)
        complete_event = complete_events[0]
        
        # Should have details
        self.assertIn('details', complete_event)
        self.assertIn('checks', complete_event['details'])


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestPreLiveChecks))
    suite.addTests(loader.loadTestsFromTestCase(TestPreLiveCheckReporting))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    import sys
    sys.exit(run_tests())
