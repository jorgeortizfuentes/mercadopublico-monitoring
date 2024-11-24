from typing import Optional, Any
from datetime import datetime
import unicodedata

def remove_accents(text: str) -> str:
    """
    Remove accents from text
    
    Args:
        text (str): Text to process
        
    Returns:
        str: Text without accents
    """
    if not text:
        return ""
    
    try:
        # Normalize to decomposed form (separate char and accent)
        nfkd_form = unicodedata.normalize('NFKD', str(text))
        # Remove accents (non-spacing marks)
        return "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    except Exception:
        return text

def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse date string to datetime object"""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except (ValueError, TypeError):
        return None

def safe_bool(value: Any) -> Optional[bool]:
    """Safely convert value to boolean"""
    if value is None:
        return None
    try:
        return str(value).lower() in ('1', 'true', 'yes', 'si')
    except (ValueError, AttributeError):
        return None

def safe_int(value: Any) -> Optional[int]:
    """Safely convert value to integer"""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

def safe_float(value: Any) -> Optional[float]:
    """Safely convert value to float"""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None