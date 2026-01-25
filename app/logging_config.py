import logging
from logging.handlers import RotatingFileHandler
from app.config import settings, BASE_DIR

DEFAULT_LOG_FOLDER = BASE_DIR / 'logs'
LOG_FOLDER = settings.LOG_FOLDER or DEFAULT_LOG_FOLDER
LOG_FILE = LOG_FOLDER / 'aibot.log'

def setup_logging():
    root = logging.getLogger()
    existing_file_handler = any(
        isinstance(handler, RotatingFileHandler)
        and getattr(handler, "baseFilename", None) == str(LOG_FILE)
        for handler in root.handlers
    )
    existing_stream_handler = any(
        isinstance(handler, logging.StreamHandler)
        and not isinstance(handler, RotatingFileHandler)
        for handler in root.handlers
    )
    if existing_file_handler:
        return

    LOG_FOLDER.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8"
    )
    stream_handler = None if existing_stream_handler else logging.StreamHandler()

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    file_handler.setFormatter(formatter)
    if stream_handler:
        stream_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(settings.LOG_LEVEL)
    root.addHandler(file_handler)
    if stream_handler:
        root.addHandler(stream_handler)
