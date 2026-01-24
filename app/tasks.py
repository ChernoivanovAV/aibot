from __future__ import annotations

from datetime import datetime
import logging

from celery import Celery
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.config import settings
from app.database import SessionLocal
from app.models import Source, Keyword, NewsItem, Post, PostStatus
from app.news_parser.sites import parse_site_source
from app.news_parser.telegram import parse_tg_source
from app.ai.generator import generate_telegram_post
from app.telegram.publisher import publish_to_channel
from app.logging_config import setup_logging

setup_logging()
log = logging.getLogger(__name__)

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


def _get_db() -> Session:
    return SessionLocal()


def _passes_keyword_filter(db: Session, text: str) -> bool:
    keywords = db.execute(select(Keyword)).scalars().all()
    if not keywords:
        return True
    low = text.lower()
    return any(k.word.lower() in low for k in keywords)


@celery_app.task(name="app.tasks.run_pipeline_task")
def run_pipeline_task():
    log.info("Running pipeline task")
    db = _get_db()
    try:
        sources = db.execute(select(Source).where(Source.enabled == True)).scalars().all()  # noqa: E712
        created_news_ids: list[int] = []

        for src in sources:
            try:
                if src.type.value == "site":
                    items = parse_site_source(src)
                else:
                    items = parse_tg_source(src)
            except Exception as e:
                log.exception("Parse failed for source=%s: %s", src.name, e)
                continue

            for it in items:
                full_text = f"{it.get('title','')}\n{it.get('summary','')}\n{it.get('raw_text','') or ''}"
                if not _passes_keyword_filter(db, full_text):
                    continue

                news = NewsItem(**it)
                db.add(news)
                try:
                    db.flush()  # triggers uq fingerprint
                except Exception:
                    db.rollback()
                    continue

                created_news_ids.append(news.id)

                post = Post(news_id=news.id, status=PostStatus.new)
                db.add(post)

        db.commit()

        for news_id in created_news_ids:
            generate_post_task.delay(news_id)

        return {"created_news": len(created_news_ids)}

    finally:
        db.close()


@celery_app.task(name="app.tasks.generate_post_task")
def generate_post_task(news_id: int):
    db = _get_db()
    try:
        news = db.get(NewsItem, news_id)
        if not news:
            return {"error": "news not found"}

        post = db.execute(
            select(Post).where(Post.news_id == news_id).order_by(desc(Post.id))
        ).scalars().first()

        if not post:
            post = Post(news_id=news_id, status=PostStatus.new)
            db.add(post)
            db.flush()

        text = generate_telegram_post(news)
        post.generated_text = text
        post.status = PostStatus.generated
        post.error = None
        db.commit()

        publish_post_task.delay(post.id)
        return {"post_id": post.id}

    except Exception as e:
        db.rollback()
        post = db.execute(
            select(Post).where(Post.news_id == news_id).order_by(desc(Post.id))
        ).scalars().first()
        if post:
            post.status = PostStatus.failed
            post.error = str(e)
            db.commit()
        raise
    finally:
        db.close()


@celery_app.task(name="app.tasks.publish_post_task")
def publish_post_task(post_id: int):
    db = _get_db()
    try:
        post = db.get(Post, post_id)
        if not post:
            return {"error": "post not found"}

        if post.status == PostStatus.published:
            return {"skipped": True}

        if not post.generated_text:
            return {"error": "post has no generated_text"}

        publish_to_channel(post.generated_text)

        post.status = PostStatus.published
        post.published_at = datetime.utcnow()
        post.error = None
        db.commit()
        return {"published": True}

    except Exception as e:
        db.rollback()
        post = db.get(Post, post_id)
        if post:
            post.status = PostStatus.failed
            post.error = str(e)
            db.commit()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    generate_post_task.delay(1)