"""
Utility functions for the Decentralized Cloud Storage Validator
"""

import hashlib
import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Set up logging configuration
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/validator.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def compute_file_hash(file_path: str, algorithm: str = "sha256") -> Optional[str]:
    """
    Compute hash of a file using the specified algorithm
    """
    try:
        hash_obj = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception as e:
        logging.error(f"Error computing hash for {file_path}: {e}")
        return None

def validate_file_path(file_path: str) -> bool:
    """
    Validate that a file path exists and is readable
    """
    path = Path(file_path)
    return path.exists() and path.is_file() and os.access(file_path, os.R_OK)

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def truncate_hash(hash_str: str, length: int = 16) -> str:
    """
    Truncate hash string for display purposes
    """
    return f"{hash_str[:length]}..." if len(hash_str) > length else hash_str

def create_metadata(file_path: str, file_hash: str, drive_id: str) -> Dict[str, Any]:
    """
    Create metadata dictionary for Firestore
    """
    path = Path(file_path)
    return {
        'hash': file_hash,
        'drive_id': drive_id,
        'file_size': path.stat().st_size,
        'upload_date': datetime.now().isoformat(),
        'file_extension': path.suffix,
        'original_path': str(path.absolute())
    }

def validate_metadata(metadata: Dict[str, Any]) -> bool:
    """
    Validate that metadata contains required fields
    """
    required_fields = ['hash', 'drive_id', 'file_size', 'upload_date']
    return all(field in metadata for field in required_fields)
