"""
logger.py - Centralized Logger Configuration
==========================================
Structured logging with file rotation and multiple handlers.
"""

import logging
import logging.handlers
import os
import json
from datetime import datetime
from typing import Optional
from enum import Enum


class LogLevel(Enum):
    """Log level definitions."""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class StructuredFormatter(logging.Formatter):
    """JSON structured log formatter."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'extra'):
            log_data['extra'] = record.extra
        
        return json.dumps(log_data)


def configure_logging(log_dir: str = 'logs',
                     level: LogLevel = LogLevel.INFO,
                     max_bytes: int = 10 * 1024 * 1024,  # 10 MB
                     backup_count: int = 5,
                     enable_console: bool = True,
                     enable_json: bool = False) -> None:
    """
    Configure centralized logging system.
    
    Args:
        log_dir: Directory for log files
        level: Logging level
        max_bytes: Maximum size per log file
        backup_count: Number of backup files to keep
        enable_console: Enable console logging
        enable_json: Enable JSON structured logging
    """
    # Create log directory
    os.makedirs(log_dir, exist_ok=True)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level.value)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler (human-readable)
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level.value)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        root_logger.addHandler(console_handler)
    
    # Main log file (rotating)
    main_log = os.path.join(log_dir, 'system.log')
    file_handler = logging.handlers.RotatingFileHandler(
        main_log,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(level.value)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    root_logger.addHandler(file_handler)
    
    # Error log file (errors only)
    error_log = os.path.join(log_dir, 'errors.log')
    error_handler = logging.handlers.RotatingFileHandler(
        error_log,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_format)
    root_logger.addHandler(error_handler)
    
    # JSON log file (structured)
    if enable_json:
        json_log = os.path.join(log_dir, 'system.jsonl')
        json_handler = logging.handlers.RotatingFileHandler(
            json_log,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        json_handler.setLevel(level.value)
        json_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(json_handler)
    
    # Trading log file (trading-specific)
    trading_log = os.path.join(log_dir, 'trading.log')
    trading_handler = logging.handlers.RotatingFileHandler(
        trading_log,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    trading_handler.setLevel(level.value)
    trading_handler.setFormatter(file_format)
    
    # Add trading handler to trading logger
    trading_logger = logging.getLogger('trading')
    trading_logger.addHandler(trading_handler)
    
    root_logger.info("Logging system configured")
    root_logger.info(f"Log directory: {log_dir}")
    root_logger.info(f"Log level: {level.name}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
