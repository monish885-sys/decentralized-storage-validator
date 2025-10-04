# Decentralized Cloud Storage Validator

A secure file integrity validation system that uses Google Drive for storage and Firestore for hash verification.

## Project Structure

```
decentralized-storage-validator/
├── src/                    # Source code
│   ├── main.py            # Main application
│   ├── enhanced_main.py   # Enhanced version with better error handling
│   ├── web_app.py         # Web interface
│   ├── mongodb_storage.py # MongoDB storage implementation
│   ├── local_storage.py   # Local storage utilities
│   ├── utils.py           # Utility functions
│   ├── config.py          # Configuration management
│   ├── complete_setup.py  # Complete setup script
│   ├── update_config.py   # Configuration updater
│   ├── verify_setup.py    # Setup verification
│   └── setup.sh           # Setup shell script
├── tests/                  # Test files
│   └── test_tampering.py  # Tampering detection tests
├── examples/               # Example files and test data
│   ├── test*.txt          # Test files
│   ├── mongodb_test.txt   # MongoDB test data
│   └── tampered_file.txt  # Example tampered file
├── docs/                   # Documentation
│   ├── README.md          # This file
│   ├── SETUP_GUIDE.md     # Detailed setup instructions
│   ├── QUICK_SETUP.md     # Quick setup guide
│   └── FINAL_SETUP_INSTRUCTIONS.md
├── config/                 # Configuration and runtime files
│   ├── logs/              # Log files
│   ├── temp/              # Temporary files
│   └── hash_storage.json  # Hash storage data
├── templates/              # Web templates
├── requirements.txt        # Python dependencies
└── .gitignore             # Git ignore rules
```

## Features

- **Secure Upload**: Upload files to Google Drive with SHA-256 hash verification
- **Integrity Verification**: Download and verify file integrity against stored hashes
- **Tamper Detection**: Detect if files have been altered in cloud storage
- **Metadata Management**: Store and retrieve file metadata including timestamps and sizes
- **File Management**: List and delete files from the system

## Setup

### 1. Prerequisites

- Python 3.7+
- Google Cloud Project with Drive API and Firestore enabled
- Google OAuth2 credentials

### 2. Installation

```bash
pip install -r requirements.txt
```

### 3. Configuration

1. **Google Drive API Setup**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Enable Google Drive API
   - Create OAuth2 credentials
   - Download `client_secret.json` and replace the placeholder in the project

2. **Firestore Setup**:
   - Enable Firestore in your Google Cloud project
   - Create a service account and download the JSON key
   - Save it as `firebase-service-account.json`
   - Set the environment variable: `export GOOGLE_APPLICATION_CREDENTIALS="firebase-service-account.json"`

3. **Update Configuration**:
   - Update `PROJECT_ID` in `main.py` with your Google Cloud project ID
   - Update `FIREBASE_DATABASE_ID` if using a named database

## Usage

### Upload a File
```bash
python src/main.py upload /path/to/your/file.pdf
```

### Verify File Integrity
```bash
python src/main.py verify filename.pdf
```

### List All Files
```bash
python src/main.py list
```

### Delete a File
```bash
python src/main.py delete filename.pdf
```

## Enhanced Version

The enhanced version (`enhanced_main.py`) includes:
- Better error handling and logging
- File size validation
- Interactive confirmation for deletions
- Detailed help messages

```bash
python src/enhanced_main.py upload document.pdf --description "Important document"
python src/enhanced_main.py list --detailed
python src/enhanced_main.py delete document.pdf --force
```

## How It Works

1. **Upload Process**:
   - Computes SHA-256 hash of the local file
   - Uploads file to Google Drive
   - Stores hash and metadata in Firestore

2. **Verification Process**:
   - Retrieves original hash from Firestore
   - Downloads file from Google Drive
   - Re-computes hash of downloaded file
   - Compares hashes to verify integrity

3. **Security Features**:
   - SHA-256 cryptographic hashing
   - Tamper detection
   - Secure OAuth2 authentication
   - Firestore for metadata storage

## Security Considerations

- Files are stored in Google Drive with standard Google security
- Hashes are stored separately in Firestore
- OAuth2 tokens are stored locally in `token.json`
- Service account credentials should be kept secure

## Troubleshooting

- Ensure all API credentials are properly configured
- Check that Google Drive API and Firestore are enabled
- Verify network connectivity for API calls
- Check file permissions for local files

## License

This project is for educational and demonstration purposes.
