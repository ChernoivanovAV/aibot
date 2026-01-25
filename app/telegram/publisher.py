from app.config import settings
from app.telegram.bot import send_message
import logging

log = logging.getLogger(__name__)


def publish_to_channel(text: str) -> None:
    # DRYRUN если не настроили канал
    log.info(f"Publishing to channel: {text}")
    log.info(f"TG_TARGET_CHANNEL: {settings.TG_TARGET_CHANNEL}")

    if not settings.TG_TARGET_CHANNEL:
        print("[PUBLISH:DRYRUN]\n", text)
        return

    send_message(settings.TG_TARGET_CHANNEL, text)
