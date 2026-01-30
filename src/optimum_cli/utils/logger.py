"""Logging configuration using Loguru."""

import sys
from pathlib import Path
from loguru import logger

from optimum_cli.core.config import get_settings


def setup_logging():
    """Configure loguru logger."""
    settings = get_settings()
    
    # Remove default handler
    logger.remove()
    
    # Console handler
    if settings.logging.console_enabled:
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=settings.logging.level,
            colorize=True,
        )
    
    # File handler
    if settings.logging.file_enabled:
        log_path = Path(settings.logging.file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            settings.logging.file_path,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=settings.logging.level,
            rotation=settings.logging.file_rotation,
            retention=settings.logging.file_retention,
            compression="zip",
        )
    
    return logger


# Global logger instance
log = setup_logging()


def get_logger():
    """Get global logger instance."""
    return log
