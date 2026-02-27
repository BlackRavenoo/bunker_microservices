from fastapi import APIRouter

from services.game_service.app.api.v1.endpoints.game import router as game_router
from services.game_service.app.api.v1.endpoints.character import router as character_router

router = APIRouter(prefix="/v1")

router.include_router(game_router)
router.include_router(character_router)