# Project M4-2: AI-генератор постов для Telegram

## Что внутри
- FastAPI API: CRUD для источников/ключевых слов, история новостей/постов, ручные триггеры.
- SQLAlchemy + SQLite (MVP-хранилище).
- Celery + Redis + Beat для фоновых задач и расписаний.
- Парсер Habr RSS как пример источника.
- Генерация постов через OpenAI (`OPENAI_API_KEY`).
- Telethon для чтения/публикации в Telegram (при заполненных `TG_*`).

## Требования
- Python 3.10+
- Docker (для Redis)

## Быстрый старт
### 1) Установка
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Redis
```bash
docker compose up -d
```

### 3) Настройки
```bash
cp .env.example .env
# отредактируй OPENAI_API_KEY и TG_* (если нужна реальная публикация)
```

### 4) Запуск API
```bash
uvicorn app.main:app --reload
```
Swagger: http://127.0.0.1:8000/docs

### 5) Запуск Celery worker и beat (2 терминала)
```bash
celery -A celery_worker.celery_app worker -l info
```
```bash
celery -A celery_worker.celery_app beat -l info
```

## Переменные окружения
Ключевые настройки задаются в `.env`:

| Переменная | Назначение |
| --- | --- |
| `OPENAI_API_KEY` | Ключ OpenAI для генерации постов. |
| `OPENAI_MODEL` | Модель для генерации (по умолчанию `gpt-4o-mini`). |
| `OPENAI_BASE_URL` | Кастомный base URL (опционально). |
| `REDIS_URL` | URL Redis для Celery. |
| `DATABASE_URL` | Явный URL БД (опционально, по умолчанию SQLite). |
| `POLL_INTERVAL_MINUTES` | Частота опроса источников. |
| `TG_API_ID`, `TG_API_HASH` | Данные для Telethon. |
| `TG_TARGET_CHANNEL` | Канал публикации (при отсутствии — DRYRUN). |
| `TG_BOT_TOKEN` | Токен бота, если используется бот-сценарий. |

## Быстрый тест (через Swagger)
1) Добавь источник Habr RSS:
`POST /api/v1/sources/`
```json
{
  "type": "site",
  "name": "Habr RSS",
  "url": "https://habr.com/ru/rss/all/all/?fl=ru",
  "enabled": true
}
```

2) Запусти пайплайн вручную:
`POST /api/v1/pipeline/run`

3) Посмотри результаты:
`GET /api/v1/news/`
`GET /api/v1/posts/`

## Важно
- Пока `TG_TARGET_CHANNEL` не задан — публикация работает в режиме DRYRUN (печать в консоль).
- Для реальной публикации через Telethon: заполни `TG_API_ID`, `TG_API_HASH`, `TG_TARGET_CHANNEL` и запусти worker. При первом запуске Telethon попросит авторизацию (код/пароль 2FA) в консоли.

## Полезные команды
Запуск через скрипты:
```bash
./run_fastapi.sh
./run_celery.sh
```

Пример ручной генерации без полного пайплайна:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/generate/
```
