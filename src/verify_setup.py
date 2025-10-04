#!/usr/bin/env python3
"""
Script to verify Google Cloud setup and credentials
"""

import os
import json
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and provide status"""
    path = Path(filepath)
    if path.exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} (NOT FOUND)")
        return False

def validate_json_file(filepath, required_fields, description):
    """Validate JSON file structure"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        missing_fields = []
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"⚠️  {description}: Missing fields {missing_fields}")
            return False
        else:
            print(f"✅ {description}: Valid structure")
            return True
            
    except json.JSONDecodeError as e:
        print(f"❌ {description}: Invalid JSON - {e}")
        return False
    except Exception as e:
        print(f"❌ {description}: Error reading file - {e}")
        return False

def check_environment():
    """Check environment variables"""
    google_creds = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    if google_creds:
        print(f"✅ GOOGLE_APPLICATION_CREDENTIALS: {google_creds}")
        if Path(google_creds).exists():
            print("✅ Service account file exists")
        else:
            print("❌ Service account file not found at specified path")
    else:
        print("⚠️  GOOGLE_APPLICATION_CREDENTIALS not set")

def main():
    print("🔍 Google Cloud Setup Verification")
    print("=" * 40)
    
    # Check required files
    files_to_check = [
        ("client_secret.json", "Google Drive OAuth2 credentials"),
        ("firebase-service-account.json", "Firestore service account"),
        ("main.py", "Main application script"),
        ("config.py", "Configuration file"),
        ("requirements.txt", "Python dependencies")
    ]
    
    all_files_exist = True
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_files_exist = False
    
    print("\n📋 Credential Validation:")
    
    # Validate client_secret.json
    if Path("client_secret.json").exists():
        validate_json_file(
            "client_secret.json",
            ["installed", "client_id", "client_secret", "project_id"],
            "Google Drive OAuth2 credentials"
        )
    
    # Validate firebase-service-account.json
    if Path("firebase-service-account.json").exists():
        validate_json_file(
            "firebase-service-account.json",
            ["type", "project_id", "private_key", "client_email"],
            "Firestore service account"
        )
    
    print("\n🌍 Environment Check:")
    check_environment()
    
    print("\n📊 Summary:")
    if all_files_exist:
        print("✅ All required files are present")
        print("📝 Next steps:")
        print("   1. Ensure your Google Cloud project has Drive API and Firestore enabled")
        print("   2. Test with: python main.py list")
        print("   3. Upload a test file: python main.py upload test.txt")
    else:
        print("❌ Some required files are missing")
        print("📝 Please follow the SETUP_GUIDE.md to download missing credentials")

if __name__ == "__main__":
    main()
