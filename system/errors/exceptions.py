"""
exceptions.py - Custom Exception Hierarchy
=========================================
Structured exceptions for the system.
"""


class SystemError(Exception):
    """Base exception for system errors."""
    
    def __init__(self, message: str, code: str = "SYSTEM_ERROR", details: dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self):
        """Convert exception to dictionary."""
        return {
            'error': self.__class__.__name__,
            'code': self.code,
            'message': self.message,
            'details': self.details
        }


class AdapterError(SystemError):
    """Exception for broker adapter errors."""
    
    def __init__(self, message: str, adapter: str = None, details: dict = None):
        super().__init__(message, code="ADAPTER_ERROR", details=details)
        self.adapter = adapter


class ConfigurationError(SystemError):
    """Exception for configuration errors."""
    
    def __init__(self, message: str, config_key: str = None, details: dict = None):
        super().__init__(message, code="CONFIG_ERROR", details=details)
        self.config_key = config_key


class TradingError(SystemError):
    """Exception for trading operation errors."""
    
    def __init__(self, message: str, symbol: str = None, order_id: str = None, details: dict = None):
        super().__init__(message, code="TRADING_ERROR", details=details)
        self.symbol = symbol
        self.order_id = order_id


class ValidationError(SystemError):
    """Exception for validation errors."""
    
    def __init__(self, message: str, field: str = None, value: any = None, details: dict = None):
        super().__init__(message, code="VALIDATION_ERROR", details=details)
        self.field = field
        self.value = value
