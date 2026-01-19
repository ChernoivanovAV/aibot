from __future__ import annotations

from ..config import settings
from .bot import send_message


def publish_to_channel(text: str) -> None:
    # DRYRUN если не настроили канал
    if not settings.TG_TARGET_CHANNEL:
        print("[PUBLISH:DRYRUN]\n", text)
        return

    send_message(settings.TG_TARGET_CHANNEL, text)
