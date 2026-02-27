from typing import Self
from services.game_service.app.infrastructure.db.session import async_session_maker
from services.game_service.app.domain.uow import UnitOfWork
from services.game_service.app.infrastructure.repositories.attribute import SQLAttributeRepository
from services.game_service.app.infrastructure.repositories.character import SQLCharacterRepository
from services.game_service.app.infrastructure.repositories.game import SQLGameRepository


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self):
        self.session_factory = async_session_maker

    async def __aenter__(self) -> Self:
        self.session = self.session_factory()

        self.games = SQLGameRepository(self.session)
        self.characters = SQLCharacterRepository(self.session)
        self.attributes = SQLAttributeRepository(self.session)

        return self

    async def __aexit__(self, *args):
        await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()