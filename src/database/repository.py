from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from datetime import datetime
from src.models.tender import Tender
from src.models.keywords import Keyword, KeywordType
from src.utils.logger import setup_logger

class TenderRepository:
    def __init__(self, db: Session):
        self.db = db
        self.logger = setup_logger(__name__)

    def create_tender(self, tender: Tender) -> Tender:
        """
        Create a new tender in the database
        
        Args:
            tender (Tender): Tender object to create
            
        Returns:
            Tender: Created tender object
        """
        try:
            tender.created_at = datetime.utcnow()
            tender.updated_at = datetime.utcnow()
            
            self.logger.debug(f"Creating new tender with code: {tender.code}")
            self.db.add(tender)
            self.db.commit()
            self.db.refresh(tender)
            return tender
        except Exception as e:
            self.logger.error(f"Error creating tender {tender.code}: {str(e)}")
            self.db.rollback()
            raise

    def update_tender(self, new_tender: Tender) -> Tender:
        """
        Update an existing tender if there are changes
        
        Args:
            new_tender (Tender): Tender object with updated data
            
        Returns:
            Tender: Updated tender object
        """
        try:
            existing_tender = self.get_tender_by_code(new_tender.code)
            if not existing_tender:
                return self.create_tender(new_tender)

            # Compare relevant fields to check if update is needed
            fields_to_compare = [
                'name', 'description', 'status', 'status_code', 'estimated_amount',
                'closing_date', 'award_date', 'number_of_bidders', 'items',
                'awarded_suppliers'
            ]

            needs_update = False
            for field in fields_to_compare:
                old_value = getattr(existing_tender, field)
                new_value = getattr(new_tender, field)
                if old_value != new_value:
                    needs_update = True
                    self.logger.debug(f"Field {field} changed from {old_value} to {new_value}")
                    setattr(existing_tender, field, new_value)

            if needs_update:
                existing_tender.updated_at = datetime.utcnow()
                self.logger.info(f"Updating tender {existing_tender.code}")
                self.db.commit()
                self.db.refresh(existing_tender)
            else:
                self.logger.debug(f"No updates needed for tender {existing_tender.code}")

            return existing_tender

        except Exception as e:
            self.logger.error(f"Error updating tender {new_tender.code}: {str(e)}")
            self.db.rollback()
            raise

    def get_tender_by_code(self, code: str) -> Optional[Tender]:
        """
        Get a tender by its code
        
        Args:
            code (str): Tender code to search for
            
        Returns:
            Optional[Tender]: Found tender or None
        """
        return self.db.query(Tender).filter(Tender.code == code).first()

    def get_tenders_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Tender]:
        """
        Get all tenders within a date range
        
        Args:
            start_date (datetime): Start date of the range
            end_date (datetime): End date of the range
            
        Returns:
            List[Tender]: List of tenders within the date range
        """
        return self.db.query(Tender).filter(
            Tender.creation_date.between(start_date, end_date)
        ).all()

    def delete_tender(self, tender: Tender) -> None:
        """
        Delete a tender from the database
        
        Args:
            tender (Tender): Tender object to delete
        """
        self.db.delete(tender)
        self.db.commit()

    def get_all_tenders(self) -> List[Tender]:
        """
        Get all tenders from the database
        
        Returns:
            List[Tender]: List of all tenders
        """
        try:
            return self.db.query(Tender).order_by(Tender.created_at.desc()).all()
        except Exception as e:
            self.logger.error(f"Error getting all tenders: {str(e)}")
            raise

    def get_tenders_with_filters(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Tender]:
        """
        Get tenders with filters
        
        Args:
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            search (str, optional): Search term for name or description
            status (str, optional): Filter by status
            start_date (datetime, optional): Filter by start date
            end_date (datetime, optional): Filter by end date
            
        Returns:
            List[Tender]: List of filtered tenders
        """
        try:
            query = self.db.query(Tender)

            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        Tender.name.ilike(search_term),
                        Tender.description.ilike(search_term)
                    )
                )

            if status:
                query = query.filter(Tender.status == status)

            if start_date:
                query = query.filter(Tender.creation_date >= start_date)

            if end_date:
                query = query.filter(Tender.creation_date <= end_date)

            return query.order_by(Tender.created_at.desc()).offset(skip).limit(limit).all()

        except Exception as e:
            self.logger.error(f"Error getting filtered tenders: {str(e)}")
            raise

    def get_tender_statistics(self) -> Dict:
        """
        Get statistics about tenders
        
        Returns:
            Dict: Dictionary containing various statistics
        """
        try:
            total_count = self.db.query(func.count(Tender.code)).scalar()
            total_amount = self.db.query(func.sum(Tender.estimated_amount)).scalar() or 0

            # Get counts by tender type
            type_counts = (
                self.db.query(
                    Tender.tender_type,
                    func.count(Tender.code).label('count')
                )
                .group_by(Tender.tender_type)
                .all()
            )

            # Get counts by status
            status_counts = (
                self.db.query(
                    Tender.status,
                    func.count(Tender.code).label('count')
                )
                .group_by(Tender.status)
                .all()
            )

            return {
                "total_count": total_count,
                "total_amount": float(total_amount),
                "by_type": {str(t.tender_type): t.count for t in type_counts if t.tender_type},
                "by_status": {s.status: s.count for s in status_counts if s.status}
            }

        except Exception as e:
            self.logger.error(f"Error getting tender statistics: {str(e)}")
            raise


class KeywordRepository:
    def __init__(self, db: Session):
        self.db = db
        self.logger = setup_logger(__name__)

    def create_keyword(self, keyword: str, type: KeywordType) -> Keyword:
        """
        Create a new keyword
        
        Args:
            keyword (str): Keyword text
            type (KeywordType): Type of keyword (include/exclude)
            
        Returns:
            Keyword: Created keyword object
        """
        try:
            new_keyword = Keyword(keyword=keyword, type=type)
            self.db.add(new_keyword)
            self.db.commit()
            self.db.refresh(new_keyword)
            return new_keyword
        except Exception as e:
            self.logger.error(f"Error creating keyword: {str(e)}")
            self.db.rollback()
            raise

    def get_all_keywords(self) -> List[Keyword]:
        """
        Get all keywords
        
        Returns:
            List[Keyword]: List of all keywords
        """
        return self.db.query(Keyword).all()

    def get_keywords_by_type(self, type: KeywordType) -> List[Keyword]:
        """
        Get keywords by type
        
        Args:
            type (KeywordType): Type of keywords to retrieve
            
        Returns:
            List[Keyword]: List of keywords of specified type
        """
        return self.db.query(Keyword).filter(Keyword.type == type).all()

    def delete_keyword(self, keyword_id: int) -> bool:
        """
        Delete a keyword
        
        Args:
            keyword_id (int): ID of keyword to delete
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            keyword = self.db.query(Keyword).filter(Keyword.id == keyword_id).first()
            if keyword:
                self.db.delete(keyword)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error deleting keyword: {str(e)}")
            self.db.rollback()
            return False

    def update_keyword(self, keyword_id: int, new_keyword: str = None, 
                      new_type: KeywordType = None) -> Optional[Keyword]:
        """
        Update a keyword
        
        Args:
            keyword_id (int): ID of keyword to update
            new_keyword (str, optional): New keyword text
            new_type (KeywordType, optional): New keyword type
            
        Returns:
            Optional[Keyword]: Updated keyword object or None if not found
        """
        try:
            keyword = self.db.query(Keyword).filter(Keyword.id == keyword_id).first()
            if keyword:
                if new_keyword is not None:
                    keyword.keyword = new_keyword
                if new_type is not None:
                    keyword.type = new_type
                self.db.commit()
                self.db.refresh(keyword)
                return keyword
            return None
        except Exception as e:
            self.logger.error(f"Error updating keyword: {str(e)}")
            self.db.rollback()
            return None

    def initialize_default_keywords(self) -> None:
        """
        Initialize default keywords if the keywords table is empty
        """
        if not self.get_all_keywords():
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
            
            try:
                # Add include keywords
                for keyword in default_includes:
                    self.create_keyword(keyword, KeywordType.INCLUDE)
                    
                # Add exclude keywords
                for keyword in default_excludes:
                    self.create_keyword(keyword, KeywordType.EXCLUDE)
                
                self.logger.info("Default keywords initialized successfully")
            except Exception as e:
                self.logger.error(f"Error initializing default keywords: {str(e)}")
                raise
