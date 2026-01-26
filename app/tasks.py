from __future__ import annotations

import asyncio
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
from contextlib import contextmanager

log = logging.getLogger(__name__)

celery_app = Celery(
    "aibot",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.timezone = "UTC"
celery_app.conf.task_routes = {
    "app.tasks.*": {
        "queue": "default"
    }
}

celery_app.conf.beat_schedule = {
    "run-collect-tg-news-every-n-minutes": {
        "task": "app.tasks.collect_tg_news_task",
        "schedule": settings.POLL_INTERVAL_MINUTES * 60,
    },
    "run-collect-site-news-every-n-minutes": {
        "task": "app.tasks.collect_site_news_task",
        "schedule": settings.POLL_INTERVAL_MINUTES * 60,
    },
}

celery_app.autodiscover_tasks(["app"])


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _passes_keyword_filter(db: Session, text: str) -> bool:
    keywords = db.execute(select(Keyword)).scalars().all()
    if not keywords:
        return True
    low = text.lower()
    return any(k.word.lower() in low for k in keywords)


def _collect_for_type(source_type: str) -> dict:
    log.info("Collecting news for type %s", source_type)
    created_news_ids: list[int] = []

    with get_db() as db:
        sources = (
            db.execute(
                select(Source)
                .where(
                    Source.enabled == True,
                    Source.type == source_type,
                )
            )
            .scalars()
            .all())

        log.info("Found %s enabled sources", len(sources))

        for src in sources:
            try:
                if src.type.value == "site":
                    items = parse_site_source(src)
                elif src.type.value == "tg":
                    items = parse_tg_source(src)
                else:
                    raise Exception(f"Unknown source type: {src}")
            except Exception as e:
                log.exception("Parse failed for source=%s: %s", src.name, e)
                continue

            for it in items:
                full_text = f"{it.get('title', '')}\n{it.get('summary', '')}\n{it.get('raw_text', '') or ''}"

                log.info("Collected news: %s", it.get("title", ""))
                if not _passes_keyword_filter(db, full_text):
                    log.info("Keyword filter rejected news for source=%s", src.name)
                    continue

                news = NewsItem(**it)
                db.add(news)
                try:
                    db.flush()
                except Exception:
                    db.rollback()
                    continue

                created_news_ids.append(news.id)
                post = Post(news_id=news.id, status=PostStatus.new)
                db.add(post)

        db.commit()
    return {"created_news": len(created_news_ids)}


@celery_app.task(name="app.tasks.run_pipeline_task")
def run_pipeline_task():
    log.info("Run app.tasks.run_pipeline_task")
    collect_site_news_task()
    collect_tg_news_task()
    publish_posts_task()
    ai_generate_posts_task()
    log.info("End run_pipeline_task")

@celery_app.task(name="app.tasks.collect_site_news_task")
def collect_site_news_task():
    """
        Collect news from site sources.

        Periodic task (Celery Beat).
        Parses enabled site sources and saves new NewsItem entries.
        Deduplication is handled by unique fingerprint.
        """
    return _collect_for_type("site")


@celery_app.task(name="app.tasks.collect_tg_news_task")
def collect_tg_news_task():
    """
        Collect news from Telegram sources.

        Periodic task (Celery Beat).
        Uses Telethon to fetch messages from enabled channels.
        Stores only new items (deduplicated).
        """
    return _collect_for_type("tg")


@celery_app.task(name="app.tasks.ai_generate_posts_task")
def ai_generate_posts_task():
    log.info("Run app.tasks.ai_generate_posts_task")
    posts_generated: list[int] = []
    with get_db() as db:
        posts = (
            db.execute(
                select(Post)
                .join(Post.news)
                .where(
                    Post.status == PostStatus.new
                )
            )
            .scalars()
            .all())

        log.info("Found %s posts to generate", len(posts))
        if not posts:
            return {"error": "posts not found"}

        for post in posts:

            post_id = post.id
            news_id = post.news_id

            try:
                text = generate_telegram_post(post.news)
                post.generated_text = text
                post.status = PostStatus.generated
                post.error = None
                db.commit()
                posts_generated.append(post_id)

            except Exception as e:

                log.exception("Generate post failed for news_id=%s post_id=%s: %s", news_id, post_id, e)
                db.rollback()

                post = db.get(Post, post_id)
                if post:
                    post.status = PostStatus.failed
                    post.error = str(e)
                    db.commit()

    return {
        'generated': posts_generated,
        'count': len(posts_generated)
    }


@celery_app.task(name="app.tasks.publish_posts_task")
def publish_posts_task():
    asyncio.run(_publish_posts_task())


async def _publish_posts_task():
    post_published: list[int] = []
    with get_db() as db:
        posts = (
            db.execute(
                select(Post)
                .where(
                    Post.status == PostStatus.generated
                )
            )
            .scalars()
            .all())

        if not posts:
            return {"error": "posts not found"}

        for post in posts:
            post_id = post.id

            try:
                if not post:
                    continue

                await publish_to_channel(post.generated_text, 5)
                post.status = PostStatus.published
                post.published_at = datetime.now()
                post.error = None
                db.commit()
                post_published.append(post_id)

                log.info('Post published: %s', post_id)

            except Exception as e:
                db.rollback()
                post = db.get(Post, post_id)
                if post:
                    post.status = PostStatus.failed
                    post.error = str(e)
                    db.commit()
                log.exception("Publish post failed for post_id=%s: %s", post_id, e)

    return {
        'published': post_published,
        'count': len(post_published),
    }


if __name__ == "__main__":
    publish_posts_task()
