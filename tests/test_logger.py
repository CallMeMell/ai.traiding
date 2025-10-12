"""
test_logger.py - Logger System Tests
==================================
Unit tests for centralized logging system.
"""

import pytest
import sys
import os
import tempfile
import shutil
import json
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from system.log_system.logger import (
    LogLevel, StructuredFormatter, configure_logging, get_logger
)


class TestLogLevel:
    """Test LogLevel enum."""
    
    def test_log_levels_defined(self):
        """Test all log levels are defined."""
        assert LogLevel.DEBUG.value == logging.DEBUG
        assert LogLevel.INFO.value == logging.INFO
        assert LogLevel.WARNING.value == logging.WARNING
        assert LogLevel.ERROR.value == logging.ERROR
        assert LogLevel.CRITICAL.value == logging.CRITICAL


class TestStructuredFormatter:
    """Test StructuredFormatter."""
    
    def test_formatter_creates_json(self):
        """Test formatter creates JSON output."""
        formatter = StructuredFormatter()
        
        # Create test log record
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='test.py',
            lineno=10,
            msg='Test message',
            args=(),
            exc_info=None
        )
        
        # Format the record
        output = formatter.format(record)
        
        # Should be valid JSON
        log_data = json.loads(output)
        
        assert 'timestamp' in log_data
        assert log_data['level'] == 'INFO'
        assert log_data['logger'] == 'test'
        assert log_data['message'] == 'Test message'
        assert 'module' in log_data
        assert 'function' in log_data
        assert 'line' in log_data
    
    def test_formatter_includes_exception(self):
        """Test formatter includes exception info."""
        formatter = StructuredFormatter()
        
        # Create record with exception
        try:
            raise ValueError("Test error")
        except ValueError:
            record = logging.LogRecord(
                name='test',
                level=logging.ERROR,
                pathname='test.py',
                lineno=10,
                msg='Error occurred',
                args=(),
                exc_info=sys.exc_info()
            )
            
            output = formatter.format(record)
            log_data = json.loads(output)
            
            assert 'exception' in log_data
            assert 'ValueError' in log_data['exception']
            assert 'Test error' in log_data['exception']


class TestConfigureLogging:
    """Test configure_logging function."""
    
    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary log directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Close all handlers before cleanup to avoid PermissionError on Windows
        self._cleanup_logging_handlers()
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def _cleanup_logging_handlers(self):
        """Close and remove all logging handlers."""
        # Get root logger and all other loggers
        loggers = [logging.getLogger()] + [
            logging.getLogger(name) for name in logging.root.manager.loggerDict
        ]
        
        for logger in loggers:
            # Close and remove all handlers
            for handler in logger.handlers[:]:  # Use slice to avoid modification during iteration
                try:
                    handler.close()
                except Exception:
                    pass  # Ignore errors during cleanup
                try:
                    logger.removeHandler(handler)
                except Exception:
                    pass  # Ignore errors during cleanup
        
        # Clear handler list completely
        logging.getLogger().handlers.clear()
    
    def test_configure_logging_creates_directory(self, temp_log_dir):
        """Test logging configuration creates log directory."""
        log_dir = os.path.join(temp_log_dir, 'test_logs')
        
        configure_logging(log_dir=log_dir, enable_console=False)
        
        assert os.path.exists(log_dir)
    
    def test_configure_logging_creates_log_files(self, temp_log_dir):
        """Test logging configuration creates log files."""
        log_dir = os.path.join(temp_log_dir, 'test_logs')
        
        configure_logging(log_dir=log_dir, enable_console=False)
        
        # Log a message to create files
        logger = get_logger('test')
        logger.info('Test message')
        logger.error('Test error')
        
        # Check main log file
        main_log = os.path.join(log_dir, 'system.log')
        assert os.path.exists(main_log)
        
        # Check error log file
        error_log = os.path.join(log_dir, 'errors.log')
        assert os.path.exists(error_log)
    
    def test_configure_logging_with_json(self, temp_log_dir):
        """Test logging with JSON format enabled."""
        log_dir = os.path.join(temp_log_dir, 'test_logs')
        
        configure_logging(
            log_dir=log_dir,
            enable_console=False,
            enable_json=True
        )
        
        # Log a message
        logger = get_logger('test')
        logger.info('JSON test message')
        
        # Check JSON log file exists
        json_log = os.path.join(log_dir, 'system.jsonl')
        assert os.path.exists(json_log)
        
        # Read and verify JSON content
        with open(json_log, 'r') as f:
            lines = f.readlines()
            # Should have at least the config message and our test message
            assert len(lines) >= 2
            
            # Last line should be our message
            last_log = json.loads(lines[-1])
            assert last_log['message'] == 'JSON test message'
    
    def test_configure_logging_level_filtering(self, temp_log_dir):
        """Test logging level filtering."""
        log_dir = os.path.join(temp_log_dir, 'test_logs')
        
        # Configure with WARNING level
        configure_logging(
            log_dir=log_dir,
            level=LogLevel.WARNING,
            enable_console=False
        )
        
        logger = get_logger('test')
        logger.debug('Debug message')  # Should be filtered
        logger.info('Info message')    # Should be filtered
        logger.warning('Warning message')  # Should be logged
        logger.error('Error message')      # Should be logged
        
        # Read main log
        main_log = os.path.join(log_dir, 'system.log')
        with open(main_log, 'r') as f:
            content = f.read()
            
            assert 'Debug message' not in content
            assert 'Info message' not in content
            assert 'Warning message' in content
            assert 'Error message' in content
    
    def test_configure_logging_error_file_only_errors(self, temp_log_dir):
        """Test error log file only contains errors."""
        log_dir = os.path.join(temp_log_dir, 'test_logs')
        
        configure_logging(log_dir=log_dir, enable_console=False)
        
        logger = get_logger('test')
        logger.info('Info message')
        logger.warning('Warning message')
        logger.error('Error message')
        
        # Read error log
        error_log = os.path.join(log_dir, 'errors.log')
        with open(error_log, 'r') as f:
            content = f.read()
            
            assert 'Info message' not in content
            assert 'Warning message' not in content
            assert 'Error message' in content


class TestGetLogger:
    """Test get_logger function."""
    
    def test_get_logger_returns_logger(self):
        """Test get_logger returns a logger instance."""
        logger = get_logger('test_logger')
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == 'test_logger'
    
    def test_get_logger_same_name_returns_same_instance(self):
        """Test get_logger with same name returns same instance."""
        logger1 = get_logger('test_logger')
        logger2 = get_logger('test_logger')
        
        assert logger1 is logger2
    
    def test_get_logger_different_names(self):
        """Test get_logger with different names returns different instances."""
        logger1 = get_logger('logger1')
        logger2 = get_logger('logger2')
        
        assert logger1 is not logger2
        assert logger1.name == 'logger1'
        assert logger2.name == 'logger2'


class TestLoggingIntegration:
    """Test logging system integration."""
    
    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary log directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Close all handlers before cleanup to avoid PermissionError on Windows
        self._cleanup_logging_handlers()
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def _cleanup_logging_handlers(self):
        """Close and remove all logging handlers."""
        # Get root logger and all other loggers
        loggers = [logging.getLogger()] + [
            logging.getLogger(name) for name in logging.root.manager.loggerDict
        ]
        
        for logger in loggers:
            # Close and remove all handlers
            for handler in logger.handlers[:]:  # Use slice to avoid modification during iteration
                try:
                    handler.close()
                except Exception:
                    pass  # Ignore errors during cleanup
                try:
                    logger.removeHandler(handler)
                except Exception:
                    pass  # Ignore errors during cleanup
        
        # Clear handler list completely
        logging.getLogger().handlers.clear()
    
    def test_multiple_loggers_write_to_same_file(self, temp_log_dir):
        """Test multiple loggers write to the same log file."""
        log_dir = os.path.join(temp_log_dir, 'test_logs')
        
        configure_logging(log_dir=log_dir, enable_console=False)
        
        # Create multiple loggers
        logger1 = get_logger('module1')
        logger2 = get_logger('module2')
        
        logger1.info('Message from module1')
        logger2.info('Message from module2')
        
        # Both messages should be in main log
        main_log = os.path.join(log_dir, 'system.log')
        with open(main_log, 'r') as f:
            content = f.read()
            
            assert 'Message from module1' in content
            assert 'Message from module2' in content
    
    def test_log_rotation_configuration(self, temp_log_dir):
        """Test log rotation is configured."""
        log_dir = os.path.join(temp_log_dir, 'test_logs')
        
        # Configure with small max_bytes for testing
        configure_logging(
            log_dir=log_dir,
            max_bytes=1024,  # 1 KB
            backup_count=3,
            enable_console=False
        )
        
        logger = get_logger('test')
        
        # Verify handlers are rotating file handlers
        root_logger = logging.getLogger()
        rotating_handlers = [
            h for h in root_logger.handlers
            if isinstance(h, logging.handlers.RotatingFileHandler)
        ]
        
        assert len(rotating_handlers) > 0
        
        # Check that handlers have correct configuration
        for handler in rotating_handlers:
            assert handler.maxBytes == 1024
            assert handler.backupCount == 3
