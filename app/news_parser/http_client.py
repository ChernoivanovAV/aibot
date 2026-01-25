import requests
from typing import Optional
from app.config import settings


def get(
        url: str,
        *,  # передавать параметры только по имени
        headers: Optional[dict] = None,
        timeout: int = 10,
) -> requests.Response:

    return requests.get(
        url=url,
        headers=headers,
        timeout=timeout,
    )
