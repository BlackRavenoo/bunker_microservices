from fastapi import APIRouter, status

from services.game_service.app.api.deps import CharacterServiceDep, VotingServiceDep
from shared.src.schemas.character import CharacterSchemaAdd, CharacterSchemaReveal, CharacterSchemaVote

router = APIRouter(prefix="/characters", tags=["characters"])

@router.post(
    "",
    status_code=status.HTTP_201_CREATED
)
async def add_character(
    schema: CharacterSchemaAdd,
    service: CharacterServiceDep
):
    await service.add_character(**schema.model_dump())

@router.post(
    "/reveal",
    status_code=status.HTTP_200_OK
)
async def reveal_attribute(
    schema: CharacterSchemaReveal,
    service: CharacterServiceDep,
):
    await service.reveal_attribute(**schema.model_dump())

@router.post(
    "/vote",
    status_code=status.HTTP_200_OK
)
async def vote(
    schema: CharacterSchemaVote,
    service: VotingServiceDep
):
    await service.vote(
        game_id=schema.game_id,
        user_id=schema.user_id,
        target_user_id=schema.target_user_id
    )