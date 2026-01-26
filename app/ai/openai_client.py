"""OpenAI client factory with configured HTTP settings."""

import logging

import httpx
from openai import OpenAI

from app.config import settings

log = logging.getLogger(__name__)


def get_openai_client() -> OpenAI:
    """Create a configured OpenAI client with optional proxy support."""
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set")

    client_kwargs = {
        "timeout": httpx.Timeout(60.0),
    }

    if settings.PROXY_DEBUG:
        client_kwargs |= {
            "proxy": settings.PROXY_DEBUG,
            "verify": False,
            "http2": False,
        }

    http_client = httpx.Client(**client_kwargs)

    log.info("OpenAI Client created")
    log.info("OPENAI_BASE_URL: %s", settings.OPENAI_BASE_URL)

    return OpenAI(
        base_url=settings.OPENAI_BASE_URL,
        api_key=settings.OPENAI_API_KEY,
        http_client=http_client,
    )
