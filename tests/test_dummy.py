"""
test_dummy.py - Dummy Test for CI Validation

Dummy test to ensure test discovery always works.

This test file guarantees that pytest will always find at least one test,
preventing test collection failures in CI environments.
"""

import pytest


class TestDummy:
    """Dummy test class to validate test discovery."""
    
    def test_dummy_always_passes(self):
        """Dummy test that always passes - validates test discovery works."""
        assert True
    
    def test_dummy_basic_math(self):
        """Basic math test to validate pytest is working."""
        assert 1 + 1 == 2
        assert 2 * 2 == 4
    
    def test_dummy_string_operations(self):
        """Basic string test to validate pytest is working."""
        assert "hello" + " " + "world" == "hello world"
        assert "test".upper() == "TEST"


def test_dummy_standalone():
    """Standalone dummy test function."""
    assert isinstance("test", str)
    assert isinstance(42, int)
    assert isinstance(3.14, float)


def test_dummy_basic_assertion():
    """Test basic Python assertions."""
    assert 1 + 1 == 2
    assert "test" in "test_dummy"
    assert [] == []


def test_dummy_import_pytest():
    """Test that pytest can be imported."""
    assert pytest is not None
