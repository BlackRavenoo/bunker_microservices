from typing import Annotated

from fastapi import Depends

from services.game_service.app.infrastructure.messaging.rabbitmq import GamePublisher, get_publisher
from services.game_service.app.infrastructure.uow import UnitOfWork, SqlAlchemyUnitOfWork
from services.game_service.app.services.character import CharacterService
from services.game_service.app.services.game import GameService
from services.game_service.app.services.voting import VotingService

UOWDep = Annotated[UnitOfWork, Depends(SqlAlchemyUnitOfWork)]
PublisherDep = Annotated[GamePublisher, Depends(get_publisher)]

def get_character_service(
    uow: UOWDep,
    publisher: PublisherDep
) -> CharacterService:
    return CharacterService(uow=uow, publisher=publisher)

def get_game_service(
    uow: UOWDep,
    publisher: PublisherDep
) -> GameService:
    return GameService(uow=uow, publisher=publisher)

def get_voting_service(
    uow: UOWDep,
    publisher: PublisherDep
) -> GameService:
    return VotingService(uow=uow, publisher=publisher)

CharacterServiceDep = Annotated[CharacterService, Depends(get_character_service)]
GameServiceDep = Annotated[GameService, Depends(get_game_service)]
VotingServiceDep = Annotated[VotingService, Depends(get_voting_service)]