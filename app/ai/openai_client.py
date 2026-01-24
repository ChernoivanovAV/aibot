import logging

from openai import OpenAI, AsyncOpenAI
from app.config import settings, BASE_DIR
from httpx_socks import SyncProxyTransport
import httpx


def get_openai_client() -> OpenAI:
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

    logging.info("OpenAI Client created")
    logging.info(f"OPENAI_BASE_URL: {settings.OPENAI_BASE_URL}")

    return OpenAI(
        base_url=settings.OPENAI_BASE_URL,
        api_key=settings.OPENAI_API_KEY,
        http_client=http_client,
    )
