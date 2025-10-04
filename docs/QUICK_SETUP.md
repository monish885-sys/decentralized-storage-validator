# Quick Setup Guide

## 🚀 Step-by-Step Google Cloud Setup

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Set Environment Variable
```bash
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/firebase-service-account.json"
```

### 3. Google Cloud Console Setup

#### A. Create/Select Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing one
3. Note your **Project ID** (you'll need this)

#### B. Enable APIs
1. Go to [APIs & Services → Library](https://console.cloud.google.com/apis/library)
2. Enable:
   - **Google Drive API**
   - **Cloud Firestore API**

#### C. Create OAuth2 Credentials (for Google Drive)
1. Go to [APIs & Services → Credentials](https://console.cloud.google.com/apis/credentials)
2. Click "Create Credentials" → "OAuth client ID"
3. Configure OAuth consent screen if prompted
4. Choose "Desktop application"
5. Download JSON and save as `client_secret.json`

#### D. Create Service Account (for Firestore)
1. Go to [IAM & Admin → Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Create service account with roles:
   - `Cloud Datastore User`
   - `Firebase Admin SDK Administrator Service Agent`
3. Create and download JSON key
4. Save as `firebase-service-account.json`

#### E. Set up Firestore
1. Go to [Firestore](https://console.cloud.google.com/firestore)
2. Create database in production mode
3. Choose location

### 4. Update Project ID
```bash
python3 update_config.py
```

### 5. Verify Setup
```bash
python3 verify_setup.py
```

### 6. Test the System
```bash
# Create test file
echo "Hello World" > test.txt

# Upload file
python3 main.py upload test.txt

# List files
python3 main.py list

# Verify file
python3 main.py verify test.txt
```

## 🔧 Troubleshooting

### Common Issues:
1. **"Project not found"**: Update PROJECT_ID in config files
2. **"API not enabled"**: Enable Drive API and Firestore API
3. **"Authentication failed"**: Check credentials files
4. **"Permission denied"**: Check service account roles

### Quick Fixes:
```bash
# Reinstall dependencies
pip3 install --upgrade -r requirements.txt

# Check environment
echo $GOOGLE_APPLICATION_CREDENTIALS

# Verify files
ls -la client_secret.json firebase-service-account.json
```
