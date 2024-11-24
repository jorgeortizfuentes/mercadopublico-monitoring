# src/database/base.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import make_url
from src.config.settings import DATABASE_URL
from src.utils.logger import setup_logger
import os

logger = setup_logger(__name__)

def get_engine_config():
    """
    Configure database engine based on DATABASE_URL
    
    Returns:
        tuple: (engine, kwargs) where engine is the SQLAlchemy engine and 
               kwargs are additional configuration parameters
    """
    url = make_url(DATABASE_URL)
    
    if url.drivername == 'postgresql':
        # PostgreSQL configuration
        return create_engine(
            DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
            echo=False
        )
    elif 'sqlite' in url.drivername:
        # SQLite configuration
        # Ensure the directory exists
        db_path = url.database
        if db_path != ':memory:':
            os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        
        return create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
            echo=False
        )
    else:
        raise ValueError(f"Unsupported database type: {url.drivername}")

try:
    # Create engine based on URL
    engine = get_engine_config()
    logger.info(f"Database engine configured for: {make_url(DATABASE_URL).drivername}")
    
    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create base class for declarative models
    Base = declarative_base()
    
except Exception as e:
    logger.error(f"Failed to configure database: {str(e)}")
    raise

def init_db():
    """Initialize the database and create all tables"""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

def get_db():
    """Database session generator"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
