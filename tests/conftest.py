"""
conftest.py - Pytest Configuration
=================================
Shared fixtures and configuration for all tests.
"""

import pytest
import os
import sys
import tempfile
import shutil
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def test_env():
    """Set up test environment variables."""
    original_env = os.environ.copy()
    
    # Set test environment
    os.environ['DRY_RUN'] = 'true'
    os.environ['BROKER_NAME'] = 'binance'
    os.environ['BINANCE_BASE_URL'] = 'https://testnet.binance.vision'
    
    yield os.environ
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_adapter():
    """Create a mock broker adapter for testing."""
    from system.adapters.base_adapter import BaseAdapter, AdapterStatus, OrderSide, OrderType
    
    class MockAdapter(BaseAdapter):
        """Mock adapter for testing."""
        
        def connect(self):
            self.status = AdapterStatus.CONNECTED
            return True
        
        def disconnect(self):
            self.status = AdapterStatus.DISCONNECTED
            return True
        
        def get_account_balance(self):
            return {
                'total': 10000.0,
                'available': 9500.0,
                'currency': 'USDT'
            }
        
        def get_market_price(self, symbol):
            return 50000.0
        
        def place_order(self, symbol, side, order_type, quantity, price=None, stop_price=None):
            return {
                'order_id': 'TEST123',
                'status': 'filled',
                'symbol': symbol,
                'side': side.value,
                'quantity': quantity
            }
        
        def get_order_status(self, order_id):
            return {'order_id': order_id, 'status': 'filled'}
        
        def cancel_order(self, order_id):
            return True
        
        def get_open_orders(self, symbol=None):
            return []
        
        def get_historical_data(self, symbol, interval, start_time=None, end_time=None, limit=500):
            return []
        
        def health_check(self):
            return self.status == AdapterStatus.CONNECTED
    
    return MockAdapter(testnet=True)


@pytest.fixture(autouse=True)
def cleanup_logging():
    """
    Auto-use fixture to clean up logging handlers after each test.
    
    This prevents PermissionError on Windows when trying to delete
    log files that are still open by FileHandler objects.
    """
    yield
    
    # Close and remove all logging handlers after each test
    loggers = [logging.getLogger()] + [
        logging.getLogger(name) for name in logging.root.manager.loggerDict
    ]
    
    for logger in loggers:
        for handler in logger.handlers[:]:  # Use slice to avoid modification during iteration
            try:
                handler.close()
            except Exception:
                pass  # Ignore errors during cleanup
            try:
                logger.removeHandler(handler)
            except Exception:
                pass  # Ignore errors during cleanup
    
    # Clear root logger handler list
    logging.getLogger().handlers.clear()
