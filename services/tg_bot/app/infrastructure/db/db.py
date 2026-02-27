from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

_client: AsyncMongoClient | None = None

_db: AsyncDatabase | None = None

def init_db(uri: str, db_name: str) -> AsyncDatabase:
    global _client, _db

    _client = AsyncMongoClient(uri)
    _db = _client[db_name]

    return _db

def get_db() -> AsyncDatabase:
    if _db is None:
        raise RuntimeError("Database not initialized")
    return _db

async def close_db():
    if _client:
        await _client.close()