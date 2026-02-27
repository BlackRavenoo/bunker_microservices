from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from typing import Callable, Dict, Any, Awaitable
import logging

logger = logging.getLogger(__name__)

class ErrorHandlerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            logger.error(f"Произошла ошибка: {e}", exc_info=True)
            
            if isinstance(event, Message):
                try:
                    await event.answer("Что-то пошло не так!")
                except Exception as send_error:
                    logger.error(f"Не удалось отправить сообщение об ошибке: {send_error}")
            
            return None