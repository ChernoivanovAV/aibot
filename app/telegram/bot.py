from __future__ import annotations

import asyncio
from telethon import TelegramClient
from app.config import settings


def get_client() -> TelegramClient:
    if not settings.TG_API_ID or not settings.TG_API_HASH:
        raise RuntimeError("TG_API_ID/TG_API_HASH are not set")
    return TelegramClient(settings.TG_SESSION, settings.TG_API_ID, settings.TG_API_HASH)


async def _send_async(channel: str, text: str) -> None:
    async with get_client() as client:
        await client.send_message(channel, text)


def send_message(channel: str, text: str) -> None:
    asyncio.run(_send_async(channel, text))
