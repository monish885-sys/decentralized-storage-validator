#!/bin/bash

echo "Setting up Decentralized Cloud Storage Validator..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3.7+ and try again."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p logs
mkdir -p temp

# Set up environment variables
echo "Setting up environment variables..."
export GOOGLE_APPLICATION_CREDENTIALS="firebase-service-account.json"

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Configure your Google Cloud credentials:"
echo "   - Download client_secret.json from Google Cloud Console"
echo "   - Download firebase-service-account.json from Google Cloud Console"
echo "2. Update PROJECT_ID in main.py with your Google Cloud project ID"
echo "3. Run: source venv/bin/activate"
echo "4. Test with: python main.py list"
