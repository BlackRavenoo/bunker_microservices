from fastapi import APIRouter

from services.game_service.app.api.v1.router import router as v1_router

router = APIRouter()

router.include_router(v1_router)