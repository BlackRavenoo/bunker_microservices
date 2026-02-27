from fastapi import APIRouter, status

from services.game_service.app.api.deps import GameServiceDep, VotingServiceDep
from shared.src.enums import TieDecisionAction
from shared.src.schemas.game import GameCreateResponse, GameSchemaAdd, GameSchemaMakeDecision

router = APIRouter(prefix="/games", tags=["games"])

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=GameCreateResponse
)
async def create_game(
    schema: GameSchemaAdd,
    service: GameServiceDep
):
    game_id = await service.create_game(
        host_id=schema.host_id
    )

    return {"game_id": game_id}

@router.post(
    "/{id}/start",
    status_code=status.HTTP_200_OK
)
async def start_game(
    id: str,
    service: GameServiceDep,
):
    await service.start_game(id)

@router.post(
    "/{id}/voting/start",
    status_code=status.HTTP_200_OK
)
async def start_voting(
    id: str,
    service: VotingServiceDep
):
    await service.start_voting(game_id=id)

@router.post(
    "/{id}/voting/make_decision",
    status_code=status.HTTP_200_OK
)
async def skip_voting(
    id: str,
    schema: GameSchemaMakeDecision,
    service: VotingServiceDep
):
    match schema.action:
        case TieDecisionAction.SKIP:
            await service.skip_voting(
                game_id=id
            )
        case TieDecisionAction.KICK_ALL:
            ...
        case TieDecisionAction.REVOTE:
            await service.revote(
                game_id=id
            )