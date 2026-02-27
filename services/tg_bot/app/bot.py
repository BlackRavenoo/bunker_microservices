import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from services.tg_bot.app.core.config import settings
from services.tg_bot.app.infrastructure.db.db import close_db, init_db
from services.tg_bot.app.infrastructure.repositories.mongo.game import MongoGameRepository
from services.tg_bot.app.messaging.broker import init_broker, shutdown_broker
from services.tg_bot.app.messaging.handlers import register_event_handlers
from services.tg_bot.app.handlers.game import router as game_router
from services.tg_bot.app.callbacks.handlers import router as callback_router
from services.tg_bot.app.middlewares.error import ErrorHandlerMiddleware
from services.tg_bot.app.services.game import GameService
from shared.src.game_client import GameClient


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot: Bot = Bot(
    token=settings.bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp: Dispatcher | None = None

def init_dispatcher() -> Dispatcher:
    global dp
    if dp is None:
        dp = Dispatcher()
        
        dp.include_routers(game_router, callback_router)

    dp.message.middleware(ErrorHandlerMiddleware())
    dp.callback_query.middleware(ErrorHandlerMiddleware())
    dp.callback_query.middleware(CallbackAnswerMiddleware())

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    return dp

def get_dispatcher() -> Dispatcher:
    if dp is None:
        raise RuntimeError("Dispatcher not initialized. Call init_dispatcher() first.")
    return dp

async def on_startup():
    logger.info("Starting bot initialization...")
    
    broker = await init_broker()

    game_client = GameClient(settings.game_service_url)
    
    db = init_db(settings.mongo_uri, settings.mongo_db_name)
    game_repo = await MongoGameRepository.create(db)

    game_service = GameService(
        game_client,
        game_repo
    )

    register_event_handlers(broker, bot, game_service)

    await broker.start()

    dp.workflow_data.update(
        game_service=game_service
    )

    me = await bot.get_me()
    bot.username = me.username
    
    logger.info(f"Bot started in {settings.bot_mode.upper()} mode")


async def on_shutdown():
    logger.info("Shutting down bot...")
    
    await bot.session.close()

    if "game_service" in dp.workflow_data:
        await dp.workflow_data["game_service"].game_client.close()
    
    await shutdown_broker()

    await close_db()
    
    logger.info("Bot stopped")