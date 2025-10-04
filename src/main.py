import argparse
import hashlib
import os
import requests
from io import BytesIO
import json
from datetime import datetime
import webbrowser

# Google Drive and Firestore imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload
# from google.cloud import firestore  # Disabled for MongoDB storage
import mongodb_storage as storage

# Configure Chrome browser for OAuth
chrome_path = '/Applications/Google Chrome.app'
if os.path.exists(chrome_path):
    webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
PROJECT_ID = "data-473906"  # <<< Your new Google Cloud Project ID
FIREBASE_DATABASE_ID = "cloud"       # <<< Your named Firestore database ID
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']

# -----------------------------------------------------------------------------
# Client Initialization (Local Storage)
# -----------------------------------------------------------------------------
# Using local storage instead of Firestore

def get_drive_service():
    """
    Handles Google Drive API authentication and returns a service object.
    The first time you run this, a browser window will open for authentication.
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', scopes=SCOPES)
            creds = flow.run_local_server(port=8082)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)

def upload_and_hash(file_path):
    """
    Computes hash, uploads the file to Google Drive, and stores the hash in Firestore.
    """
    try:
        # Validate file exists
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found.")
            return
        
        # Step 1: Compute the SHA-256 hash
        print(f"Computing hash for {file_path}...")
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        print(f"File hash created: {file_hash}")
        
        # Step 2: Upload the file to Google Drive
        service = get_drive_service()
        file_name = os.path.basename(file_path)
        file_metadata = {'name': file_name}
        media = MediaFileUpload(file_path, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id, name').execute()
        file_id = file.get('id')
        print(f"File uploaded successfully to Google Drive. File ID: {file_id}, Name: {file_name}")

        # Step 3: Store the hash and ID in MongoDB
        print("Storing hash and Drive ID in MongoDB...")
        storage.store_file_hash(file_name, file_hash, file_id, os.path.getsize(file_path))
        print("Hash and Drive ID stored successfully.")
        print("Your unique code for this file is:", file_name)

    except Exception as e:
        print(f"An error occurred during upload: {e}")

def verify_and_match(file_name):
    """
    Downloads the file from Google Drive, re-hashes it, and compares with the stored hash.
    """
    try:
        # Step 1: Retrieve original hash and Drive ID from MongoDB
        print(f"Retrieving metadata for {file_name} from MongoDB...")
        stored_data = storage.get_file_hash(file_name)

        if not stored_data:
            print(f"Error: No metadata found for '{file_name}'.")
            return
        
        original_hash = stored_data['hash']
        file_id = stored_data['drive_id']
        print(f"Original hash found: {original_hash}")

        # Step 2: Download the file from Google Drive
        print(f"Downloading file with ID {file_id} from Google Drive...")
        service = get_drive_service()
        request = service.files().get_media(fileId=file_id)
        fh = BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        downloaded_content = fh.getvalue()
        
        # Step 3: Re-compute the hash of the downloaded content
        print("Re-computing hash of downloaded file...")
        downloaded_hash = hashlib.sha256(downloaded_content).hexdigest()
        print(f"Downloaded file's hash: {downloaded_hash}")

        # Step 4: Compare the hashes and show the result
        if original_hash == downloaded_hash:
            print("\n✅ Verification Successful! The file is intact. Trust Score: 100%")
            print(f"File size: {len(downloaded_content)} bytes")
            # Update verification stats in MongoDB
            db_storage = storage.MongoDBStorage()
            db_storage.update_verification(file_name, "success", 100)
            db_storage.close_connection()
        else:
            print("\n🚨🚨🚨 SECURITY ALERT - FILE TAMPERING DETECTED! 🚨🚨🚨")
            print("=" * 60)
            print("❌ WARNING: This file has been modified or corrupted!")
            print("📊 SECURITY ANALYSIS:")
            print(f"   👤 Original Hash:   {original_hash}")
            print(f"   🔍 Current Hash:    {downloaded_hash}")
            print(f"   📏 File Size:       {len(downloaded_content)} bytes")
            print("\n⚠️  RECOMMENDATIONS:")
            print("   • Do NOT trust this file")
            print("   • Contact the file owner immediately")
            print("   • Do not open or execute this file")
            print("   • Try downloading from original source")
            print("=" * 60)
            # Update verification stats in MongoDB
            db_storage = storage.MongoDBStorage()
            db_storage.update_verification(file_name, "tampered", 0)
            db_storage.close_connection()

    except Exception as e:
        print(f"An error occurred during verification: {e}")

def list_files():
    """
    List all files stored in the system with their metadata.
    """
    try:
        storage.list_all_files()
    except Exception as e:
        print(f"An error occurred while listing files: {e}")

def verify_all_files():
    """
    Verify integrity of all stored files at once.
    """
    print("🔍 STARTING BATCH VERIFICATION OF ALL FILES")
    print("=" * 50)
    
    try:
        files = storage.list_all_files()
        
        if not files:
            print("❌ No files to verify.")
            return
        
        verified_count = 0
        tampered_count = 0
        
        for file_name in files:
            print(f"\n🔍 Verifying: {file_name}")
            print("-" * 30)
            
            try:
                stored_data = storage.get_file_hash(file_name)
                if not stored_data:
                    print(f"❌ No metadata found for {file_name}")
                    continue
                
                original_hash = stored_data['hash']
                file_id = stored_data['drive_id']
                
                # Download and verify
                service = get_drive_service()
                request = service.files().get_media(fileId=file_id)
                fh = BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                
                downloaded_content = fh.getvalue()
                downloaded_hash = hashlib.sha256(downloaded_content).hexdigest()
                
                if original_hash == downloaded_hash:
                    print(f"✅ INTACT - Trust Score: 100%")
                    verified_count += 1
                    db_storage = storage.MongoDBStorage()
                    db_storage.update_verification(file_name, "success", 100)
                    db_storage.close_connection()
                else:
                    print(f"🚨 TAMPERED - Trust Score: 0%")
                    tampered_count += 1
                    db_storage = storage.MongoDBStorage()
                    db_storage.update_verification(file_name, "tampered", 0)
                    db_storage.close_connection()
                    
            except Exception as e:
                print(f"❌ Error verifying {file_name}: {e}")
        
        # Summary
        print(f"\n📊 VERIFICATION SUMMARY")
        print("=" * 50)
        print(f"✅ Intact files: {verified_count}")
        print(f"🚨 Tampered files: {tampered_count}")
        total = verified_count + tampered_count
        if total > 0:
            security_percentage = (verified_count / total) * 100
            print(f"🔒 Overall Security Score: {security_percentage:.1f}%")
            
            if tampered_count > 0:
                print(f"\n⚠️  SECURITY ALERT: {tampered_count} file(s) have been tampered!")
                print("🚨 Immediate action required!")
        else:
            print("❌ No files were verified.")
            
    except Exception as e:
        print(f"An error occurred during batch verification: {e}")

def delete_file(file_name):
    """
    Delete a file from both Google Drive and MongoDB storage.
    """
    try:
        # Get metadata from MongoDB
        stored_data = storage.get_file_hash(file_name)
        
        if not stored_data:
            print(f"Error: No metadata found for '{file_name}'.")
            return
        
        file_id = stored_data['drive_id']
        
        # Delete from Google Drive
        service = get_drive_service()
        service.files().delete(fileId=file_id).execute()
        print(f"File deleted from Google Drive: {file_id}")
        
        # Delete from MongoDB (soft delete)
        storage.delete_file_hash(file_name)
        print(f"✅ File '{file_name}' successfully deleted from the system.")
        
    except Exception as e:
        print(f"An error occurred during deletion: {e}")

def search_files(query):
    """Search files by name or hash"""
    try:
        db_storage = storage.MongoDBStorage()
        db_storage.search_files(query)
        db_storage.close_connection()
    except Exception as e:
        print(f"An error occurred while searching: {e}")

def show_database_stats():
    """Show MongoDB database statistics"""
    try:
        db_storage = storage.MongoDBStorage()
        db_storage.get_database_stats()
        db_storage.close_connection()
    except Exception as e:
        print(f"An error occurred while getting stats: {e}")

def migrate_to_mongodb():
    """Migrate existing JSON data to MongoDB"""
    try:
        db_storage = storage.MongoDBStorage()
        migrated_count = db_storage.migrate_from_json()
        print(f"\n🔄 Migration Summary:")
        print(f"Files migrated: {migrated_count}")
        print(f"Storage: JSON → MongoDB")
        db_storage.close_connection()
    except Exception as e:
        print(f"An error occurred during migration: {e}")

# Main CLI logic
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A Decentralized Cloud Storage Validator MVP.")
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available commands')

    upload_parser = subparsers.add_parser('upload', help='Upload a file to Google Drive and store its hash.')
    upload_parser.add_argument('file_path', type=str, help='The path to the file on your local machine.')

    verify_parser = subparsers.add_parser('verify', help='Verify the integrity of a file stored in Google Drive.')
    verify_parser.add_argument('file_name', type=str, help='The name of the file to verify (e.g., my_document.pdf).')

    list_parser = subparsers.add_parser('list', help='List all files stored in the system.')

    verify_all_parser = subparsers.add_parser('verify-all', help='Verify integrity of all stored files at once.')

    search_parser = subparsers.add_parser('search', help='Search files by name or hash.')
    search_parser.add_argument('query', type=str, help='Search term (file name or partial hash).')

    stats_parser = subparsers.add_parser('stats', help='Show database statistics.')

    migrate_parser = subparsers.add_parser('migrate', help='Migrate data from JSON to MongoDB.')

    delete_parser = subparsers.add_parser('delete', help='Delete a file from both Google Drive and MongoDB storage.')
    delete_parser.add_argument('file_name', type=str, help='The name of the file to delete.')

    args = parser.parse_args()

    if args.command == 'upload':
        upload_and_hash(args.file_path)
    elif args.command == 'verify':
        verify_and_match(args.file_name)
    elif args.command == 'list':
        list_files()
    elif args.command == 'verify-all':
        verify_all_files()
    elif args.command == 'search':
        search_files(args.query)
    elif args.command == 'stats':
        show_database_stats()
    elif args.command == 'migrate':
        migrate_to_mongodb()
    elif args.command == 'delete':
        delete_file(args.file_name)
