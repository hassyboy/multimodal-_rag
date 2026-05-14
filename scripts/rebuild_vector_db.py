import os
import shutil
import sys

# Ensure the app module is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

def rebuild_database():
    """
    Deletes the existing ChromaDB storage directory to start fresh.
    """
    logger.info(f"Preparing to rebuild ChromaDB at path: {settings.CHROMA_DB_PATH}")
    
    if os.path.exists(settings.CHROMA_DB_PATH):
        try:
            shutil.rmtree(settings.CHROMA_DB_PATH)
            logger.info(f"Successfully deleted existing database at {settings.CHROMA_DB_PATH}")
        except Exception as e:
            logger.error(f"Failed to delete existing database: {e}")
            sys.exit(1)
    else:
        logger.info("No existing database found. Nothing to delete.")
        
    logger.info("Database rebuild prep complete. You can now run the ingestion script.")

if __name__ == "__main__":
    # Prompt for confirmation to prevent accidental deletion
    print(f"WARNING: This will delete all data in {settings.CHROMA_DB_PATH}.")
    confirm = input("Are you sure you want to proceed? (yes/no): ")
    if confirm.lower() == 'yes':
        rebuild_database()
    else:
        print("Operation cancelled.")
