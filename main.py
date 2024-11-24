from src.api.public_market_api import PublicMarketAPI
from src.database.base import get_db, init_db
from src.database.repository import TenderRepository, KeywordRepository
from src.models.keywords import KeywordType
from src.utils.logger import setup_logger
from typing import List, Tuple


def get_keywords(repo: KeywordRepository) -> Tuple[List[str], List[str]]:
    """
    Get include and exclude keywords from the database
    
    Args:
        repo: KeywordRepository instance
        
    Returns:
        Tuple[List[str], List[str]]: Lists of include and exclude keywords
    """
    include_keywords = [k.keyword for k in repo.get_keywords_by_type(KeywordType.INCLUDE)]
    exclude_keywords = [k.keyword for k in repo.get_keywords_by_type(KeywordType.EXCLUDE)]
    return include_keywords, exclude_keywords


def initialize_default_keywords(repo: KeywordRepository) -> None:
    """
    Initialize default keywords if the keywords table is empty
    
    Args:
        repo: KeywordRepository instance
    """
    if not repo.get_all_keywords():
        # Default include keywords
        default_includes = [
            "software", "analisis", "datos", "inteligencia artificial", "web",
            "aplicación", "plataforma", "digital",
            "tecnología", "informática", "computación", "desarrollo"
        ]
        
        # Default exclude keywords
        default_excludes = [
            "limpieza", "licencia", "suscripción", "mantención", "aseo", "arriendo",
        ]
        
        # Add include keywords
        for keyword in default_includes:
            repo.create_keyword(keyword, KeywordType.INCLUDE)
            
        # Add exclude keywords
        for keyword in default_excludes:
            repo.create_keyword(keyword, KeywordType.EXCLUDE)


def main():
    # Setup logging
    logger = setup_logger(__name__)
    
    try:
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

        # Get keywords from database
        include_keywords, exclude_keywords = get_keywords(keyword_repo)
        
        logger.info(f"Using include keywords: {include_keywords}")
        logger.info(f"Using exclude keywords: {exclude_keywords}")

        # Search tenders
        tenders = api.search_tenders(
            include_keywords=include_keywords,
            exclude_keywords=exclude_keywords,
            days_back=2
        )

        # Save to database
        new_tenders = 0
        updated_tenders = 0
        unchanged_tenders = 0
        
        for tender in tenders:
            try:
                existing_tender = tender_repo.get_tender_by_code(tender.code)
                
                if existing_tender:
                    # Update existing tender
                    updated_tender = tender_repo.update_tender(tender)
                    if updated_tender.updated_at > existing_tender.updated_at:
                        updated_tenders += 1
                    else:
                        unchanged_tenders += 1
                else:
                    # Create new tender
                    tender_repo.create_tender(tender)
                    new_tenders += 1
                    
            except Exception as e:
                logger.error(f"Error processing tender {tender.code}: {str(e)}")
                continue

            logger.info(f"Successfully processed {len(tenders)} tenders")
            logger.info(f"New tenders: {new_tenders}")
            logger.info(f"Updated tenders: {updated_tenders}")
            logger.info(f"Unchanged tenders: {unchanged_tenders}")

    except Exception as e:
        logger.error(f"Execution error: {str(e)}")
        raise
    finally:
        logger.info("Process completed")


if __name__ == "__main__":
    main()
