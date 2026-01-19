from __future__ import annotations

import time
from openai import RateLimitError, APIError
from ..config import settings
from ..models import NewsItem
from .openai_client import get_openai_client


SYSTEM_PROMPT = "Ты редактор новостного Telegram-канала. Пиши ярко, кратко, без воды."

USER_TEMPLATE = """Сделай короткий пост для Telegram на русском:
- 1-2 абзаца, суммарно 300-700 символов
- добавь 2-4 подходящих emoji
- в конце добавь call-to-action (вопрос/предложение обсудить)
- если есть ссылка — добавь ее в конце отдельной строкой

Заголовок: {title}
Сводка: {summary}
Источник: {source}
Ссылка: {url}
"""


def generate_telegram_post(news: NewsItem) -> str:
    client = get_openai_client()

    prompt = USER_TEMPLATE.format(
        title=news.title,
        summary=news.summary,
        source=news.source,
        url=news.url or "",
    )

    last_err: Exception | None = None
    for attempt in range(5):
        try:
            resp = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.8,
            )
            return resp.choices[0].message.content.strip()
        except (RateLimitError, APIError) as e:
            last_err = e
            time.sleep(1.5 * (attempt + 1))
        except Exception as e:
            # non-retryable
            raise e

    raise RuntimeError(f"OpenAI failed after retries: {last_err}")
