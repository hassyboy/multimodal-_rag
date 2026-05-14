import logging
import sys
from app.core.config import settings

def get_logger(name: str) -> logging.Logger:
    """
    Configure and return a centralized logger.
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(settings.LOG_LEVEL.upper())
        
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        
    return logger
