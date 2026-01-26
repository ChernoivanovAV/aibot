# AI-генератор постов для Telegram

## Описание
Сервис собирает новости из источников (например, Habr RSS), формирует краткие посты с помощью OpenAI и публикует их в Telegram. Архитектура разделена на HTTP API (FastAPI) и фоновые задачи (Celery) с хранением данных в SQLite (по умолчанию).

## Возможности
- CRUD для источников, ключевых слов, новостей и постов через REST API.
- Планировщик и фоновая обработка (Celery + Redis + Beat).
- Парсинг RSS (пример — Habr).
- Генерация постов через OpenAI (`OPENAI_API_KEY`).
- Публикация в Telegram через Telethon (если заполнены `TG_*`).

## Структура проекта
```
.
├── app/                 # FastAPI-приложение (роуты, сервисы, модели)
├── screens/             # Скриншоты/Демонстрация работы
├── celery_worker.py     # Конфигурация Celery
├── docker-compose.yml   # Redis для фоновых задач
├── run_celery.sh        # Скрипт запуска Celery
├── run_fastapi.sh       # Скрипт запуска API
├── requirements.txt     # Зависимости (pip)
└── README.md            # Документация проекта
```

## Требования
- Python 3.10+
- Docker (для Redis)

## Установка
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Настройки
```bash
cp .env.example .env
# отредактируй OPENAI_API_KEY и TG_* (если нужна реальная публикация)
```

### Переменные окружения
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

## Запуск
### 1) Redis (Docker)
```bash
docker compose up -d
```

### 2) Запуск API
```bash
uvicorn app.main:app --reload
```
Swagger: http://127.0.0.1:8000/docs

### 3) Запуск Celery worker и beat (2 терминала)
```bash
celery -A celery_worker.celery_app worker -l info
```
```bash
celery -A celery_worker.celery_app beat -l info
```

### Быстрый запуск скриптами
```bash
./run_fastapi.sh
./run_celery.sh
```

## Процесс фильтрации и публикации новостей
1) **Сбор данных.** Celery-планировщик по расписанию опрашивает источники (RSS) и сохраняет свежие новости в базу.
2) **Фильтрация.** На этапе обработки учитывается статус источника (`enabled`) и связанные ключевые слова/правила (если настроены). Результатом становятся новости, которые прошли фильтры и готовы к генерации постов.
3) **Генерация постов.** Для каждой отобранной новости сервис формирует краткое описание через OpenAI и сохраняет пост в хранилище.
4) **Публикация.** Если задан `TG_TARGET_CHANNEL`, посты отправляются в Telegram через Telethon. Если канал не задан, публикация выполняется в режиме DRYRUN (вывод в консоль).
5) **Ручной запуск.** Весь пайплайн можно запустить вручную через `POST /api/v1/pipeline/run`, что удобно для тестирования.

## Примеры API-запросов
### Добавить RSS-источник
`POST /api/v1/sources/`
```bash
curl -X POST http://127.0.0.1:8000/api/v1/sources/ \
  -H "Content-Type: application/json" \
  -d '{
    "type": "site",
    "name": "Habr RSS",
    "url": "https://habr.com/ru/rss/all/all/?fl=ru",
    "enabled": true
  }'
```

### Запустить пайплайн вручную
`POST /api/v1/pipeline/run`
```bash
curl -X POST http://127.0.0.1:8000/api/v1/pipeline/run
```

### Получить список новостей
`GET /api/v1/news/`
```bash
curl http://127.0.0.1:8000/api/v1/news/
```

### Получить список постов
`GET /api/v1/posts/`
```bash
curl http://127.0.0.1:8000/api/v1/posts/
```

### Ручная генерация без полного пайплайна
`POST /api/v1/generate/`
```bash
curl -X POST http://127.0.0.1:8000/api/v1/generate/
```

## Важно
- Пока `TG_TARGET_CHANNEL` не задан — публикация работает в режиме DRYRUN (печать в консоль).
- Для реальной публикации через Telethon: заполни `TG_API_ID`, `TG_API_HASH`, `TG_TARGET_CHANNEL` и запусти worker. При первом запуске Telethon попросит авторизацию (код/пароль 2FA) в консоли.
