# app/api/routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from src.database.base import get_db
from src.database.repository import TenderRepository, KeywordRepository, KeywordType
from .schemas import TenderResponse, StatisticsResponse, KeywordResponse, KeywordCreate, ExecuteRequest
from src.api.public_market_api import PublicMarketAPI
from fastapi import BackgroundTasks

# Import logger from src.utils 
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

@router.get("/tenders", response_model=List[TenderResponse])
async def get_tenders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Get tenders with optional filtering
    """
    try:
        repo = TenderRepository(db)
        if any([search, status, start_date, end_date]):
            tenders = repo.get_tenders_with_filters(
                skip=skip,
                limit=limit,
                search=search,
                status=status,
                start_date=start_date,
                end_date=end_date
            )
        else:
            tenders = repo.get_all_tenders()
            
        # Convertir los objetos SQLAlchemy a diccionarios y luego a modelos Pydantic
        return [TenderResponse.model_validate(tender) for tender in tenders]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(db: Session = Depends(get_db)):
    """
    Get tender statistics
    """
    try:
        repo = TenderRepository(db)
        return repo.get_tender_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/keywords", response_model=List[KeywordResponse])
async def get_keywords(db: Session = Depends(get_db)):
    """Get all keywords"""
    try:
        repo = KeywordRepository(db)
        keywords = repo.get_all_keywords()
        return [KeywordResponse.model_validate(k) for k in keywords]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/keywords", response_model=KeywordResponse)
async def create_keyword(
    keyword: KeywordCreate,
    db: Session = Depends(get_db)
):
    """Create a new keyword"""
    try:
        repo = KeywordRepository(db)
        new_keyword = repo.create_keyword(keyword.keyword, KeywordType(keyword.type))
        return KeywordResponse.model_validate(new_keyword)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/keywords/{keyword_id}")
async def delete_keyword(
    keyword_id: int,
    db: Session = Depends(get_db)
):
    """Delete a keyword"""
    try:
        repo = KeywordRepository(db)
        success = repo.delete_keyword(keyword_id)
        if not success:
            raise HTTPException(status_code=404, detail="Keyword not found")
        return {"message": "Keyword deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/keywords/{keyword_id}", response_model=KeywordResponse)
async def update_keyword(
    keyword_id: int,
    keyword: KeywordCreate,
    db: Session = Depends(get_db)
):
    """Update a keyword"""
    try:
        repo = KeywordRepository(db)
        updated_keyword = repo.update_keyword(
            keyword_id, 
            new_keyword=keyword.keyword, 
            new_type=KeywordType(keyword.type)
        )
        if not updated_keyword:
            raise HTTPException(status_code=404, detail="Keyword not found")
        return KeywordResponse.model_validate(updated_keyword)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute")
async def execute_search(
    request: ExecuteRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Execute tender search with specified parameters"""
    try:
        # Initialize repositories
        tender_repo = TenderRepository(db)
        keyword_repo = KeywordRepository(db)
        
        # Get keywords
        include_keywords = [k.keyword for k in keyword_repo.get_keywords_by_type(KeywordType.INCLUDE)]
        exclude_keywords = [k.keyword for k in keyword_repo.get_keywords_by_type(KeywordType.EXCLUDE)]
        
        # Initialize API
        api = PublicMarketAPI()
        
        # Add search task to background tasks
        background_tasks.add_task(
            process_search,
            api,
            include_keywords,
            exclude_keywords,
            request.days,
            tender_repo
        )
        
        return {
            "message": "Search started successfully",
            "status": "processing"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error starting search: {str(e)}"
        )

async def process_search(
    api: PublicMarketAPI,
    include_keywords: List[str],
    exclude_keywords: List[str],
    days: int,
    tender_repo: TenderRepository
):
    """Process search in background"""
    try:
        tenders = api.search_tenders(
            include_keywords=include_keywords,
            exclude_keywords=exclude_keywords,
            days_back=days
        )
        
        new_count = 0
        updated_count = 0
        
        for tender in tenders:
            existing = tender_repo.get_tender_by_code(tender.code)
            if existing:
                tender_repo.update_tender(tender)
                updated_count += 1
            else:
                tender_repo.create_tender(tender)
                new_count += 1
                
    except Exception as e:
        logger.error(f"Error in background search: {str(e)}")
