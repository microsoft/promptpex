"""Test helper functions."""
import pytest
from promptpex.utils.helpers import hash_string


def test_hash_string():
    """Test string hashing function."""
    # Test basic hashing
    hash1 = hash_string("test string")
    hash2 = hash_string("test string")
    hash3 = hash_string("different string")
    
    # Same string should produce same hash
    assert hash1 == hash2
    
    # Different strings should produce different hashes
    assert hash1 != hash3
    
    # Hash should be a string
    assert isinstance(hash1, str)
    
    # Test empty string
    empty_hash = hash_string("")
    assert isinstance(empty_hash, str)
    
    # Test unicode
    unicode_hash = hash_string("测试字符串")
    assert isinstance(unicode_hash, str)