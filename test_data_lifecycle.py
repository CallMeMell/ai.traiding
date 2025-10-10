"""
test_data_lifecycle.py - Tests for Data Lifecycle Management
===========================================================
Unit tests for data lifecycle: rotation, archiving, PII masking, and integrity checks.
"""

import unittest
import os
import tempfile
import shutil
import json
import gzip
from pathlib import Path
from datetime import datetime, timedelta
from automation.data_lifecycle import DataLifecycle, rotate_logs, mask_pii, check_archive


class TestDataLifecycle(unittest.TestCase):
    """Test DataLifecycle functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.logs_dir = os.path.join(self.test_dir, "logs")
        self.data_dir = os.path.join(self.test_dir, "data")
        self.archive_dir = os.path.join(self.test_dir, "data", "archive")
        
        # Create directories
        os.makedirs(self.logs_dir)
        os.makedirs(self.data_dir)
        
        self.lifecycle = DataLifecycle(
            logs_dir=self.logs_dir,
            data_dir=self.data_dir,
            archive_dir=self.archive_dir,
            max_age_days=7
        )
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def _create_old_log_file(self, filename: str, days_old: int = 10) -> Path:
        """Create a log file with modified time in the past."""
        log_path = Path(self.logs_dir) / filename
        log_path.write_text(f"Test log content for {filename}\n" * 10)
        
        # Set modification time to past
        old_time = (datetime.now() - timedelta(days=days_old)).timestamp()
        os.utime(log_path, (old_time, old_time))
        
        return log_path
    
    def test_rotate_logs_archives_old_files(self):
        """Test that old log files are archived."""
        # Create old log file
        log_file = self._create_old_log_file("old_system.log", days_old=10)
        
        # Run rotation
        results = self.lifecycle.rotate_logs()
        
        # Verify results
        self.assertEqual(results['status'], 'success')
        self.assertEqual(results['archived_count'], 1)
        self.assertEqual(results['failed_count'], 0)
        
        # Verify original file is removed
        self.assertFalse(log_file.exists())
        
        # Verify archive exists
        archive_files = list(Path(self.archive_dir).rglob("*.gz"))
        self.assertEqual(len(archive_files), 1)
    
    def test_rotate_logs_keeps_recent_files(self):
        """Test that recent log files are not archived."""
        # Create recent log file
        log_path = Path(self.logs_dir) / "recent_system.log"
        log_path.write_text("Recent log content\n" * 10)
        
        # Run rotation
        results = self.lifecycle.rotate_logs()
        
        # Verify results
        self.assertEqual(results['archived_count'], 0)
        
        # Verify file still exists
        self.assertTrue(log_path.exists())
    
    def test_rotate_logs_handles_missing_directory(self):
        """Test rotation handles missing logs directory gracefully."""
        # Remove logs directory
        shutil.rmtree(self.logs_dir)
        
        # Run rotation
        results = self.lifecycle.rotate_logs()
        
        # Should handle gracefully
        self.assertEqual(results['status'], 'warning')
        self.assertEqual(results['archived_count'], 0)
    
    def test_mask_pii_dict_masks_email(self):
        """Test PII masking for email in dictionary."""
        data = {
            "user": "Max Mustermann",
            "email": "max@example.com"
        }
        
        masked = self.lifecycle.mask_pii(data)
        
        # Email should be masked
        self.assertNotEqual(masked['email'], "max@example.com")
        self.assertIn("*", masked['email'])
        
        # User should be partially masked (PII field)
        self.assertNotEqual(masked['user'], "Max Mustermann")
        self.assertIn("*", masked['user'])
    
    def test_mask_pii_dict_masks_sensitive_fields(self):
        """Test PII masking for various sensitive fields."""
        data = {
            "username": "testuser",
            "password": "secretpass123",
            "api_key": "abc123def456ghi789jkl",
            "normal_field": "normal_value"
        }
        
        masked = self.lifecycle.mask_pii(data)
        
        # Sensitive fields should be masked
        self.assertNotEqual(masked['password'], "secretpass123")
        self.assertIn("*", masked['password'])
        self.assertNotEqual(masked['api_key'], "abc123def456ghi789jkl")
        self.assertIn("*", masked['api_key'])
        
        # Normal field should not be masked
        self.assertEqual(masked['normal_field'], "normal_value")
    
    def test_mask_pii_string_masks_email(self):
        """Test PII masking for email in string."""
        text = "Contact us at support@example.com for help"
        
        masked = self.lifecycle.mask_pii(text)
        
        # Email should be masked
        self.assertNotEqual(masked, text)
        self.assertNotIn("support@example.com", masked)
        self.assertIn("*", masked)
    
    def test_mask_pii_string_masks_api_key(self):
        """Test PII masking for API key in string."""
        text = "api_key=abc123def456ghi789jkl"
        
        masked = self.lifecycle.mask_pii(text)
        
        # API key should be masked
        self.assertNotEqual(masked, text)
        self.assertNotIn("abc123def456ghi789jkl", masked)
        self.assertIn("api_key=", masked)
        self.assertIn("*", masked)
    
    def test_mask_pii_preserves_structure(self):
        """Test that masking preserves data structure."""
        data = {
            "user": "test",
            "metadata": {
                "email": "test@example.com",
                "timestamp": "2024-01-01"
            },
            "values": [1, 2, 3]
        }
        
        masked = self.lifecycle.mask_pii(data)
        
        # Structure should be preserved
        self.assertIn("metadata", masked)
        self.assertIn("values", masked)
        self.assertIsInstance(masked['metadata'], dict)
        self.assertIsInstance(masked['values'], list)
        
        # Non-PII should be unchanged
        self.assertEqual(masked['metadata']['timestamp'], "2024-01-01")
        self.assertEqual(masked['values'], [1, 2, 3])
    
    def test_check_archive_with_no_archives(self):
        """Test archive integrity check with no archives."""
        result = self.lifecycle.check_archive()
        
        # Should return True when no archives exist
        self.assertTrue(result)
    
    def test_check_archive_validates_existing_archives(self):
        """Test archive integrity check validates existing archives."""
        # Create and archive a file
        log_file = self._create_old_log_file("test.log", days_old=10)
        self.lifecycle.rotate_logs()
        
        # Check archive integrity
        result = self.lifecycle.check_archive()
        
        # Should pass
        self.assertTrue(result)
    
    def test_check_archive_detects_missing_files(self):
        """Test archive integrity check detects missing files."""
        # Create and archive a file
        log_file = self._create_old_log_file("test.log", days_old=10)
        self.lifecycle.rotate_logs()
        
        # Remove the archived file
        archive_files = list(Path(self.archive_dir).rglob("*.gz"))
        if archive_files:
            archive_files[0].unlink()
        
        # Check archive integrity
        result = self.lifecycle.check_archive()
        
        # Should fail
        self.assertFalse(result)
    
    def test_archive_creates_metadata(self):
        """Test that archiving creates metadata."""
        # Create and archive a file
        log_file = self._create_old_log_file("test.log", days_old=10)
        self.lifecycle.rotate_logs()
        
        # Verify metadata file exists
        metadata_file = Path(self.archive_dir) / "archive_metadata.json"
        self.assertTrue(metadata_file.exists())
        
        # Verify metadata content
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        self.assertGreater(len(metadata), 0)
        
        # Check metadata structure
        for key, meta in metadata.items():
            self.assertIn('original_path', meta)
            self.assertIn('archived_at', meta)
            self.assertIn('checksum', meta)
            self.assertIn('category', meta)
    
    def test_compressed_archives(self):
        """Test that archives are compressed when enabled."""
        # Create and archive a file
        log_file = self._create_old_log_file("test.log", days_old=10)
        self.lifecycle.rotate_logs()
        
        # Verify archive is compressed
        archive_files = list(Path(self.archive_dir).rglob("*.gz"))
        self.assertEqual(len(archive_files), 1)
        
        # Verify it's a valid gzip file
        with gzip.open(archive_files[0], 'rb') as f:
            content = f.read()
            self.assertGreater(len(content), 0)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions for easy import."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.logs_dir = os.path.join(self.test_dir, "logs")
        self.data_dir = os.path.join(self.test_dir, "data")
        self.archive_dir = os.path.join(self.test_dir, "data", "archive")
        
        os.makedirs(self.logs_dir)
        os.makedirs(self.data_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_rotate_logs_function(self):
        """Test standalone rotate_logs function."""
        # Create old log file
        log_path = Path(self.logs_dir) / "old.log"
        log_path.write_text("test content\n" * 10)
        
        # Set old modification time
        old_time = (datetime.now() - timedelta(days=35)).timestamp()
        os.utime(log_path, (old_time, old_time))
        
        # Run rotation
        results = rotate_logs(
            logs_dir=self.logs_dir,
            data_dir=self.data_dir,
            archive_dir=self.archive_dir,
            max_age_days=30
        )
        
        # Verify results
        self.assertEqual(results['status'], 'success')
        self.assertEqual(results['archived_count'], 1)
    
    def test_mask_pii_function(self):
        """Test standalone mask_pii function."""
        data = {"user": "Max Mustermann", "email": "max@example.com"}
        masked = mask_pii(data)
        
        # Verify masking
        self.assertNotEqual(masked['email'], "max@example.com")
        self.assertIn("*", masked['email'])
    
    def test_check_archive_function(self):
        """Test standalone check_archive function."""
        result = check_archive(archive_dir=self.archive_dir)
        
        # Should return True when no archives exist
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
