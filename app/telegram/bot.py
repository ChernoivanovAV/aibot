import asyncio
from telethon import TelegramClient
from telethon.sessions import MemorySession
from app.config import settings


def get_client() -> TelegramClient:
    if not settings.TG_API_ID or not settings.TG_API_HASH:
        raise RuntimeError("TG_API_ID/TG_API_HASH are not set")

    if not settings.TG_BOT_TOKEN:
        raise RuntimeError("TG_BOT_TOKEN is not set")

    # Use in-memory session to avoid sqlite locking when multiple workers publish.
    session = MemorySession()
    return TelegramClient(session, settings.TG_API_ID, settings.TG_API_HASH)


async def _send_async(channel: str, text: str) -> None:
    client = get_client()
    await client.start(bot_token=settings.TG_BOT_TOKEN)
    try:
        await asyncio.sleep(2)
        await client.send_message(channel, text)
    finally:
        await client.disconnect()


def send_message(channel: str, text: str) -> None:
    asyncio.run(_send_async(channel, text))


if __name__ == "__main__":
    get_client()
