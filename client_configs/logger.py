import logging
import os
import json
from logging.handlers import RotatingFileHandler

def setup_logger(name, config_path="config.json"):
    """Setup logger with rotating file handler"""
    
    # Load config
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        log_config = config.get('logging', {})
    except:
        log_config = {
            "level": "INFO",
            "max_file_size": "100KB",
            "max_files": 10,
            "log_file": "browser_tracking.log"
        }
    
    # Parse max file size
    max_size_str = log_config.get('max_file_size', '100KB')
    if 'KB' in max_size_str:
        max_size = int(max_size_str.replace('KB', '')) * 1024
    elif 'MB' in max_size_str:
        max_size = int(max_size_str.replace('MB', '')) * 1024 * 1024
    else:
        max_size = 100 * 1024  # Default 100KB
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_config.get('level', 'INFO')))
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler with rotation
    log_file = log_config.get('log_file', 'browser_tracking.log')
    max_files = log_config.get('max_files', 10)
    
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=max_size, 
        backupCount=max_files
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler for debugging
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger
