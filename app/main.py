from fastapi import FastAPI
from app.config import settings
from app.database import engine, Base
from app.api.endpoints import router as api_router


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME)

    # MVP: автосоздание таблиц (позже можно Alembic)
    Base.metadata.create_all(bind=engine)

    app.include_router(api_router, prefix=settings.API_PREFIX)
    return app


app = create_app()
