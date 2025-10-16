"""
Dummy test to ensure test discovery always works.

This test file guarantees that pytest will always find at least one test,
preventing test collection failures in CI environments.
"""


def test_dummy_always_passes():
    """A dummy test that always passes to ensure test discovery works."""
    assert True, "Dummy test should always pass"


def test_dummy_basic_assertion():
    """Test basic Python assertions."""
    assert 1 + 1 == 2
    assert "test" in "test_dummy"
    assert [] == []


def test_dummy_import_pytest():
    """Test that pytest can be imported."""
    import pytest
    assert pytest is not None
