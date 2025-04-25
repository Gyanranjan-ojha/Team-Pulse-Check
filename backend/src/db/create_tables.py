"""
Script for creating database tables.
"""

from ..utils.logger import app_logger
from .create_db import create_database
from .database import get_engine
from .models import Base


def create_tables() -> None:
    """
    Create database tables based on SQLAlchemy models.
    """
    try:
        # First ensure the database exists
        create_database()

        # Create tables
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        app_logger.info("Database tables created successfully")

    except Exception as e:
        app_logger.error(f"Error creating tables: {str(e)}")
        raise Exception(f"Error creating tables: {str(e)}") from e


if __name__ == "__main__":
    create_tables()
