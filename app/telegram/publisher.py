from app.config import settings
from app.telegram.bot import send_message
import logging

log = logging.getLogger(__name__)


def publish_to_channel(text: str) -> None:
    # DRYRUN если не настроили канал
    log.info("Publishing to channel: %s", text)
    log.info("TG_TARGET_CHANNEL: %s", settings.TG_TARGET_CHANNEL)

    if not settings.TG_TARGET_CHANNEL:
        log.warning("Publish skipped: TG_TARGET_CHANNEL is not set")
        return

    send_message(settings.TG_TARGET_CHANNEL, text)
