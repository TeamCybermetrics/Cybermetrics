import logging
import sys

def setup_logger(name: str) -> logging.Logger:
    """Set up logger with consistent formatting"""
    logger = logging.getLogger(name)
    # Avoid adding multiple handlers if logger already configured
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    
    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    return logger


def get_logger(name: str) -> logging.Logger:
    """Backwards-compatible alias used across the codebase"""
    return setup_logger(name)

