# Project M4-2: AI-генератор постов для Telegram (skeleton)

## Что внутри
- FastAPI API (CRUD источников/ключевых слов, история новостей/постов, ручные триггеры)
- SQLAlchemy + SQLite (для MVP)
- Celery + Redis (очереди) + Beat (расписание)
- Парсер Habr RSS (как пример)
- OpenAI генерация постов (через `OPENAI_API_KEY`)
- Telethon заготовки чтения/публикации (работает после заполнения TG_* в `.env`)

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
cp .env .env
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

## Быстрый тест (через Swagger)
1) Добавь источник Habr RSS:
`POST /api/sources/`
```json
{
  "type": "site",
  "name": "Habr RSS",
  "url": "https://habr.com/ru/rss/all/all/?fl=ru",
  "enabled": true
}
```

2) Запусти пайплайн вручную:
`POST /api/pipeline/run`

3) Посмотри результаты:
`GET /api/news/`
`GET /api/posts/`

## Важно
- Пока `TG_TARGET_CHANNEL` не задан — публикация работает в режиме DRYRUN (печать в консоль).
- Для реальной публикации через Telethon: заполни `TG_API_ID`, `TG_API_HASH`, `TG_TARGET_CHANNEL` и запусти worker. При первом запуске Telethon попросит авторизацию (код/пароль 2FA) в консоли.
