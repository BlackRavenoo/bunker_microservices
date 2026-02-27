import asyncio
import logging

from fastapi import FastAPI

from services.tg_bot.app.api import health, webhook
from services.tg_bot.app.bot import init_dispatcher, bot
from services.tg_bot.app.core.config import BotMode, settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(
        title="Telegram Bot API"
    )
    
    app.include_router(webhook.router, tags=["webhook"])
    app.include_router(health.router, tags=["health"])

    return app

async def run_polling():
    dp = init_dispatcher()

    await dp.start_polling(bot)

def main():
    if settings.bot_mode == BotMode.POLLING:
        asyncio.run(run_polling())
    else:
        logger.error(
            "For WEBHOOK mode use: "
            "granian --interface asgi app.main:create_app --factory"
        )
        exit(1)


if __name__ == "__main__":
    main()