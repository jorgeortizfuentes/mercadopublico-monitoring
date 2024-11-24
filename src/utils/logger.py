import logging
from src.config.settings import LOG_LEVEL, LOG_FORMAT

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    formatter = logging.Formatter(LOG_FORMAT)
    
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)

    return logger
