"""
security_manager.py - Security Management Module
=================================================
Enhanced security features for production trading:
- API key encryption/decryption
- Rate limiting for API calls
- Request validation and sanitization
- Security audit logging
"""
import os
import json
import time
import logging
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64

logger = logging.getLogger(__name__)


class SecurityManager:
    """
    Manages security features for the trading system
    
    Features:
    - API key encryption/decryption
    - Rate limiting
    - Security audit logging
    - Request validation
    """
    
    def __init__(self, master_password: Optional[str] = None):
        """
        Initialize Security Manager
        
        Args:
            master_password: Master password for encryption (uses env var if not provided)
        """
        self.master_password = master_password or os.getenv("MASTER_PASSWORD", "default-change-me")
        self.rate_limiters: Dict[str, RateLimiter] = {}
        self.security_log_file = "logs/security_audit.log"
        self._setup_security_logging()
        
        # Initialize encryption key
        self._cipher = self._generate_cipher()
        
        logger.info("✓ Security Manager initialized")
    
    def _generate_cipher(self) -> Fernet:
        """Generate encryption cipher from master password"""
        # Derive encryption key from master password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'ai.trading.salt',  # In production, use random salt per installation
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_password.encode()))
        return Fernet(key)
    
    def _setup_security_logging(self):
        """Setup security audit logging"""
        os.makedirs("logs", exist_ok=True)
        
        # Create security logger
        security_logger = logging.getLogger('security_audit')
        security_logger.setLevel(logging.INFO)
        
        # File handler for security logs
        handler = logging.FileHandler(self.security_log_file)
        handler.setFormatter(
            logging.Formatter('%(asctime)s - SECURITY - %(levelname)s - %(message)s')
        )
        security_logger.addHandler(handler)
        
        self.security_logger = security_logger
    
    def encrypt_api_key(self, api_key: str) -> str:
        """
        Encrypt API key for secure storage
        
        Args:
            api_key: Plain text API key
            
        Returns:
            Encrypted API key (base64 encoded)
        """
        try:
            encrypted = self._cipher.encrypt(api_key.encode())
            self.security_logger.info("API key encrypted successfully")
            return encrypted.decode()
        except Exception as e:
            logger.error(f"API key encryption failed: {e}")
            raise
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        """
        Decrypt API key for use
        
        Args:
            encrypted_key: Encrypted API key (base64 encoded)
            
        Returns:
            Plain text API key
        """
        try:
            decrypted = self._cipher.decrypt(encrypted_key.encode())
            self.security_logger.info("API key decrypted successfully")
            return decrypted.decode()
        except Exception as e:
            logger.error(f"API key decryption failed: {e}")
            raise
    
    def store_encrypted_keys(self, keys: Dict[str, str], filepath: str = "config/encrypted_keys.json"):
        """
        Store encrypted API keys to file
        
        Args:
            keys: Dictionary of key_name -> api_key
            filepath: Path to store encrypted keys
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        encrypted_keys = {}
        for key_name, api_key in keys.items():
            if api_key and api_key.strip():
                encrypted_keys[key_name] = self.encrypt_api_key(api_key)
        
        with open(filepath, 'w') as f:
            json.dump(encrypted_keys, f, indent=2)
        
        self.security_logger.info(f"Encrypted keys stored to {filepath}")
        logger.info(f"✓ API keys encrypted and stored securely")
    
    def load_encrypted_keys(self, filepath: str = "config/encrypted_keys.json") -> Dict[str, str]:
        """
        Load and decrypt API keys from file
        
        Args:
            filepath: Path to encrypted keys file
            
        Returns:
            Dictionary of key_name -> decrypted_api_key
        """
        if not os.path.exists(filepath):
            logger.warning(f"Encrypted keys file not found: {filepath}")
            return {}
        
        try:
            with open(filepath, 'r') as f:
                encrypted_keys = json.load(f)
            
            decrypted_keys = {}
            for key_name, encrypted_key in encrypted_keys.items():
                decrypted_keys[key_name] = self.decrypt_api_key(encrypted_key)
            
            self.security_logger.info(f"Encrypted keys loaded from {filepath}")
            return decrypted_keys
        except Exception as e:
            logger.error(f"Failed to load encrypted keys: {e}")
            return {}
    
    def create_rate_limiter(self, name: str, max_calls: int, time_window: int) -> 'RateLimiter':
        """
        Create a rate limiter for a specific resource
        
        Args:
            name: Name of the resource (e.g., 'binance_api', 'order_execution')
            max_calls: Maximum number of calls allowed
            time_window: Time window in seconds
            
        Returns:
            RateLimiter instance
        """
        limiter = RateLimiter(name, max_calls, time_window)
        self.rate_limiters[name] = limiter
        logger.info(f"✓ Rate limiter created: {name} ({max_calls} calls / {time_window}s)")
        return limiter
    
    def get_rate_limiter(self, name: str) -> Optional['RateLimiter']:
        """Get rate limiter by name"""
        return self.rate_limiters.get(name)
    
    def validate_request(self, request_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate request data for security issues
        
        Args:
            request_data: Request data to validate
            
        Returns:
            (is_valid, error_message)
        """
        # Check for SQL injection patterns
        sql_patterns = ["'", "--", ";", "DROP", "DELETE", "INSERT", "UPDATE"]
        
        # Check for XSS patterns
        xss_patterns = ["<script>", "javascript:", "onerror=", "onload="]
        
        for key, value in request_data.items():
            if isinstance(value, str):
                # Check SQL injection
                for pattern in sql_patterns:
                    if pattern.lower() in value.lower():
                        self.security_logger.warning(f"Potential SQL injection detected: {key}={value}")
                        return False, f"Invalid characters in {key}"
                
                # Check XSS
                for pattern in xss_patterns:
                    if pattern.lower() in value.lower():
                        self.security_logger.warning(f"Potential XSS detected: {key}={value}")
                        return False, f"Invalid content in {key}"
        
        return True, None
    
    def log_security_event(self, event_type: str, details: str, severity: str = "INFO"):
        """
        Log security event
        
        Args:
            event_type: Type of security event
            details: Event details
            severity: Event severity (INFO, WARNING, ERROR, CRITICAL)
        """
        log_method = getattr(self.security_logger, severity.lower(), self.security_logger.info)
        log_method(f"[{event_type}] {details}")
    
    def generate_security_report(self) -> Dict[str, Any]:
        """
        Generate security audit report
        
        Returns:
            Security report with statistics
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "rate_limiters": {},
            "security_log_file": self.security_log_file,
            "encrypted_keys_count": len(self.load_encrypted_keys())
        }
        
        # Add rate limiter stats
        for name, limiter in self.rate_limiters.items():
            report["rate_limiters"][name] = limiter.get_stats()
        
        return report


class RateLimiter:
    """
    Token bucket rate limiter for API calls
    """
    
    def __init__(self, name: str, max_calls: int, time_window: int):
        """
        Initialize rate limiter
        
        Args:
            name: Name of the rate limiter
            max_calls: Maximum calls allowed in time window
            time_window: Time window in seconds
        """
        self.name = name
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls: List[float] = []
        self.blocked_count = 0
        self.total_calls = 0
    
    def is_allowed(self) -> bool:
        """
        Check if a call is allowed based on rate limit
        
        Returns:
            True if call is allowed, False if rate limit exceeded
        """
        now = time.time()
        self.total_calls += 1
        
        # Remove old calls outside time window
        self.calls = [call_time for call_time in self.calls 
                     if now - call_time < self.time_window]
        
        # Check if limit exceeded
        if len(self.calls) >= self.max_calls:
            self.blocked_count += 1
            logger.warning(
                f"Rate limit exceeded for {self.name}: "
                f"{len(self.calls)} calls in last {self.time_window}s"
            )
            return False
        
        # Add current call
        self.calls.append(now)
        return True
    
    def wait_if_needed(self) -> float:
        """
        Wait if rate limit would be exceeded
        
        Returns:
            Time waited in seconds
        """
        while not self.is_allowed():
            sleep_time = 1.0
            time.sleep(sleep_time)
            return sleep_time
        return 0.0
    
    def get_remaining_calls(self) -> int:
        """Get number of remaining calls in current window"""
        now = time.time()
        self.calls = [call_time for call_time in self.calls 
                     if now - call_time < self.time_window]
        return max(0, self.max_calls - len(self.calls))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics"""
        return {
            "name": self.name,
            "max_calls": self.max_calls,
            "time_window": self.time_window,
            "current_calls": len(self.calls),
            "remaining_calls": self.get_remaining_calls(),
            "total_calls": self.total_calls,
            "blocked_count": self.blocked_count,
            "blocked_percentage": (self.blocked_count / self.total_calls * 100) 
                                  if self.total_calls > 0 else 0
        }
    
    def reset(self):
        """Reset rate limiter"""
        self.calls = []
        self.blocked_count = 0
        self.total_calls = 0


# Example usage
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize security manager
    security = SecurityManager()
    
    # Test API key encryption
    test_key = "test_api_key_12345"
    encrypted = security.encrypt_api_key(test_key)
    print(f"Encrypted: {encrypted}")
    
    decrypted = security.decrypt_api_key(encrypted)
    print(f"Decrypted: {decrypted}")
    print(f"Match: {test_key == decrypted}")
    
    # Test rate limiter
    limiter = security.create_rate_limiter("test_api", max_calls=5, time_window=10)
    
    print("\nTesting rate limiter (5 calls / 10s):")
    for i in range(8):
        allowed = limiter.is_allowed()
        print(f"Call {i+1}: {'✓ Allowed' if allowed else '✗ Blocked'} "
              f"(Remaining: {limiter.get_remaining_calls()})")
        time.sleep(0.5)
    
    # Print stats
    print("\nRate Limiter Stats:")
    print(json.dumps(limiter.get_stats(), indent=2))
    
    # Generate security report
    print("\nSecurity Report:")
    print(json.dumps(security.generate_security_report(), indent=2))
