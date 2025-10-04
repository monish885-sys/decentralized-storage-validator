"""
Enhanced version of the main script with better error handling and logging
"""

import argparse
import sys
from pathlib import Path
from google.cloud import firestore
from config import *
from utils import *

# Import the original functions
from main import get_drive_service, upload_and_hash, verify_and_match, list_files, delete_file

def main():
    """
    Enhanced main function with better error handling and logging
    """
    logger = setup_logging(LOG_LEVEL)
    
    try:
        parser = argparse.ArgumentParser(
            description="A Decentralized Cloud Storage Validator MVP.",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python enhanced_main.py upload document.pdf
  python enhanced_main.py verify document.pdf
  python enhanced_main.py list
  python enhanced_main.py delete document.pdf
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', required=True, help='Available commands')

        # Upload command
        upload_parser = subparsers.add_parser('upload', help='Upload a file to Google Drive and store its hash.')
        upload_parser.add_argument('file_path', type=str, help='The path to the file on your local machine.')
        upload_parser.add_argument('--description', type=str, help='Optional description for the file.')

        # Verify command
        verify_parser = subparsers.add_parser('verify', help='Verify the integrity of a file stored in Google Drive.')
        verify_parser.add_argument('file_name', type=str, help='The name of the file to verify (e.g., my_document.pdf).')

        # List command
        list_parser = subparsers.add_parser('list', help='List all files stored in the system.')
        list_parser.add_argument('--detailed', action='store_true', help='Show detailed information for each file.')

        # Delete command
        delete_parser = subparsers.add_parser('delete', help='Delete a file from both Google Drive and Firestore.')
        delete_parser.add_argument('file_name', type=str, help='The name of the file to delete.')
        delete_parser.add_argument('--force', action='store_true', help='Force deletion without confirmation.')

        args = parser.parse_args()

        # Validate configuration
        if not CLIENT_SECRET_FILE.exists():
            logger.error(f"Client secret file not found: {CLIENT_SECRET_FILE}")
            logger.error("Please download client_secret.json from Google Cloud Console")
            sys.exit(1)

        if not SERVICE_ACCOUNT_FILE.exists():
            logger.error(f"Service account file not found: {SERVICE_ACCOUNT_FILE}")
            logger.error("Please download firebase-service-account.json from Google Cloud Console")
            sys.exit(1)

        # Execute commands
        if args.command == 'upload':
            if not validate_file_path(args.file_path):
                logger.error(f"Invalid file path: {args.file_path}")
                sys.exit(1)
            
            file_size = Path(args.file_path).stat().st_size
            if file_size > MAX_FILE_SIZE:
                logger.error(f"File too large: {format_file_size(file_size)} (max: {format_file_size(MAX_FILE_SIZE)})")
                sys.exit(1)
            
            logger.info(f"Uploading file: {args.file_path}")
            upload_and_hash(args.file_path)
            
        elif args.command == 'verify':
            logger.info(f"Verifying file: {args.file_name}")
            verify_and_match(args.file_name)
            
        elif args.command == 'list':
            logger.info("Listing all files...")
            list_files()
            
        elif args.command == 'delete':
            if not args.force:
                response = input(f"Are you sure you want to delete '{args.file_name}'? (y/N): ")
                if response.lower() != 'y':
                    logger.info("Deletion cancelled.")
                    sys.exit(0)
            
            logger.info(f"Deleting file: {args.file_name}")
            delete_file(args.file_name)

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
