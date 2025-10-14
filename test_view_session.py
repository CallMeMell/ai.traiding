"""
test_view_session.py - Tests for View Session Feature
=====================================================
Unit tests for session viewing functionality
"""
import os
import sys
import unittest
import tempfile
import shutil
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dashboard import _get_session_list, _parse_session_log, _get_session_details


class TestViewSessionFeature(unittest.TestCase):
    """Test View Session functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_logs_dir = tempfile.mkdtemp()
        self.original_logs_dir = "logs"
        
        # Temporarily modify the logs directory for testing
        import dashboard
        self.original_get_session_list = dashboard._get_session_list
        self.original_get_session_details = dashboard._get_session_details
        
        # Create test session log
        self.session_id = "20240101_120000"
        self.test_log_path = os.path.join(
            self.test_logs_dir, 
            f"simulated_trading_session_{self.session_id}.log"
        )
        
        with open(self.test_log_path, 'w') as f:
            f.write("""================================================================================
SIMULATED LIVE TRADING SESSION LOG
================================================================================
Session Start: 2024-01-01 12:00:00
Session End: 2024-01-01 14:30:00
Initial Capital: $10,000.00
Final Equity: $10,234.50
Total P&L: $234.50

================================================================================
PERFORMANCE METRICS
================================================================================
total_orders: 15
filled_orders: 14
partially_filled_orders: 1
rejected_orders: 0
win_rate: 0.57

================================================================================
EXECUTION HISTORY
================================================================================

Order ID: SIM_1_1704110400000
  Symbol: BTCUSDT
  Side: BUY
  Quantity: 0.1/0.1
  Execution Price: $50000.00
  Slippage: $12.50 (0.025%)
  Fees: $2.50
  Delay: 120.0ms
  Status: FILLED
  Timestamp: 2024-01-01 12:05:00
""")
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_logs_dir, ignore_errors=True)
    
    def test_parse_session_log(self):
        """Test session log parsing"""
        session_data = _parse_session_log(self.test_log_path)
        
        self.assertIsNotNone(session_data)
        self.assertEqual(session_data['id'], self.session_id)
        self.assertEqual(session_data['initial_capital'], 10000.0)
        self.assertEqual(session_data['final_equity'], 10234.5)
        self.assertEqual(session_data['total_pnl'], 234.5)
        self.assertEqual(session_data['total_trades'], 15)
        self.assertAlmostEqual(session_data['win_rate'], 0.57, places=2)
    
    def test_parse_session_log_missing_file(self):
        """Test parsing non-existent log file"""
        result = _parse_session_log("nonexistent.log")
        self.assertIsNone(result)
    
    def test_get_session_details(self):
        """Test getting session details"""
        # Temporarily change logs directory
        import dashboard
        original_func = dashboard._get_session_details
        
        def mock_get_session_details(session_id):
            logs_dir = self.test_logs_dir
            filepath = os.path.join(logs_dir, f"simulated_trading_session_{session_id}.log")
            
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r') as f:
                content = f.read()
            
            lines = content.split('\n')
            session_data = {
                'id': session_id,
                'timestamp': '',
                'metrics': {},
                'trades': [],
                'performance': {}
            }
            
            current_section = None
            current_trade = {}
            
            for line in lines:
                line_stripped = line.strip()
                
                if 'PERFORMANCE METRICS' in line:
                    current_section = 'metrics'
                    continue
                elif 'EXECUTION HISTORY' in line:
                    current_section = 'trades'
                    continue
                
                if current_section == 'metrics' and ':' in line_stripped:
                    key, value = line_stripped.split(':', 1)
                    session_data['metrics'][key.strip()] = value.strip()
                elif current_section == 'trades':
                    if line_stripped.startswith('Order ID:'):
                        if current_trade:
                            session_data['trades'].append(current_trade)
                        current_trade = {'order_id': line_stripped.split(':', 1)[1].strip()}
                    elif ':' in line_stripped and current_trade:
                        key, value = line_stripped.split(':', 1)
                        current_trade[key.strip().lower().replace(' ', '_')] = value.strip()
            
            if current_trade:
                session_data['trades'].append(current_trade)
            
            return session_data
        
        dashboard._get_session_details = mock_get_session_details
        
        try:
            details = dashboard._get_session_details(self.session_id)
            
            self.assertIsNotNone(details)
            self.assertEqual(details['id'], self.session_id)
            self.assertIn('metrics', details)
            self.assertIn('trades', details)
            self.assertGreater(len(details['metrics']), 0)
            self.assertGreater(len(details['trades']), 0)
            
            # Check trade details
            first_trade = details['trades'][0]
            self.assertEqual(first_trade['order_id'], 'SIM_1_1704110400000')
            self.assertEqual(first_trade['symbol'], 'BTCUSDT')
            self.assertEqual(first_trade['side'], 'BUY')
        finally:
            dashboard._get_session_details = original_func
    
    def test_get_session_details_nonexistent(self):
        """Test getting details for non-existent session"""
        import dashboard
        original_func = dashboard._get_session_details
        
        def mock_get_session_details(session_id):
            logs_dir = self.test_logs_dir
            filepath = os.path.join(logs_dir, f"simulated_trading_session_{session_id}.log")
            if not os.path.exists(filepath):
                return None
            return {}
        
        dashboard._get_session_details = mock_get_session_details
        
        try:
            details = dashboard._get_session_details("nonexistent")
            self.assertIsNone(details)
        finally:
            dashboard._get_session_details = original_func
    
    def test_session_filtering_profitable(self):
        """Test filtering sessions by profitability"""
        # Create two sessions: one profitable, one loss
        sessions = [
            {'id': 'session1', 'total_pnl': 234.5, 'timestamp': '2024-01-01 12:00:00'},
            {'id': 'session2', 'total_pnl': -150.0, 'timestamp': '2024-01-02 09:30:00'}
        ]
        
        # Filter profitable
        profitable = [s for s in sessions if s['total_pnl'] > 0]
        self.assertEqual(len(profitable), 1)
        self.assertEqual(profitable[0]['id'], 'session1')
        
        # Filter loss
        loss_sessions = [s for s in sessions if s['total_pnl'] < 0]
        self.assertEqual(len(loss_sessions), 1)
        self.assertEqual(loss_sessions[0]['id'], 'session2')
    
    def test_session_search(self):
        """Test searching sessions"""
        sessions = [
            {'id': '20240101_120000', 'timestamp': '2024-01-01 12:00:00'},
            {'id': '20240102_093000', 'timestamp': '2024-01-02 09:30:00'}
        ]
        
        # Search by date
        search_term = '20240101'
        filtered = [s for s in sessions if search_term.lower() in s['id'].lower()]
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['id'], '20240101_120000')


class TestSessionAPIIntegration(unittest.TestCase):
    """Test session API integration"""
    
    def test_session_list_format(self):
        """Test that session list has correct format"""
        # This test uses actual logs directory
        if os.path.exists("logs"):
            sessions = _get_session_list()
            
            for session in sessions:
                self.assertIn('id', session)
                self.assertIn('timestamp', session)
                self.assertIn('total_pnl', session)
                self.assertIn('total_trades', session)
                self.assertIn('initial_capital', session)
                self.assertIn('final_equity', session)
                
                # Check data types
                self.assertIsInstance(session['total_pnl'], (int, float))
                self.assertIsInstance(session['total_trades'], int)
    
    def test_session_detail_format(self):
        """Test that session details have correct format"""
        if os.path.exists("logs"):
            sessions = _get_session_list()
            
            if sessions:
                session_id = sessions[0]['id']
                details = _get_session_details(session_id)
                
                self.assertIsNotNone(details)
                self.assertIn('id', details)
                self.assertIn('metrics', details)
                self.assertIn('trades', details)
                
                # Check metrics is a dict
                self.assertIsInstance(details['metrics'], dict)
                
                # Check trades is a list
                self.assertIsInstance(details['trades'], list)


def run_tests():
    """Run all tests"""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestViewSessionFeature))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSessionAPIIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
