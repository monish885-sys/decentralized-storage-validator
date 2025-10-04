# Google Cloud Setup Guide

This guide will walk you through setting up Google Cloud credentials for the Decentralized Cloud Storage Validator.

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name: `datavalidator-469205` (or your preferred name)
4. Click "Create"
5. Note your Project ID (you'll need this later)

## Step 2: Enable Required APIs

1. In the Google Cloud Console, go to "APIs & Services" → "Library"
2. Search for and enable:
   - **Google Drive API**
   - **Cloud Firestore API**

## Step 3: Create OAuth2 Credentials (for Google Drive)

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" user type
   - Fill in required fields (App name, User support email, Developer email)
   - Add your email to test users
4. For Application type, choose "Desktop application"
5. Name it: "Decentralized Storage Validator"
6. Click "Create"
7. Download the JSON file and save it as `client_secret.json` in your project directory

## Step 4: Create Service Account (for Firestore)

1. Go to "IAM & Admin" → "Service Accounts"
2. Click "Create Service Account"
3. Enter details:
   - Name: `firestore-admin`
   - Description: `Service account for Firestore access`
4. Click "Create and Continue"
5. Grant roles:
   - `Cloud Datastore User`
   - `Firebase Admin SDK Administrator Service Agent`
6. Click "Continue" → "Done"
7. Click on the created service account
8. Go to "Keys" tab → "Add Key" → "Create new key"
9. Choose "JSON" format
10. Download and save as `firebase-service-account.json` in your project directory

## Step 5: Set up Firestore Database

1. Go to "Firestore" in the Google Cloud Console
2. Click "Create database"
3. Choose "Start in production mode"
4. Select a location (choose closest to you)
5. Click "Create"

## Step 6: Update Configuration

Update the PROJECT_ID in your configuration files with your actual Google Cloud Project ID.

## Security Notes

- Never commit `client_secret.json` or `firebase-service-account.json` to version control
- Keep these files secure and private
- The `.gitignore` file is already configured to exclude these files
