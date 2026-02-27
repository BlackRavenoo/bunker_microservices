from fastapi import APIRouter, Header, HTTPException, status
from aiogram.types import Update

from services.tg_bot.app.bot import bot, get_dispatcher
from services.tg_bot.app.core.config import settings

router = APIRouter()

@router.post(settings.webhook_path)
async def telegram_webhook(
    update: dict,
    x_telegram_bot_api_secret_token: str | None = Header(None)
):
    if settings.webhook_secret:
        if x_telegram_bot_api_secret_token != settings.webhook_secret:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN
            )
        
    dp = get_dispatcher()
    
    telegram_update = Update(**update)
    await dp.feed_update(bot, telegram_update)