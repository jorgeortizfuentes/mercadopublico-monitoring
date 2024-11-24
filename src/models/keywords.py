from sqlalchemy import Column, Integer, String, Enum as SQLAlchemyEnum
from src.database.base import Base
import enum

class KeywordType(enum.Enum):
    """Type of keyword for filtering"""
    INCLUDE = "include"
    EXCLUDE = "exclude"

class Keyword(Base):
    """Model for storing search keywords"""
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, autoincrement=True, 
                doc="Unique identifier for the keyword")
    keyword = Column(String, nullable=False, unique=True, 
                    doc="The keyword text to search for")
    type = Column(SQLAlchemyEnum(KeywordType), nullable=False, default=KeywordType.INCLUDE,
                 doc="Type of keyword (include/exclude)")

    def __repr__(self):
        """String representation of the keyword"""
        return f"<Keyword(id={self.id}, keyword='{self.keyword}', type={self.type.value})>"
