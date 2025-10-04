"""
Configuration settings for the Decentralized Cloud Storage Validator
"""

import os
from pathlib import Path

# Project Configuration
PROJECT_ID = "data-473906"  # Your new Google Cloud Project ID
FIREBASE_DATABASE_ID = "cloud"       # Update if using a named Firestore database

# API Scopes
SCOPES = ['https://www.googleapis.com/auth/drive']

# File Paths
BASE_DIR = Path(__file__).parent
CLIENT_SECRET_FILE = BASE_DIR / "client_secret.json"
TOKEN_FILE = BASE_DIR / "token.json"
SERVICE_ACCOUNT_FILE = BASE_DIR / "firebase-service-account.json"
LOGS_DIR = BASE_DIR / "logs"
TEMP_DIR = BASE_DIR / "temp"

# Create directories if they don't exist
LOGS_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# Environment Variables
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', str(SERVICE_ACCOUNT_FILE))

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# File Upload Configuration
MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024  # 5GB
CHUNK_SIZE = 1024 * 1024  # 1MB chunks for resumable uploads

# Hash Configuration
HASH_ALGORITHM = "sha256"
HASH_DISPLAY_LENGTH = 16  # Show first 16 characters of hash in listings
