"""Logging setup: rotating file log so terminal output stays clean."""
import logging
from logging.handlers import RotatingFileHandler

from fitness_tracker import config

_LOGGER_NAME = "fitness_tracker"


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure the app logger (idempotent). Falls back silently if the
    log directory is not writable, so logging never crashes the app."""
    logger = logging.getLogger(_LOGGER_NAME)
    if logger.handlers:
        return logger
    logger.setLevel(level)
    try:
        path = config.get_log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        handler = RotatingFileHandler(path, maxBytes=500_000, backupCount=2, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
        logger.addHandler(handler)
    except OSError:
        logger.addHandler(logging.NullHandler())
    return logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"{_LOGGER_NAME}.{name}")
