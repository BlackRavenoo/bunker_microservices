from services.tg_bot.app.domain.dto import Game
from services.tg_bot.app.domain.repositories.game import GameRepository
from services.tg_bot.app.schema import TelegramUser
from shared.src.enums import AttributeCategory, MakeDecisionAction
from shared.src.exceptions import EntityAlreadyExists, EntityNotFound
from shared.src.game_client import CharacterSchemaReveal, GameClient, GameSchemaStart
from shared.src.schemas.character import CharacterSchemaAdd, CharacterSchemaVote
from shared.src.schemas.game import GameSchemaAdd, GameSchemaMakeDecision, GameSchemaStartVoting

class GameService:
    def __init__(
        self,
        game_client: GameClient,
        game_repository: GameRepository,
    ):
        self.game_client = game_client
        self.game_repository = game_repository

    async def create_game(
        self,
        user: TelegramUser,
        chat_id: int
    ) -> int:
        if await self.game_repository.get_by_chat_id(chat_id):
            raise EntityAlreadyExists()

        resp = await self.game_client.create_game(
            GameSchemaAdd(host_id=user.id)
        )

        await self.game_repository.add_game_id_binding(
            chat_id=chat_id,
            game_id=resp.game_id
        )

        return resp.game_id
    
    async def join_game(
        self,
        user: TelegramUser,
        game_id: int,
    ):
        await self.game_client.add_character(
            CharacterSchemaAdd(
                game_id=game_id,
                user_id=user.id,
                name=user.name
            )
        )

    async def start_game(
        self,
        chat_id: int,
    ):
        game = await self.game_repository.get_by_chat_id(chat_id)
        
        if not game:
            raise EntityNotFound()

        await self.game_client.start_game(GameSchemaStart(
            game_id=game.game_id
        ))

    async def reveal_attribute(
        self,
        user_id: str,
        game_id: str,
        attribute: AttributeCategory,
        index: int | None,
    ):
        user_id = f"tg:{user_id}"

        await self.game_client.reveal_attribute(CharacterSchemaReveal(
            game_id=game_id,
            user_id=user_id,
            attribute=attribute,
            index=index,
        ))

    async def start_voting(
        self,
        game_id: str
    ):
        await self.game_client.start_voting(GameSchemaStartVoting(
            game_id=game_id
        ))

    async def vote(
        self,
        game_id: str,
        user_id: str,
        target_id: str,
    ):
        user_id = f"tg:{user_id}"

        await self.game_client.vote(CharacterSchemaVote(
            game_id=game_id,
            user_id=user_id,
            target_user_id=target_id
        ))

    async def make_decision(
        self,
        game_id: str,
        action: MakeDecisionAction
    ):
        await self.game_client.make_decision(GameSchemaMakeDecision(
            game_id=game_id,
            action=action
        ))

    async def get_game(self, game_id: str) -> Game | None:
        return await self.game_repository.get_by_game_id(
            game_id=game_id
        )

    async def get_game_by_chat_id(self, chat_id: str) -> Game | None:
        return await self.game_repository.get_by_chat_id(
            chat_id=chat_id
        )

    async def update_message_id(self, chat_id: int, message_id: int):
        await self.game_repository.update_message_id(
            chat_id=chat_id,
            message_id=message_id
        )

    async def delete_game(self, game_id: str):
        await self.game_repository.delete_game(
            game_id=game_id
        )