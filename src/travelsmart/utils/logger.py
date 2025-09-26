"""Logging utilities for TravelSmart."""

import sys
from loguru import logger
from ..config import settings


def setup_logging():
    """Setup logging configuration."""
    
    # Remove default logger
    logger.remove()
    
    # Add console logging with custom format
    logger.add(
        sys.stdout,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        colorize=True
    )
    
    # Add file logging
    logger.add(
        "logs/travelsmart.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="1 MB",
        retention="7 days",
        compression="zip"
    )
    
    # Add error file logging
    logger.add(
        "logs/errors.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="1 MB",
        retention="30 days"
    )
    
    logger.info("Logging setup complete")


def get_logger(name: str):
    """Get logger instance for specific module."""
    return logger.bind(name=name)
