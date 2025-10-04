"""
Local hash storage for the Decentralized Cloud Storage Validator
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Local storage file path
STORAGE_FILE = Path(__file__).parent / "hash_storage.json"

def load_storage():
    """Load existing hash storage data"""
    if STORAGE_FILE.exists():
        try:
            with open(STORAGE_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_storage(data):
    """Save hash storage data"""
    with open(STORAGE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def store_file_hash(file_name, file_hash, drive_id, file_size):
    """Store file hash and metadata locally"""
    data = load_storage()
    data[file_name] = {
        'hash': file_hash,
        'drive_id': drive_id,
        'file_size': file_size,
        'timestamp': datetime.now().isoformat(),
        'upload_date': datetime.now().isoformat()
    }
    save_storage(data)
    print(f"Hash and metadata stored locally for: {file_name}")

def get_file_hash(file_name):
    """Retrieve file hash and metadata"""
    data = load_storage()
    if file_name in data:
        return data[file_name]
    return None

def list_all_files():
    """List all stored files"""
    data = load_storage()
    if not data:
        print("No files stored locally.")
        return []
    
    print("\n📁 Locally Stored Files:")
    print("=" * 50)
    for file_name, file_data in data.items():
        print(f"📄 {file_name}")
        print(f"   Hash: {file_data['hash'][:16]}...")
        print(f"   Drive ID: {file_data['drive_id']}")
        print(f"   Size: {file_data['file_size']} bytes")
        print(f"   Uploaded: {file_data['upload_date']}")
        print()
    
    return list(data.keys())

def delete_file_hash(file_name):
    """Delete file hash from local storage"""
    data = load_storage()
    if file_name in data:
        del data[file_name]
        save_storage(data)
        print(f"Removed {file_name} from local storage")
        return True
    else:
        print(f"{file_name} not found in local storage")
        return False
