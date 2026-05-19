from abc import abstractmethod, ABC

from services.game_service.app.domain.dto import ActionCardDTO

class ActionCardRepository(ABC):
    @abstractmethod
    async def get_random_action_cards(
        self,
        count: int
    ) -> list[ActionCardDTO]:
        pass

    @abstractmethod
    async def get_card(self, id: int) -> ActionCardDTO | None:
        pass