import logging
from logging.handlers import RotatingFileHandler
from app.config import settings, BASE_DIR

DEFAULT_LOG_FOLDER = BASE_DIR / 'logs'
LOG_FOLDER = settings.LOG_FOLDER or DEFAULT_LOG_FOLDER
LOG_FILE = LOG_FOLDER / 'aibot.log'

def setup_logging():
    root = logging.getLogger()
    if root.handlers:
        return

    LOG_FOLDER.mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8"
    )

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(settings.LOG_LEVEL)
    root.addHandler(handler)
