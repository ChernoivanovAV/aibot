from celery import Celery
from app.config import settings

celery_app = Celery(
    "aibot",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.timezone = "UTC"
celery_app.conf.task_routes = {"app.tasks.*": {"queue": "default"}}

celery_app.conf.beat_schedule = {
    "run-pipeline-every-n-minutes": {
        "task": "app.tasks.run_pipeline_task",
        "schedule": settings.POLL_INTERVAL_MINUTES * 60,
    }
}

celery_app.autodiscover_tasks(["app"])
