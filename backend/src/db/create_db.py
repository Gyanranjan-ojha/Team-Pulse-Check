"""
Script for creating the database if it doesn't exist.
"""

# mypy: ignore-errors
from typing import Any

import pymysql

from ..utils.config import app_settings
from ..utils.logger import app_logger


def create_database() -> None:
    """
    Creates the database if it doesn't exist based on the configuration.
    """
    try:
        # Extract database connection parameters
        db_params: dict[str, Any] = {
            "host": app_settings.MYSQL_HOST,
            "user": app_settings.MYSQL_USER,
            "password": app_settings.MYSQL_ROOT_PASSWORD.get_secret_value(),
            "port": app_settings.MYSQL_PORT,
        }

        # Connect to MySQL server without specifying a database
        conn = pymysql.connect(**db_params)
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall()]

        MYSQL_DB_NAME = app_settings.MYSQL_DB_NAME

        if MYSQL_DB_NAME not in databases:
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB_NAME}")
            app_logger.info(f"Database '{MYSQL_DB_NAME}' created successfully")
        else:
            app_logger.warning(f"Database '{MYSQL_DB_NAME}' already exists")

        conn.close()
    except Exception as e:
        app_logger.error(f"Error creating database: {str(e)}")
        raise Exception(f"Error creating database: {str(e)}") from e
