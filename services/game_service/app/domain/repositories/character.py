from abc import abstractmethod, ABC
from typing import Any

from services.game_service.app.domain.dto import CharacterDTO, CharacterWithoutAttrs
from services.game_service.app.domain.dto.update import CharacterBatchUpdateDTO, CharacterUpdateDTO
from shared.src.enums import AttributeCategory

class CharacterRepository(ABC):
    @abstractmethod
    async def add_character(self, game_id: str, user_id: str, name: str):
        pass

    @abstractmethod
    async def get_character_ids(self, game_id: str) -> list[int]:
        pass

    @abstractmethod
    async def update_characters(self, updates: list[CharacterBatchUpdateDTO]):
        pass

    @abstractmethod
    async def update_active_characters_by_game_id(self, game_id: str, updates: CharacterUpdateDTO):
        pass

    @abstractmethod
    async def reveal_attribute(self, game_id: str, user_id: str, attribute: AttributeCategory, index: int | None) -> Any:
        pass

    @abstractmethod
    async def get_characters_without_attrs(self, game_id: str, user_ids: list[str]) -> list[CharacterWithoutAttrs | None]:
        pass

    @abstractmethod
    async def is_all_revealed(self, game_id: str) -> bool | None:
        pass

    @abstractmethod
    async def get_characters(self, game_id: str) -> list[CharacterDTO]:
        pass

    @abstractmethod
    async def get_active_characters(self, game_id: str) -> list[CharacterDTO]:
        pass

    @abstractmethod
    async def vote(self, game_id: str, user_id: str, target_id: int):
        pass