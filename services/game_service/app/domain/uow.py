from abc import ABC, abstractmethod
from typing import Self, Type

from services.game_service.app.domain.repositories.attribute import AttributeRepository
from services.game_service.app.domain.repositories.character import CharacterRepository
from services.game_service.app.domain.repositories.game import GameRepository


class UnitOfWork(ABC):
    games: Type[GameRepository]
    characters: Type[CharacterRepository]
    attributes: Type[AttributeRepository]
    
    @abstractmethod
    def __init__(self):
        ...

    @abstractmethod
    async def __aenter__(self) -> Self:
        ...

    @abstractmethod
    async def __aexit__(self, *args):
        ...

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...