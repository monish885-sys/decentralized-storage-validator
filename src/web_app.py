#!/usr/bin/env python3
"""
Flask Web API for Decentralized Storage Validator
"""

import os
import hashlib
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import mongodb_storage

# Import from main.py
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from io import BytesIO

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = 'temp'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure temp directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Google Drive configuration
SCOPES = ['https://www.googleapis.com/auth/drive']
TOKEN_FILE = 'token.json'

def get_drive_service():
    """Get authenticated Google Drive service"""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=8081, open_browser=False)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)

def compute_file_hash(file_path):
    """Compute SHA-256 hash of file"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/styles/<path:filename>')
def styles(filename):
    """Serve CSS files"""
    return send_from_directory('templates/styles', filename)

@app.route('/scripts/<path:filename>')
def serve_scripts(filename):
    """Serve JavaScript files"""
    return send_from_directory('templates/scripts', filename)

@app.route('/api/files', methods=['GET'])
def get_all_files():
    """Get all stored files"""
    try:
        storage = mongodb_storage.MongoDBStorage()
        files = []
        
        # Get files from MongoDB
        documents = storage.collection.find({"status": "active"}).sort("upload_date", -1)
        
        for doc in documents:
            # Convert ObjectId to string
            doc['_id'] = str(doc['_id'])
            files.append(doc)
        
        storage.close_connection()
        return jsonify({
            'success': True,
            'files': files,
            'count': len(files)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload a file to Google Drive and store hash in MongoDB"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                # Compute hash
                file_hash = compute_file_hash(filepath)
                
                # Upload to Google Drive
                service = get_drive_service()
                file_metadata = {'name': filename}
                media = MediaFileUpload(filepath, resumable=True)
                
                drive_file = service.files().create(
                    body=file_metadata, 
                    media_body=media, 
                    fields='id,name,size'
                ).execute()
                
                file_id = drive_file.get('id')
                file_size = os.path.getsize(filepath)
                
                # Store in MongoDB
                storage = mongodb_storage.MongoDBStorage()
                storage.store_file_hash(filename, file_hash, file_id, file_size)
                
                # Clean up temp file
                os.remove(filepath)
                
                storage.close_connection()
                
                return jsonify({
                    'success': True,
                    'message': 'File uploaded successfully',
                    'data': {
                        'filename': filename,
                        'hash': file_hash,
                        'drive_id': file_id,
                        'size': file_size,
                        'upload_time': datetime.now().isoformat()
                    }
                })
                
            except Exception as e:
                # Clean up temp file on error
                if os.path.exists(filepath):
                    os.remove(filepath)
                raise e

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }), 500

@app.route('/api/verify/<filename>', methods=['GET'])
def verify_file(filename):
    """Verify file integrity"""
    try:
        storage = mongodb_storage.MongoDBStorage()
        
        # Get file metadata
        file_data = storage.get_file_hash(filename)
        if not file_data:
            storage.close_connection()
            return jsonify({
                'success': False,
                'error': 'File not found in database'
            }), 404
        
        original_hash = file_data['hash']
        file_id = file_data['drive_id']
        
        # Download from Google Drive
        service = get_drive_service()
        request_obj = service.files().get_media(fileId=file_id)
        fh = BytesIO()
        downloader = MediaIoBaseDownload(fh, request_obj)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        downloaded_content = fh.getvalue()
        downloaded_hash = hashlib.sha256(downloaded_content).hexdigest()
        
        # Check integrity
        is_intact = original_hash == downloaded_hash
        trust_score = 100 if is_intact else 0
        
        # Update verification stats
        storage.update_verification(filename, "success" if is_intact else "tampered", trust_score)
        storage.close_connection()
        
        return jsonify({
            'success': True,
            'data': {
                'filename': filename,
                'is_intact': is_intact,
                'trust_score': trust_score,
                'original_hash': original_hash,
                'downloaded_hash': downloaded_hash,
                'file_size': len(downloaded_content),
                'verification_time': datetime.now().isoformat()
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Verification failed: {str(e)}'
        }), 500

@app.route('/api/verify-all', methods=['POST'])
def verify_all_files():
    """Verify all files at once"""
    try:
        storage = mongodb_storage.MongoDBStorage()
        files = storage.list_all_files()
        
        results = []
        verified_count = 0
        tampered_count = 0
        
        for filename in files:
            try:
                file_data = storage.get_file_hash(filename)
                if not file_data:
                    continue
                
                original_hash = file_data['hash']
                file_id = file_data['drive_id']
                
                # Download and verify
                service = get_drive_service()
                request_obj = service.files().get_media(fileId=file_id)
                fh = BytesIO()
                downloader = MediaIoBaseDownload(fh, request_obj)
                
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                
                downloaded_content = fh.getvalue()
                downloaded_hash = hashlib.sha256(downloaded_content).hexdigest()
                
                is_intact = original_hash == downloaded_hash
                trust_score = 100 if is_intact else 0
                
                if is_intact:
                    verified_count += 1
                else:
                    tampered_count += 1
                
                storage.update_verification(filename, "success" if is_intact else "tampered", trust_score)
                
                results.append({
                    'filename': filename,
                    'is_intact': is_intact,
                    'trust_score': trust_score,
                    'verified': True
                })
                
            except Exception as e:
                results.append({
                    'filename': filename,
                    'is_intact': False,
                    'trust_score': 0,
                    'verified': False,
                    'error': str(e)
                })
        
        total = len(results)
        security_percentage = (verified_count / total * 100) if total > 0 else 0
        
        storage.close_connection()
        
        return jsonify({
            'success': True,
            'data': {
                'verified_count': verified_count,
                'tampered_count': tampered_count,
                'total_files': total,
                'security_percentage': security_percentage,
                'results': results,
                'verification_time': datetime.now().isoformat()
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Batch verification failed: {str(e)}'
        }), 500

@app.route('/api/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    """Delete a file from both Google Drive and MongoDB"""
    try:
        storage = mongodb_storage.MongoDBStorage()
        
        # Get file metadata
        file_data = storage.get_file_hash(filename)
        if not file_data:
            storage.close_connection()
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
        
        file_id = file_data['drive_id']
        
        # Delete from Google Drive
        service = get_drive_service()
        service.files().delete(fileId=file_id).execute()
        
        # Soft delete from MongoDB
        storage.delete_file_hash(filename)
        storage.close_connection()
        
        return jsonify({
            'success': True,
            'message': 'File deleted successfully',
            'filename': filename,
            'deleted_time': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Delete failed: {str(e)}'
        }), 500

@app.route('/api/search', methods=['GET'])
def search_files():
    """Search files by name or hash"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query required'
            }), 400
        
        storage = mongodb_storage.MongoDBStorage()
        results = storage.search_files(query)
        storage.close_connection()
        
        return jsonify({
            'success': True,
            'data': {
                'query': query,
                'results': results,
                'count': len(results) if results else 0
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Search failed: {str(e)}'
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    try:
        storage = mongodb_storage.MongoDBStorage()
        stats = storage.get_database_stats()
        storage.close_connection()
        
        return jsonify({
            'success': True,
            'data': stats
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get statistics: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Decentralized Storage Validator Web App")
    print("🌐 Access at: http://localhost:8080")
    app.run(debug=True, host='0.0.0.0', port=8080)
