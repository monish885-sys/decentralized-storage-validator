#!/usr/bin/env python3
"""
Complete setup script for Decentralized Cloud Storage Validator
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def print_header():
    print("🚀 Decentralized Cloud Storage Validator - Complete Setup")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7+ is required. Current version:", sys.version)
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Set up environment variables"""
    print("\n🌍 Setting up environment...")
    
    # Set GOOGLE_APPLICATION_CREDENTIALS
    service_account_path = Path("firebase-service-account.json").absolute()
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(service_account_path)
    
    print(f"✅ GOOGLE_APPLICATION_CREDENTIALS set to: {service_account_path}")
    return True

def open_google_cloud_console():
    """Open Google Cloud Console in browser"""
    print("\n🌐 Opening Google Cloud Console...")
    urls = [
        "https://console.cloud.google.com/",
        "https://console.cloud.google.com/apis/library",
        "https://console.cloud.google.com/apis/credentials",
        "https://console.cloud.google.com/firestore"
    ]
    
    print("📋 Please complete these steps in Google Cloud Console:")
    print("   1. Create a new project or select existing one")
    print("   2. Enable Google Drive API")
    print("   3. Enable Cloud Firestore API")
    print("   4. Create OAuth2 credentials (Desktop application)")
    print("   5. Create Service Account for Firestore")
    
    response = input("\nOpen Google Cloud Console in browser? (y/N): ")
    if response.lower() in ['y', 'yes']:
        for url in urls:
            webbrowser.open(url)
            break
        print("✅ Google Cloud Console opened in browser")

def update_project_config():
    """Update project configuration"""
    print("\n⚙️  Project Configuration")
    
    # Check if update_config.py exists and run it
    if Path("update_config.py").exists():
        response = input("Run project ID configuration updater? (y/N): ")
        if response.lower() in ['y', 'yes']:
            subprocess.run([sys.executable, "update_config.py"])
    else:
        print("ℹ️  Please manually update PROJECT_ID in main.py and config.py")

def verify_credentials():
    """Verify that credentials are properly set up"""
    print("\n🔍 Verifying credentials...")
    
    if Path("verify_setup.py").exists():
        subprocess.run([sys.executable, "verify_setup.py"])
    else:
        print("ℹ️  Please run: python verify_setup.py")

def create_test_file():
    """Create a test file for upload"""
    test_file = Path("test_file.txt")
    if not test_file.exists():
        with open(test_file, 'w') as f:
            f.write("This is a test file for the Decentralized Cloud Storage Validator.\n")
            f.write("Created during setup process.\n")
        print(f"✅ Created test file: {test_file}")
    else:
        print(f"ℹ️  Test file already exists: {test_file}")

def main():
    print_header()
    
    # Step 1: Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Step 2: Install dependencies
    if not install_dependencies():
        print("⚠️  Continuing without installing dependencies...")
    
    # Step 3: Set up environment
    setup_environment()
    
    # Step 4: Open Google Cloud Console
    open_google_cloud_console()
    
    # Step 5: Update project configuration
    update_project_config()
    
    # Step 6: Create test file
    create_test_file()
    
    # Step 7: Verify setup
    verify_credentials()
    
    print("\n🎉 Setup Complete!")
    print("\n📝 Next Steps:")
    print("   1. Download your credentials from Google Cloud Console")
    print("   2. Replace client_secret.json and firebase-service-account.json")
    print("   3. Test the setup:")
    print("      python main.py list")
    print("      python main.py upload test_file.txt")
    print("      python main.py verify test_file.txt")
    
    print("\n📚 Documentation:")
    print("   - README.md: Complete usage guide")
    print("   - SETUP_GUIDE.md: Detailed Google Cloud setup")
    print("   - Run 'python main.py --help' for command help")

if __name__ == "__main__":
    main()
