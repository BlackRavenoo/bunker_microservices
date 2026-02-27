from pymongo import ASCENDING
from pymongo.asynchronous.database import AsyncDatabase
from services.tg_bot.app.domain.dto import Game
from services.tg_bot.app.domain.repositories.game import GameRepository


class MongoGameRepository(GameRepository):
    def __init__(self, db: AsyncDatabase):
        self.collection = db.games

    @classmethod
    async def create(cls, db: AsyncDatabase) -> "MongoGameRepository":
        instance = cls(db)
        await instance._ensure_indexes()
        return instance

    async def _ensure_indexes(self):
        await self.collection.create_index([("chat_id", ASCENDING)], unique=True)
        await self.collection.create_index([("game_id", ASCENDING)], unique=True)

    async def get_by_chat_id(self, chat_id: int) -> Game | None:
        binding = await self.collection.find_one({"chat_id": chat_id})
        return Game(
            chat_id=binding["chat_id"],
            game_id=binding["game_id"],
            message_id=binding["message_id"]
        ) if binding else None
    
    async def get_by_game_id(self, game_id: int) -> Game | None:
        binding = await self.collection.find_one({"game_id": game_id})
        return Game(
            chat_id=binding["chat_id"],
            game_id=binding["game_id"],
            message_id=binding["message_id"]
        ) if binding else None
    
    async def add_game_id_binding(self, chat_id: int, game_id: int):
        await self.collection.insert_one({
            "chat_id": chat_id,
            "game_id": game_id,
            "message_id": None
        })

    async def update_message_id(self, chat_id, message_id):
        await self.collection.update_one(
            {"chat_id": chat_id},
            {"$set": {"message_id": message_id}}
        )

    async def delete_game(self, game_id):
        await self.collection.delete_one({"game_id": game_id})