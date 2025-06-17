from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings
from .logger import logger  

engine = create_engine(settings.DATABASE_URL)  # Creates a SQLAlchemy engine connected to PostgreSQL
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)  # Creates a factory to generate database sessions
Base = declarative_base()  # Base class that all SQLAlchemy models will inherit from

def get_db():
    logger.debug("Creating new database session.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        logger.debug("Database session closed.")