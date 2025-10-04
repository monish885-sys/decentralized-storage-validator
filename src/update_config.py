#!/usr/bin/env python3
"""
Script to update PROJECT_ID in configuration files
"""

import os
import re
from pathlib import Path

def update_project_id(new_project_id):
    """
    Update PROJECT_ID in all configuration files
    """
    files_to_update = [
        'main.py',
        'config.py',
        'client_secret.json',
        'firebase-service-account.json'
    ]
    
    updated_files = []
    
    for filename in files_to_update:
        file_path = Path(filename)
        if not file_path.exists():
            print(f"Warning: {filename} not found, skipping...")
            continue
            
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            original_content = content
            
            if filename.endswith('.py'):
                # Update Python files
                content = re.sub(
                    r'PROJECT_ID = "[^"]*"',
                    f'PROJECT_ID = "{new_project_id}"',
                    content
                )
                content = re.sub(
                    r'project_id = "[^"]*"',
                    f'project_id = "{new_project_id}"',
                    content
                )
            elif filename.endswith('.json'):
                # Update JSON files
                content = re.sub(
                    r'"project_id": "[^"]*"',
                    f'"project_id": "{new_project_id}"',
                    content
                )
                content = re.sub(
                    r'"projectId": "[^"]*"',
                    f'"projectId": "{new_project_id}"',
                    content
                )
            
            if content != original_content:
                with open(file_path, 'w') as f:
                    f.write(content)
                updated_files.append(filename)
                print(f"✅ Updated {filename}")
            else:
                print(f"ℹ️  No changes needed for {filename}")
                
        except Exception as e:
            print(f"❌ Error updating {filename}: {e}")
    
    if updated_files:
        print(f"\n🎉 Successfully updated PROJECT_ID to '{new_project_id}' in {len(updated_files)} files:")
        for file in updated_files:
            print(f"   - {file}")
    else:
        print("\n⚠️  No files were updated. Please check the project ID format.")

def main():
    print("🔧 Google Cloud Project Configuration Updater")
    print("=" * 50)
    
    current_project_id = "datavalidator-469205"
    print(f"Current PROJECT_ID: {current_project_id}")
    
    new_project_id = input("\nEnter your Google Cloud Project ID: ").strip()
    
    if not new_project_id:
        print("❌ Project ID cannot be empty!")
        return
    
    if new_project_id == current_project_id:
        print("ℹ️  Project ID is already set to this value.")
        return
    
    confirm = input(f"\nUpdate PROJECT_ID from '{current_project_id}' to '{new_project_id}'? (y/N): ")
    
    if confirm.lower() in ['y', 'yes']:
        update_project_id(new_project_id)
        print("\n📝 Next steps:")
        print("1. Download client_secret.json from Google Cloud Console")
        print("2. Download firebase-service-account.json from Google Cloud Console")
        print("3. Replace the placeholder files in your project directory")
        print("4. Run: python main.py list (to test the setup)")
    else:
        print("❌ Update cancelled.")

if __name__ == "__main__":
    main()
