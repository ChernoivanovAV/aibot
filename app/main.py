from fastapi import FastAPI
from app.config import settings
from app.database import engine, Base
from app.api.endpoints import router as api_router
from app.logging_config import setup_logging
import logging


def create_app() -> FastAPI:
    setup_logging()
    log = logging.getLogger(__name__)

    app = FastAPI(title=settings.APP_NAME)
    log.info(f"Application created")

    # MVP: автосоздание таблиц (позже можно Alembic)
    Base.metadata.create_all(bind=engine)

    app.include_router(api_router, prefix=settings.API_PREFIX)
    return app


app = create_app()
