# app/api/schemas.py
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

class KeywordUpdate(BaseModel):
    """
    Schema for updating keywords
    
    Attributes:
        include_keywords: List of keywords to include in searches
        exclude_keywords: List of keywords to exclude from searches
    """
    include_keywords: List[str] = Field(
        default=[],
        description="List of keywords to include in searches"
    )
    exclude_keywords: List[str] = Field(
        default=[],
        description="List of keywords to exclude from searches"
    )

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "include_keywords": ["software", "desarrollo", "tecnología"],
                "exclude_keywords": ["limpieza", "mantenimiento"]
            }
        }
    )

class ExecuteRequest(BaseModel):
    """
    Schema for execution request
    
    Attributes:
        days: Number of days to look back for tenders
        status: Status of tenders to search
    """
    days: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Number of days to look back for tenders"
    )
    status: str = Field(
        default="publicada",
        description="Status of tenders to search"
    )

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "days": 30,
                "status": "publicada"
            }
        }
    )

class TenderResponse(BaseModel):
    """
    Schema for tender response
    
    Attributes:
        code: Unique identifier for the tender
        name: Name or title of the tender
        status: Current status of the tender
        organization: Organization that created the tender
        closing_date: Deadline for tender submissions
        estimated_amount: Estimated budget for the tender
        tender_type: Type of tender based on amount
    """
    code: str = Field(..., description="Unique identifier for the tender")
    name: str = Field(..., description="Name or title of the tender")
    status: str = Field(..., description="Current status of the tender")
    organization: Optional[str] = Field(None, description="Organization that created the tender")
    closing_date: Optional[datetime] = Field(None, description="Deadline for tender submissions")
    estimated_amount: Optional[float] = Field(None, description="Estimated budget for the tender")
    tender_type: Optional[str] = Field(None, description="Type of tender based on amount")

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    )


class KeywordBase(BaseModel):
    """
    Base schema for keywords
    
    Attributes:
        keyword: The keyword text
        type: Type of keyword (include/exclude)
    """
    keyword: str = Field(..., description="The keyword text")
    type: str = Field(..., description="Type of keyword (include/exclude)")

class KeywordCreate(KeywordBase):
    """Schema for creating a new keyword"""
    pass

class KeywordResponse(KeywordBase):
    """
    Schema for keyword response
    
    Attributes:
        id: Unique identifier for the keyword
    """
    id: int = Field(..., description="Unique identifier for the keyword")

    model_config = ConfigDict(
        from_attributes=True
    )
