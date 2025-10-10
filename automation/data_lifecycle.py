"""
data_lifecycle.py - Data Lifecycle Management
==============================================
Handles log rotation, archiving, PII masking, and integrity checks.
"""

import os
import json
import shutil
import hashlib
import logging
import gzip
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import re

logger = logging.getLogger(__name__)


class DataLifecycle:
    """Manages data lifecycle: rotation, archiving, PII masking, and integrity."""
    
    def __init__(self,
                 logs_dir: str = "logs",
                 data_dir: str = "data",
                 archive_dir: str = "data/archive",
                 max_age_days: int = 30,
                 compress: bool = True):
        """
        Initialize data lifecycle manager.
        
        Args:
            logs_dir: Directory containing log files
            data_dir: Directory containing data files
            archive_dir: Directory for archived files
            max_age_days: Maximum age in days before archiving
            compress: Whether to compress archives
        """
        self.logs_dir = Path(logs_dir)
        self.data_dir = Path(data_dir)
        self.archive_dir = Path(archive_dir)
        self.max_age_days = max_age_days
        self.compress = compress
        
        # Ensure directories exist
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        # PII patterns to mask
        self.pii_patterns = {
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'api_key': re.compile(r'(?i)(api[_-]?key|apikey|access[_-]?token|secret[_-]?key)[\s:=]+[\'\"]?([A-Za-z0-9_\-]{20,})[\'\"]?'),
            'password': re.compile(r'(?i)(password|passwd|pwd)[\s:=]+[\'\"]?([^\s\'"]+)[\'\"]?'),
            'phone': re.compile(r'\b\+?[1-9]\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b'),
        }
        
        # Archive metadata file
        self.metadata_file = self.archive_dir / "archive_metadata.json"
        self._load_metadata()
    
    def _load_metadata(self) -> None:
        """Load archive metadata."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load metadata: {e}")
                self.metadata = {}
        else:
            self.metadata = {}
    
    def _save_metadata(self) -> None:
        """Save archive metadata."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, indent=2, fp=f)
        except Exception as e:
            logger.error(f"Could not save metadata: {e}")
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Could not calculate checksum for {file_path}: {e}")
            return ""
    
    def _archive_file(self, file_path: Path, category: str = "general") -> Optional[Path]:
        """
        Archive a single file with compression and checksum.
        
        Args:
            file_path: Path to file to archive
            category: Category for organizing archives (logs, data, etc.)
        
        Returns:
            Path to archived file or None on failure
        """
        if not file_path.exists():
            logger.warning(f"File not found for archiving: {file_path}")
            return None
        
        try:
            # Calculate checksum before archiving
            checksum = self._calculate_checksum(file_path)
            
            # Create category directory
            category_dir = self.archive_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate archive filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
            
            if self.compress and file_path.suffix not in ['.gz', '.zip']:
                archive_name += '.gz'
                archive_path = category_dir / archive_name
                
                # Compress file
                with open(file_path, 'rb') as f_in:
                    with gzip.open(archive_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                archive_path = category_dir / archive_name
                shutil.copy2(file_path, archive_path)
            
            # Store metadata
            archive_key = str(archive_path.relative_to(self.archive_dir))
            self.metadata[archive_key] = {
                'original_path': str(file_path),
                'archived_at': datetime.now().isoformat(),
                'checksum': checksum,
                'compressed': self.compress,
                'category': category,
                'size_bytes': file_path.stat().st_size
            }
            self._save_metadata()
            
            logger.info(f"Archived: {file_path} -> {archive_path}")
            return archive_path
            
        except Exception as e:
            logger.error(f"Failed to archive {file_path}: {e}")
            return None
    
    def rotate_logs(self, max_age_days: Optional[int] = None) -> Dict[str, Any]:
        """
        Rotate and archive old log files.
        
        Args:
            max_age_days: Maximum age in days (uses instance default if None)
        
        Returns:
            Dictionary with rotation results
        """
        if max_age_days is None:
            max_age_days = self.max_age_days
        
        results = {
            'status': 'success',
            'archived_count': 0,
            'failed_count': 0,
            'archived_files': [],
            'errors': []
        }
        
        # Check if logs directory exists
        if not self.logs_dir.exists():
            logger.warning(f"Logs directory not found: {self.logs_dir}")
            results['status'] = 'warning'
            results['errors'].append(f"Logs directory not found: {self.logs_dir}")
            return results
        
        try:
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            
            # Find log files older than cutoff
            for log_file in self.logs_dir.rglob("*.log*"):
                if log_file.is_file():
                    # Skip already compressed archives
                    if log_file.suffix == '.gz':
                        continue
                    
                    # Check file age
                    file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if file_mtime < cutoff_date:
                        archive_path = self._archive_file(log_file, category="logs")
                        if archive_path:
                            results['archived_files'].append(str(log_file))
                            results['archived_count'] += 1
                            
                            # Remove original file after successful archiving
                            log_file.unlink()
                            logger.info(f"Removed original log file: {log_file}")
                        else:
                            results['failed_count'] += 1
                            results['errors'].append(f"Failed to archive: {log_file}")
            
            if results['failed_count'] > 0:
                results['status'] = 'partial'
            
            logger.info(f"Log rotation complete: {results['archived_count']} archived, {results['failed_count']} failed")
            
        except Exception as e:
            logger.error(f"Log rotation error: {e}")
            results['status'] = 'error'
            results['errors'].append(str(e))
        
        return results
    
    def mask_pii(self, data: Union[Dict[str, Any], str], mask_char: str = "*") -> Union[Dict[str, Any], str]:
        """
        Mask personally identifiable information (PII) in data.
        
        Args:
            data: Data to mask (dict or string)
            mask_char: Character to use for masking
        
        Returns:
            Data with PII masked
        """
        if isinstance(data, dict):
            return self._mask_pii_dict(data, mask_char)
        elif isinstance(data, str):
            return self._mask_pii_string(data, mask_char)
        else:
            return data
    
    def _mask_pii_dict(self, data: Dict[str, Any], mask_char: str = "*") -> Dict[str, Any]:
        """Mask PII in dictionary."""
        masked = {}
        
        # Fields that should NOT be masked (timestamps, IDs, etc.)
        safe_fields = ['timestamp', 'time', 'date', 'id', 'status', 'type', 'phase', 'duration', 'count']
        
        for key, value in data.items():
            # Check if key indicates PII
            key_lower = key.lower()
            
            # Skip safe fields
            if any(safe_field in key_lower for safe_field in safe_fields):
                if isinstance(value, dict):
                    masked[key] = self._mask_pii_dict(value, mask_char)
                elif isinstance(value, list):
                    masked[key] = [self._mask_pii_dict(item, mask_char) if isinstance(item, dict) else item for item in value]
                else:
                    masked[key] = value
            elif any(pii_key in key_lower for pii_key in ['email', 'password', 'api_key', 'secret', 'token', 'phone', 'user', 'name']):
                if isinstance(value, str) and value:
                    # Mask the value partially (show first 2 and last 2 chars if long enough)
                    if len(value) > 8:
                        masked[key] = value[:2] + mask_char * (len(value) - 4) + value[-2:]
                    else:
                        masked[key] = mask_char * len(value)
                else:
                    masked[key] = mask_char * 8
            elif isinstance(value, dict):
                masked[key] = self._mask_pii_dict(value, mask_char)
            elif isinstance(value, list):
                masked[key] = [self._mask_pii_dict(item, mask_char) if isinstance(item, dict) else item for item in value]
            elif isinstance(value, str):
                masked[key] = self._mask_pii_string(value, mask_char)
            else:
                masked[key] = value
        
        return masked
    
    def _mask_pii_string(self, text: str, mask_char: str = "*") -> str:
        """Mask PII patterns in string."""
        masked_text = text
        
        # Mask emails
        masked_text = self.pii_patterns['email'].sub(
            lambda m: m.group(0)[:2] + mask_char * (len(m.group(0)) - 4) + m.group(0)[-2:] if len(m.group(0)) > 4 else mask_char * len(m.group(0)),
            masked_text
        )
        
        # Mask API keys and tokens
        masked_text = self.pii_patterns['api_key'].sub(
            lambda m: m.group(1) + "=" + mask_char * 20,
            masked_text
        )
        
        # Mask passwords
        masked_text = self.pii_patterns['password'].sub(
            lambda m: m.group(1) + "=" + mask_char * 8,
            masked_text
        )
        
        # Mask phone numbers
        masked_text = self.pii_patterns['phone'].sub(
            lambda m: mask_char * len(m.group(0)),
            masked_text
        )
        
        return masked_text
    
    def check_archive(self) -> bool:
        """
        Check integrity of archived files using stored checksums.
        
        Returns:
            True if all archives are valid, False otherwise
        """
        if not self.metadata:
            logger.info("No archive metadata found")
            return True
        
        all_valid = True
        invalid_files = []
        
        try:
            for archive_key, meta in self.metadata.items():
                archive_path = self.archive_dir / archive_key
                
                if not archive_path.exists():
                    logger.warning(f"Archive file missing: {archive_path}")
                    invalid_files.append(str(archive_path))
                    all_valid = False
                    continue
                
                # Skip checksum validation for compressed files (checksum is for original)
                if meta.get('compressed', False) and archive_path.suffix == '.gz':
                    # For compressed files, just verify file exists and has content
                    if archive_path.stat().st_size == 0:
                        logger.warning(f"Archive file is empty: {archive_path}")
                        invalid_files.append(str(archive_path))
                        all_valid = False
                    continue
                
                # For uncompressed files, verify checksum
                stored_checksum = meta.get('checksum', '')
                if stored_checksum:
                    current_checksum = self._calculate_checksum(archive_path)
                    if current_checksum != stored_checksum:
                        logger.warning(f"Checksum mismatch for {archive_path}")
                        invalid_files.append(str(archive_path))
                        all_valid = False
            
            if all_valid:
                logger.info("Archive integrity check passed")
            else:
                logger.error(f"Archive integrity check failed: {len(invalid_files)} invalid files")
                for invalid in invalid_files:
                    logger.error(f"  - {invalid}")
            
        except Exception as e:
            logger.error(f"Archive integrity check error: {e}")
            return False
        
        return all_valid


# Convenience functions for easy import
def rotate_logs(logs_dir: str = "logs", 
                data_dir: str = "data",
                archive_dir: str = "data/archive",
                max_age_days: int = 30) -> Dict[str, Any]:
    """
    Rotate and archive old log files.
    
    Args:
        logs_dir: Directory containing log files
        data_dir: Directory containing data files
        archive_dir: Directory for archived files
        max_age_days: Maximum age in days before archiving
    
    Returns:
        Dictionary with rotation results
    """
    lifecycle = DataLifecycle(logs_dir, data_dir, archive_dir, max_age_days)
    return lifecycle.rotate_logs()


def mask_pii(data: Union[Dict[str, Any], str], mask_char: str = "*") -> Union[Dict[str, Any], str]:
    """
    Mask personally identifiable information (PII) in data.
    
    Args:
        data: Data to mask (dict or string)
        mask_char: Character to use for masking
    
    Returns:
        Data with PII masked
    """
    lifecycle = DataLifecycle()
    return lifecycle.mask_pii(data, mask_char)


def check_archive(archive_dir: str = "data/archive") -> bool:
    """
    Check integrity of archived files.
    
    Args:
        archive_dir: Directory containing archived files
    
    Returns:
        True if all archives are valid, False otherwise
    """
    lifecycle = DataLifecycle(archive_dir=archive_dir)
    return lifecycle.check_archive()
