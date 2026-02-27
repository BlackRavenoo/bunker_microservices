from contextlib import asynccontextmanager
from fastapi import FastAPI
import sentry_sdk

from services.game_service.app.api.exception_handlers import register_exception_handlers
from services.game_service.app.core.config import settings
from services.game_service.app.api.main import router
from services.game_service.app.infrastructure.messaging.rabbitmq import init_publisher, stop_publisher


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up game service...")
    
    publisher = init_publisher()
    
    await publisher.start()

    yield

    await stop_publisher()
    
    print("Shutting down game service...")


def create_app() -> FastAPI:
    if settings.is_production and settings.sentry_dsn:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            send_default_pii=True,
            traces_sample_rate=0.1,
            profile_session_sample_rate=0.1,
            profile_lifecycle="trace",
        )
    
    app = FastAPI(
        title="Game Service",
        description="Core game logic service",
        version="0.1.0",
        lifespan=lifespan
    )
    
    @app.get("/health")
    async def health():
        return {"status": "ok", "service": "game-service"}
    
    app.include_router(router)

    register_exception_handlers(app)
    
    return app