"""
MongoDB storage for the Decentralized Cloud Storage Validator
"""

import json
import os
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# MongoDB configuration
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "decentralized_storage"
COLLECTION_NAME = "file_hashes"

class MongoDBStorage:
    def __init__(self):
        """Initialize MongoDB connection"""
        try:
            self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.server_info()
            self.db = self.client[DATABASE_NAME]
            self.collection = self.db[COLLECTION_NAME]
            
            # Create indexes for better performance
            self.collection.create_index("file_name", unique=True)
            self.collection.create_index([("upload_date", -1)])
            self.collection.create_index("hash")
            
            print("✅ Connected to MongoDB successfully")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            print("💡 Make sure MongoDB is running locally")
            raise
            
        except Exception as e:
            print(f"❌ Unexpected error connecting to MongoDB: {e}")
            raise

    def store_file_hash(self, file_name, file_hash, drive_id, file_size):
        """Store file hash and metadata in MongoDB"""
        try:
            # Check if file already exists
            existing = self.collection.find_one({"file_name": file_name})
            
            file_data = {
                "file_name": file_name,
                "hash": file_hash,
                "drive_id": drive_id,
                "file_size": file_size,
                "timestamp": datetime.now(),
                "upload_date": datetime.now().isoformat(),
                "last_verified": None,
                "verify_count": 0,
                "status": "active"
            }
            
            if existing:
                # Update existing record
                result = self.collection.replace_one(
                    {"file_name": file_name}, 
                    file_data,
                    upsert=True
                )
                print(f"📝 Updated existing file in MongoDB: {file_name}")
            else:
                # Insert new record
                result = self.collection.insert_one(file_data)
                print(f"📊 Stored new file in MongoDB: {file_name}")
                
            return str(result.inserted_id) if hasattr(result, 'inserted_id') else "updated"
            
        except Exception as e:
            print(f"❌ Error storing file in MongoDB: {e}")
            raise

    def get_file_hash(self, file_name):
        """Retrieve file hash and metadata from MongoDB"""
        try:
            doc = self.collection.find_one({"file_name": file_name})
            if doc:
                # Convert ObjectId to string and remove MongoDB-specific fields
                doc['_id'] = str(doc['_id'])
                return doc
            return None
            
        except Exception as e:
            print(f"❌ Error retrieving file from MongoDB: {e}")
            raise

    def list_all_files(self):
        """List all stored files from MongoDB"""
        try:
            files = list(self.collection.find({"status": "active"}).sort("upload_date", -1))
            
            if not files:
                print("\n📁 No files stored in MongoDB.")
                return []
            
            print("\n📁 Files Stored in MongoDB:")
            print("=" * 60)
            
            for file_doc in files:
                print(f"📄 {file_doc['file_name']}")
                print(f"   Hash: {file_doc['hash'][:16]}...")
                print(f"   Drive ID: {file_doc['drive_id']}")
                print(f"   Size: {file_doc['file_size']} bytes")
                print(f"   Uploaded: {file_doc['upload_date']}")
                
                if file_doc.get('verify_count', 0) > 0:
                    print(f"   Last Verified: {file_doc.get('last_verified', 'Never')}")
                    print(f"   Verify Count: {file_doc.get('verify_count', 0)}")
                    
                print()
            
            print(f"📊 Total files in MongoDB: {len(files)}")
            return [doc['file_name'] for doc in files]
            
        except Exception as e:
            print(f"❌ Error listing files in MongoDB: {e}")
            raise

    def delete_file_hash(self, file_name):
        """Delete file hash from MongoDB (soft delete)"""
        try:
            # Soft delete - mark as inactive instead of actually removing
            result = self.collection.update_one(
                {"file_name": file_name},
                {
                    "$set": {
                        "status": "deleted",
                        "deleted_at": datetime.now().isoformat()
                    }
                }
            )
            
            if result.modified_count > 0:
                print(f"🗑️ Soft deleted {file_name} from MongoDB")
                return True
            else:
                print(f"❌ File {file_name} not found in MongoDB")
                return False
                
        except Exception as e:
            print(f"❌ Error deleting file from MongoDB: {e}")
            raise

    def update_verification(self, file_name, verification_status, trust_score):
        """Update verification statistics for a file"""
        try:
            result = self.collection.update_one(
                {"file_name": file_name},
                {
                    "$set": {
                        "last_verified": datetime.now().isoformat(),
                        "last_trust_score": trust_score
                    },
                    "$inc": {"verify_count": 1}
                }
            )
            
            if result.modified_count > 0:
                print(f"📊 Updated verification stats for {file_name}")
                return True
            else:
                print(f"❌ File {file_name} not found for verification update")
                return False
                
        except Exception as e:
            print(f"❌ Error updating verification stats: {e}")
            raise

    def search_files(self, query):
        """Search files by name or hash partial match"""
        try:
            regex_query = {"$regex": query, "$options": "i"}
            files = list(self.collection.find({
                "$or": [
                    {"file_name": regex_query},
                    {"hash": regex_query}
                ],
                "status": "active"
            }))
            
            if files:
                print(f"\n🔍 Search Results for '{query}':")
                print("=" * 40)
                for file_doc in files:
                    print(f"📄 {file_doc['file_name']}")
                    print(f"   Hash: {file_doc['hash'][:16]}...")
                    print(f"   Size: {file_doc['file_size']} bytes")
                    print()
            else:
                print(f"❌ No files found matching '{query}'")
                
            return files
            
        except Exception as e:
            print(f"❌ Error searching files: {e}")
            raise

    def get_database_stats(self):
        """Get database statistics"""
        try:
            total_files = self.collection.count_documents({"status": "active"})
            deleted_files = self.collection.count_documents({"status": "deleted"})
            total_size = self.collection.aggregate([
                {"$match": {"status": "active"}},
                {"$group": {"_id": None, "total": {"$sum": "$file_size"}}}
            ])
            
            total_size_bytes = next(total_size, {}).get('total', 0)
            
            print(f"\n📊 MongoDB Database Statistics:")
            print(f"📄 Active files: {total_files}")
            print(f"🗑️ Deleted files: {deleted_files}")
            print(f"💾 Total storage: {total_size_bytes:,} bytes")
            
            return {
                "active_files": total_files,
                "deleted_files": deleted_files,
                "total_storage_bytes": total_size_bytes
            }
            
        except Exception as e:
            print(f"❌ Error getting database stats: {e}")
            raise

    def migrate_from_json(self, json_file_path="hash_storage.json"):
        """Migrate data from existing JSON file to MongoDB"""
        try:
            if not os.path.exists(json_file_path):
                print(f"📁 No JSON file found at {json_file_path}")
                return 0
                
            with open(json_file_path, 'r') as f:
                json_data = json.load(f)
            
            migrated_count = 0
            for file_name, file_data in json_data.items():
                try:
                    self.store_file_hash(
                        file_name=file_name,
                        file_hash=file_data['hash'],
                        drive_id=file_data['drive_id'],
                        file_size=file_data['file_size']
                    )
                    migrated_count += 1
                    
                except Exception as e:
                    print(f"⚠️ Error migrating {file_name}: {e}")
                    
            print(f"✅ Successfully migrated {migrated_count} files to MongoDB")
            return migrated_count
            
        except Exception as e:
            print(f"❌ Error migrating from JSON: {e}")
            raise

    def close_connection(self):
        """Close MongoDB connection"""
        try:
            self.client.close()
            print("🔌 MongoDB connection closed")
        except Exception as e:
            print(f"❌ Error closing MongoDB connection: {e}")


# Convenience functions for backward compatibility
def load_storage():
    """Load existing hash storage data (deprecated - use MongoDB)"""
    return {}

def save_storage(data):
    """Save hash storage data (deprecated - use MongoDB)"""
    pass

def store_file_hash(file_name, file_hash, drive_id, file_size):
    """Store file hash and metadata"""
    storage = MongoDBStorage()
    try:
        return storage.store_file_hash(file_name, file_hash, drive_id, file_size)
    finally:
        storage.close_connection()

def get_file_hash(file_name):
    """Retrieve file hash and metadata"""
    storage = MongoDBStorage()
    try:
        return storage.get_file_hash(file_name)
    finally:
        storage.close_connection()

def list_all_files():
    """List all stored files"""
    storage = MongoDBStorage()
    try:
        return storage.list_all_files()
    finally:
        storage.close_connection()

def delete_file_hash(file_name):
    """Delete file hash from storage"""
    storage = MongoDBStorage()
    try:
        return storage.delete_file_hash(file_name)
    finally:
        storage.close_connection()
