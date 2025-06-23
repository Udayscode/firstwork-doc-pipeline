import logging
from logging.handlers import RotatingFileHandler

def configure_logging(verbose: bool = False):
    """Configure logging for the application"""
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Clear any existing handlers
    for handler in logging.getLogger().handlers[:]:
        logging.getLogger().removeHandler(handler)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler('document_processor.log', maxBytes=10_000_000, backupCount=5),
            logging.StreamHandler()
        ]
    )