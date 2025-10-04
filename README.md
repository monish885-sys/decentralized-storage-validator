# Decentralized Cloud Storage Validator

A secure file integrity validation system that uses Google Drive for storage and Firestore for hash verification.

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd decentralized-storage-validator
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup configuration**:
   - Follow the detailed setup guide in `docs/SETUP_GUIDE.md`
   - Or use the quick setup: `docs/QUICK_SETUP.md`

4. **Run the application**:
   ```bash
   python src/main.py upload examples/test1.txt
   python src/main.py list
   ```

## Project Structure

- `src/` - Source code and main application files
- `tests/` - Test files and test data
- `examples/` - Example files and sample data
- `docs/` - Documentation and setup guides
- `config/` - Configuration files and runtime data
- `templates/` - Web interface templates

## Features

- **Secure Upload**: Upload files to Google Drive with SHA-256 hash verification
- **Integrity Verification**: Download and verify file integrity against stored hashes
- **Tamper Detection**: Detect if files have been altered in cloud storage
- **Metadata Management**: Store and retrieve file metadata including timestamps and sizes
- **File Management**: List and delete files from the system
- **Web Interface**: Browser-based file management interface

## Documentation

- [Setup Guide](docs/SETUP_GUIDE.md) - Detailed setup instructions
- [Quick Setup](docs/QUICK_SETUP.md) - Quick setup guide
- [Final Setup Instructions](docs/FINAL_SETUP_INSTRUCTIONS.md) - Complete setup walkthrough

## Security

This system provides cryptographic file integrity verification using SHA-256 hashing. Files are stored in Google Drive with metadata stored separately in Firestore for enhanced security.

## License

This project is for educational and demonstration purposes.
