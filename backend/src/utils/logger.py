"""
Logger configuration for the application.
"""

import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from .config import app_settings


def configure_logger(name: str) -> logging.Logger:
    """
    Creates and configures a logger with appropriate handlers based on environment.
    """
    log_level = app_settings.LOG_LEVEL
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger_format = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    if not logger.hasHandlers():
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logger_format)

        if app_settings.CURRENT_ENV in ("test", "production"):
            console_handler.setLevel(log_level)
        else:
            # Create logs directory if it doesn't exist
            logs_dir = Path(os.getcwd()) / "logs"
            logs_dir.mkdir(exist_ok=True)

            log_file = logs_dir / f"{datetime.now().strftime('%d-%m-%Y')}.log"
            file_handler = TimedRotatingFileHandler(
                log_file, when="midnight", interval=1, backupCount=7
            )
            console_handler.setLevel(log_level)
            file_handler.setFormatter(logger_format)
            file_handler.setLevel(logging.WARNING)
            logger.addHandler(file_handler)

        logger.addHandler(console_handler)

    return logger


# Create a default logger for the application
app_logger = configure_logger("pulse_check_service")

# Reduce verbosity of third-party loggers
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
