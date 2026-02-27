from abc import ABC, abstractmethod

from services.tg_bot.app.domain.dto import Game

class GameRepository(ABC):
    @abstractmethod
    async def get_by_chat_id(self, chat_id: int) -> Game | None:
        pass

    @abstractmethod
    async def get_by_game_id(self, game_id: str) -> Game | None:
        pass

    @abstractmethod
    async def add_game_id_binding(self, chat_id: int, game_id: str):
        pass

    @abstractmethod
    async def update_message_id(self, chat_id: int, message_id: int):
        pass

    @abstractmethod
    async def delete_game(self, game_id: str):
        pass