# Bunker Game

Микросервисная реализация игры "Бункер".

## Архитектура

- **Game Service** — основная логика игры (FastAPI + PostgreSQL)
- **Telegram Bot** — взаимодействие с игроками через Telegram бота (Aiogram + MongoDB)
- **Shared** — общие типы, события, схемы
- **RabbitMQ** — шина событий для межсервисного взаимодействия

# Запуск

```sh
bash init.sh
# Data seeding (optional)
python -m seed
```

## Переменные окружения
# Game Service
DATABASE_URL, RABBITMQ_URL

# Telegram Bot
BOT_TOKEN, MONGODB_URL