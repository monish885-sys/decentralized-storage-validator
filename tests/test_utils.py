"""
Unit tests for utility functions
"""

import pytest
import tempfile
import os
from pathlib import Path
from utils import compute_file_hash, validate_file_path, format_file_size, truncate_hash

def test_compute_file_hash():
    """Test hash computation"""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"test content")
        tmp_path = tmp.name
    
    try:
        hash_result = compute_file_hash(tmp_path)
        assert hash_result is not None
        assert len(hash_result) == 64  # SHA-256 produces 64 character hex string
    finally:
        os.unlink(tmp_path)

def test_validate_file_path():
    """Test file path validation"""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"test")
        tmp_path = tmp.name
    
    try:
        assert validate_file_path(tmp_path) == True
        assert validate_file_path("/nonexistent/file") == False
    finally:
        os.unlink(tmp_path)

def test_format_file_size():
    """Test file size formatting"""
    assert format_file_size(0) == "0 B"
    assert format_file_size(1024) == "1.0 KB"
    assert format_file_size(1024 * 1024) == "1.0 MB"
    assert format_file_size(1024 * 1024 * 1024) == "1.0 GB"

def test_truncate_hash():
    """Test hash truncation"""
    long_hash = "a" * 64
    assert truncate_hash(long_hash, 16) == "aaaaaaaaaaaaaaaa..."
    assert truncate_hash("short", 16) == "short"
