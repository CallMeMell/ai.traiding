"""
test_enhanced_view_session.py - Tests for Enhanced View Session Features
========================================================================
Tests for new chart data and filtering functionality
"""
import os
import sys
import unittest
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dashboard import _calculate_chart_data


class TestEnhancedViewSession(unittest.TestCase):
    """Test Enhanced View Session functionality"""
    
    def test_calculate_chart_data_basic(self):
        """Test chart data calculation with basic session data"""
        # Create sample session data
        session_data = {
            'trades': [
                {
                    'order_id': 'TEST_1',
                    'symbol': 'BTCUSDT',
                    'side': 'BUY',
                    'quantity': '0.1/0.1',
                    'execution_price': '$50000.00',
                    'status': 'FILLED'
                },
                {
                    'order_id': 'TEST_2',
                    'symbol': 'BTCUSDT',
                    'side': 'SELL',
                    'quantity': '0.1/0.1',
                    'execution_price': '$51000.00',
                    'status': 'FILLED'
                },
                {
                    'order_id': 'TEST_3',
                    'symbol': 'ETHUSDT',
                    'side': 'BUY',
                    'quantity': '1.0/1.0',
                    'execution_price': '$3000.00',
                    'status': 'FILLED'
                }
            ]
        }
        
        # Calculate chart data
        chart_data = _calculate_chart_data(session_data)
        
        # Verify structure
        self.assertIn('pnl_over_time', chart_data)
        self.assertIn('win_loss_distribution', chart_data)
        self.assertIn('trade_types', chart_data)
        self.assertIn('symbols_traded', chart_data)
        
        # Verify P&L over time has correct number of entries
        self.assertEqual(len(chart_data['pnl_over_time']), 3)
        
        # Verify trade types tracking
        self.assertIn('BUY', chart_data['trade_types'])
        self.assertIn('SELL', chart_data['trade_types'])
        self.assertEqual(chart_data['trade_types']['BUY'], 2)
        self.assertEqual(chart_data['trade_types']['SELL'], 1)
        
        # Verify symbols tracking
        self.assertIn('BTCUSDT', chart_data['symbols_traded'])
        self.assertIn('ETHUSDT', chart_data['symbols_traded'])
        self.assertEqual(chart_data['symbols_traded']['BTCUSDT'], 2)
        self.assertEqual(chart_data['symbols_traded']['ETHUSDT'], 1)
        
        # Verify win/loss distribution
        self.assertIn('wins', chart_data['win_loss_distribution'])
        self.assertIn('losses', chart_data['win_loss_distribution'])
        total_wl = chart_data['win_loss_distribution']['wins'] + chart_data['win_loss_distribution']['losses']
        self.assertEqual(total_wl, 3)  # Should match number of trades
    
    def test_calculate_chart_data_empty(self):
        """Test chart data calculation with empty trades"""
        session_data = {'trades': []}
        
        chart_data = _calculate_chart_data(session_data)
        
        # Should still have structure
        self.assertIn('pnl_over_time', chart_data)
        self.assertEqual(len(chart_data['pnl_over_time']), 0)
        self.assertEqual(chart_data['win_loss_distribution']['wins'], 0)
        self.assertEqual(chart_data['win_loss_distribution']['losses'], 0)
    
    def test_calculate_chart_data_pnl_progression(self):
        """Test that P&L progresses correctly over time"""
        session_data = {
            'trades': [
                {'order_id': '1', 'symbol': 'BTC', 'side': 'BUY', 
                 'quantity': '1/1', 'execution_price': '$100', 'status': 'FILLED'},
                {'order_id': '2', 'symbol': 'BTC', 'side': 'SELL', 
                 'quantity': '1/1', 'execution_price': '$200', 'status': 'FILLED'},
            ]
        }
        
        chart_data = _calculate_chart_data(session_data)
        pnl_data = chart_data['pnl_over_time']
        
        # P&L should be cumulative (each entry >= previous)
        for i in range(len(pnl_data)):
            self.assertIsInstance(pnl_data[i]['cumulative_pnl'], (int, float))
            self.assertIn('trade_number', pnl_data[i])
            self.assertEqual(pnl_data[i]['trade_number'], i + 1)


if __name__ == '__main__':
    unittest.main()
