import logging
import logging.handlers
import os
from ..config import Config


def setup_logger(name='app', log_file=None, level=None):

#Logger beállítása file és console handler-rel

    logger = logging.getLogger(name)
    
    # Ne állítsuk be többször
    if logger.handlers:
        return logger
    
    # Log level beállítása
    if level is None:
        level = getattr(logging, Config.LOG_LEVEL, logging.INFO)
    logger.setLevel(level)
    
    # Formatter létrehozása
    formatter = logging.Formatter(
        Config.LOG_FORMAT,
        datefmt=Config.LOG_DATE_FORMAT
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (rotating)
    if log_file is None:
        log_file = Config.LOG_FILE
    
    # Logs könyvtár létrehozása ha nem létezik
    log_dir = os.path.dirname(log_file)
    os.makedirs(log_dir, exist_ok=True)
    
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=Config.LOG_MAX_BYTES,
        backupCount=Config.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Error log file handler (csak ERROR és CRITICAL szintű üzenetek)
    error_handler = logging.handlers.RotatingFileHandler(
        Config.LOG_ERROR_FILE,
        maxBytes=Config.LOG_MAX_BYTES,
        backupCount=Config.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    return logger


def get_logger(name=None):

#Logger példány lekérése

    if name is None:
        name = 'app'
    return logging.getLogger(name)

