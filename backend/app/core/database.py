"""
Database configuration for VerificAI Backend - Demo Mode (Supabase compatible)
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator
import logging

from app.core.config import settings
from app.models.base import Base

# Import all models to ensure they are registered with SQLAlchemy
from app.models.user import User
from app.models.prompt import Prompt, PromptConfiguration
from app.models.analysis import Analysis, AnalysisResult
from app.models.uploaded_file import UploadedFile
from app.models.file_path import FilePath
from app.models.code_entry import CodeEntry

logger = logging.getLogger(__name__)

# Fix Supabase/Render DATABASE_URL format (postgres:// → postgresql://)
database_url = settings.DATABASE_URL
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# SQLAlchemy engine - small pool for free-tier cloud hosting
engine = create_engine(
    database_url,
    poolclass=QueuePool,
    pool_size=3,           # Supabase free tier has limited connections
    max_overflow=2,
    pool_timeout=30,
    pool_recycle=1800,     # Recycle connections every 30 minutes
    pool_pre_ping=True,    # Verify connection before use
    echo=settings.DEBUG,
    connect_args={"sslmode": "require"} if "supabase" in database_url else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
Base.metadata.naming_convention = convention


def get_db() -> Generator[Session, None, None]:
    """Database dependency for FastAPI routes"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    """Create database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def drop_tables():
    """Drop database tables (use with caution)"""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise


class DatabaseManager:
    """Database connection manager"""

    def __init__(self):
        self.engine = engine
        self.session_factory = SessionLocal

    def get_session(self) -> Session:
        """Get a new database session"""
        return self.session_factory()

    def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager()
