from abc import abstractmethod, ABC

from services.game_service.app.domain.dto import VotingMetadata, VotingParticipant
from services.game_service.app.domain.dto.update import GameUpdateDTO

class GameRepository(ABC):
    @abstractmethod
    async def create_game(self, host_id: str) -> str:
        pass

    @abstractmethod
    async def start_game(self, game_id: str):
        pass

    @abstractmethod
    async def get_game(self, game_id: str): # TODO: указать тип
        pass

    @abstractmethod
    async def generate_catastrophe(self, game_id: str):
        pass

    @abstractmethod
    async def start_voting(self, game_id: str):
        pass

    @abstractmethod
    async def get_voting_participants(self, game_id: str) -> list[VotingParticipant]:
        pass

    @abstractmethod
    async def get_voting_metadata(self, game_id: str) -> VotingMetadata:
        pass

    @abstractmethod
    async def update_game(self, game_id: str, update_data: GameUpdateDTO):
        pass