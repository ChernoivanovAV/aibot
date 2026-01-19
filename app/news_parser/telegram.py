from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from telethon import TelegramClient
from telethon.tl.types import Message

from ..config import settings
from ..models import Source
from ..utils import sha256_hex


def parse_tg_source(source: Source) -> list[dict]:
    """Sync wrapper for Celery."""
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
