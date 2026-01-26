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
├── aibot.db                     # Локальная база данных (SQLite)
├── app/                         # Основной код приложения
│   ├── ai/                      # Логика работы с ИИ
│   │   ├── generator.py         # Генерация текста/ответов
│   │   ├── openai_client.py     # Клиент для работы с OpenAI API
│   │   └── __init__.py
│   ├── api/                     # HTTP API (FastAPI)
│   │   ├── endpoints.py         # REST-эндпоинты
│   │   ├── schemas.py           # Pydantic-схемы
│   │   └── __init__.py
│   ├── news_parser/             # Парсеры новостных источников
│   │   ├── habr.py              # Парсер Habr
│   │   ├── telegram.py          # Получение новостей из Telegram
│   │   ├── sites.py             # Конфигурация источников
│   │   ├── http_client.py       # HTTP-клиент для запросов
│   │   ├── utils.py             # Вспомогательные функции
│   │   └── __init__.py
│   ├── telegram/                # Telegram-бот
│   │   ├── bot.py               # Инициализация и логика бота
│   │   ├── publisher.py         # Публикация сообщений
│   │   └── __init__.py
│   ├── config.py                # Конфигурация приложения
│   ├── database.py              # Подключение к БД и сессии
│   ├── logging_config.py        # Настройки логирования
│   ├── models.py                # ORM-модели
│   ├── tasks.py                 # Celery-задачи
│   ├── utils.py                 # Общие утилиты
│   ├── main.py                  # Точка входа FastAPI
│   └── __init__.py
├── celery_worker.py             # Конфигурация Celery worker
├── docker-compose.yml           # Docker Compose (Redis)
├── logs/                        # Логи приложения
│   └── aibot.log                # Основной лог-файл
├── poetry.lock                  # Зафиксированные зависимости Poetry
├── pyproject.toml               # Конфигурация проекта и зависимостей
├── requirements.txt             # Зависимости (pip)
├── run_celery.sh                # Скрипт запуска Celery worker
├── run_fastapi.sh               # Скрипт запуска FastAPI
├── screens/                     # Скриншоты/демонстрация работы
│   ├── *.png                    # Скриншоты интерфейса и логов
├── README.md                    # Документация проекта
├── tg.bot.session               # Сессия Telegram-бота
├── tg.bot.session-journal       # Журнал сессии Telegram-бота
└── tg.session                   # Общая Telegram-сессия


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
### Добавить источник
`POST /api/v1/sources/`
```bash
curl -X POST http://127.0.0.1:8000/api/v1/sources/ \
  -H "Content-Type: application/json" \
  -d '{
    "type": "site",
    "name": "Habr.ru",
    "url": "https://habr.com",
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
