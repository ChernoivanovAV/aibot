from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from telethon import TelegramClient
from telethon.tl.types import Message

from app.config import settings
from app.database import SessionLocal
from app.models import Source
from app.utils import sha256_hex
import logging
from pprint import pprint

log = logging.getLogger(__name__)


def parse_tg_source(source: Source) -> list[dict]:
    """Sync wrapper for Celery."""
    log.info("Parsing Telegram source")
    log.info(f"source.url: {source.url}")

    if not settings.TG_API_ID or not settings.TG_API_HASH:
        return []
    return asyncio.run(_parse_tg_async(source))


async def _parse_tg_async(source: Source) -> list[dict]:
    items: list[dict] = []

    async with TelegramClient(settings.TG_SESSION, settings.TG_API_ID, settings.TG_API_HASH) as client:
        entity = source.url  # username like @channel or link
        async for msg in client.iter_messages(entity, limit=30):
            if not isinstance(msg, Message):
                continue
            if not msg.message:
                continue

            text = msg.message.strip()
            title = text.splitlines()[0][:140] if text else "(no title)"

            published_at = datetime.now(tz=timezone.utc)
            if msg.date:
                dt = msg.date
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                published_at = dt.astimezone(timezone.utc)

            # try build url if message has id and username
            link = None
            try:
                if isinstance(entity, str) and entity.startswith("@"):
                    link = f"https://t.me/{entity[1:]}/{msg.id}"
            except Exception:
                pass

            fingerprint = sha256_hex(link or f"{source.name}|{msg.id}|{published_at.isoformat()}")

            items.append({
                "title": title[:512],
                "url": (link[:1024] if link else None),
                "summary": text[:5000],
                "source": source.name,
                "published_at": published_at.replace(tzinfo=None),
                "raw_text": text[:10000],
                "fingerprint": fingerprint,
            })

    return items


if __name__ == "__main__":
    db = SessionLocal()
    print("DB URL:", db.bind.url)
    db.bind.echo = True
    source = db.get(Source, 2)
    print(vars(source))
    items = parse_tg_source(source)
    pprint(items)
