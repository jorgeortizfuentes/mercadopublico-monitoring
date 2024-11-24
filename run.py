import uvicorn

from src.api.public_market_api import PublicMarketAPI
from src.database.base import get_db, init_db
from src.database.repository import KeywordRepository, TenderRepository
from src.database.repository import KeywordRepository, TenderRepository
from src.utils.logger import setup_logger

if __name__ == "__main__":
    logger = setup_logger(__name__)

    # Initialize database
    logger.info("Initializing database...")
    init_db()

    # Initialize API
    logger.info("Initializing API client...")
    api = PublicMarketAPI()

    # Get database session
    db = next(get_db())
    tender_repo = TenderRepository(db)
    keyword_repo = KeywordRepository(db)

    # Initialize default keywords if needed
    keyword_repo.initialize_default_keywords()

    uvicorn.run("app.main:app", host="0.0.0.0", port=5353, reload=True)
