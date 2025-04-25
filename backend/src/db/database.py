"""
Module for database connection and session management.
"""

from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool

from ..utils.config import app_settings

# Global engine instance for connection reuse
_engine: Engine | None = None
Base: Any = declarative_base()


def get_engine() -> Engine:
    """
    Create or return existing database engine with optimized pooling configuration.

    Returns:
        Engine: SQLAlchemy engine instance
    """
    global _engine
    if _engine is None:
        _engine = create_engine(
            app_settings.DB_URL,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # Connection health check
            pool_recycle=3600,  # Prevent stale connections
            connect_args={"connect_timeout": 5},
        )
    return _engine


def setup_database() -> None:
    """Initialize database connection."""
    get_engine()


def cleanup_database() -> None:
    """Clean up database connections."""
    global _engine
    if _engine:
        _engine.dispose()
        _engine = None


SessionLocal = sessionmaker(autocommit=False, autoflush=False)


def get_db():
    """
    Database session dependency for FastAPI.

    Yields:
        Session: SQLAlchemy session object
    """
    engine = get_engine()
    SessionLocal.configure(bind=engine)
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """Initialize database for application startup."""
    setup_database()


def cleanup_db() -> None:
    """Cleanup database connections for application shutdown."""
    cleanup_database()
