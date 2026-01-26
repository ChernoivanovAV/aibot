import asyncio
import logging

from telethon import TelegramClient
from app.config import settings

log = logging.getLogger(__name__)

_client = None
_client_lock = asyncio.Lock()


async def get_shared_client() -> TelegramClient:
    if not settings.TG_API_ID or not settings.TG_API_HASH:
        raise RuntimeError("TG_API_ID/TG_API_HASH are not set")

    if not settings.TG_BOT_TOKEN:
        raise RuntimeError("TG_BOT_TOKEN is not set")

    global _client
    async with _client_lock:
        if _client is None:
            _client = await TelegramClient(
                session=settings.TG_BOT_SESSION,
                api_id=settings.TG_API_ID,
                api_hash=settings.TG_API_HASH,
            ).start(bot_token=settings.TG_BOT_TOKEN)
        else:
            if not _client.is_connected():
                await _client.connect()
    return _client


async def send_async(channel: str, text: str, delay: float) -> None:
    client = await get_shared_client()
    if delay > 0:
        log.info('Delay set to %s', delay)
        await asyncio.sleep(delay)
    await client.send_message(channel, text)


async def disconnect() -> None:
    global _client
    if isinstance(_client, TelegramClient):
        _client.disconnect()
