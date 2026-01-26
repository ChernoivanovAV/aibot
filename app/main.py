import logging

from fastapi import FastAPI

from app.api.endpoints import router as api_router
from app.config import settings
from app.database import Base, engine
from app.logging_config import setup_logging


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    setup_logging()
    log = logging.getLogger(__name__)

    app = FastAPI(title=settings.APP_NAME)
    log.info("Application created")

    # MVP: автосоздание таблиц (позже можно Alembic)
    Base.metadata.create_all(bind=engine)

    app.include_router(api_router, prefix=settings.API_PREFIX)
    return app


app = create_app()
