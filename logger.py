import logging
import os
import json
from logging.handlers import RotatingFileHandler

def setup_logger(name, config_path="config.json"):
    """Setup logger with rotating file handler"""

    # Check if running in Vercel (serverless environment)
    is_vercel = os.environ.get('VERCEL') == '1' or os.environ.get('AWS_LAMBDA_FUNCTION_NAME')

    # Load config
    try:
        config_file = os.environ.get('CONFIG_FILE', config_path)
        with open(config_file, 'r') as f:
            config = json.load(f)
        log_config = config.get('logging', {})
    except:
        log_config = {
            "level": "INFO",
            "max_file_size": "100KB",
            "max_files": 10,
            "log_file": "/tmp/browser_tracking.log" if is_vercel else "browser_tracking.log"
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
    
    # File handler with rotation (only if not in serverless environment)
    if not is_vercel:
        log_file = log_config.get('log_file', 'browser_tracking.log')
        max_files = log_config.get('max_files', 10)

        try:
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_size,
                backupCount=max_files
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except (OSError, PermissionError):
            # Fallback to console only if file logging fails
            pass
    
    # Console handler for debugging
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger
