# init_app.py
from src.database.base import get_db, init_db
from src.database.repository import KeywordRepository
from src.utils.logger import setup_logger

def initialize_application():
    """Initialize database and required components"""
    logger = setup_logger(__name__)
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        init_db()

        # Initialize API
        logger.info("Initializing API client...")

        # Get database session
        db = next(get_db())
        keyword_repo = KeywordRepository(db)

        # Initialize default keywords if needed
        logger.info("Initializing default keywords...")
        keyword_repo.initialize_default_keywords()

        logger.info("Application initialization completed successfully")
        return True

    except Exception as e:
        logger.error(f"Error during application initialization: {str(e)}")
        raise

if __name__ == "__main__":
    initialize_application()
