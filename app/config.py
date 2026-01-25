from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import logging

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", env_file_encoding="utf-8")

    APP_NAME: str = "aibot"
    API_PREFIX: str = "/api/v1"

    PROXY_DEBUG: str | None = None
    DATABASE_URL: str | None = None
    LOG_FOLDER: str | None = None
    LOG_LEVEL: int = logging.INFO

    REDIS_URL: str = "redis://localhost:6379/0"
    POLL_INTERVAL_MINUTES: int = 30

    OPENAI_BASE_URL: str | None = None
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    TG_API_ID: int | None = None
    TG_API_HASH: str | None = None
    TG_SESSION: str | None = str(BASE_DIR / 'tg.session')
    TG_TARGET_CHANNEL: str | None = None
    TG_BOT_TOKEN: str | None = None
    TG_BOT_SESSION: str | None = str(BASE_DIR / 'tg.bot.session')


settings = Settings()
