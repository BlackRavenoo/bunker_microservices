from abc import ABC, abstractmethod

from services.game_service.app.domain.uow import UnitOfWork

class Action(ABC):
    @abstractmethod
    async def execute(self, uow: UnitOfWork):
        pass

    @abstractmethod
    def is_valid(self) -> bool:
        pass