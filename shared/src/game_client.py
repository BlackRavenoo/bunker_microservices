from functools import wraps
from typing import get_type_hints
from aiohttp import ClientResponse, ClientSession
from msgspec.json import Decoder

from shared.src.exceptions import build_error_code_map
from shared.src.schemas.character import CharacterSchemaAdd, CharacterSchemaReveal, CharacterSchemaVote
from shared.src.schemas.game import GameCreateResponse, GameSchemaAdd, GameSchemaMakeDecision, GameSchemaStart, GameSchemaStartVoting

ERROR_CODE_MAP = build_error_code_map()

def decode_response(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        hints = get_type_hints(func)
        return_type = hints.get('return')
        
        if return_type is None:
            raise ValueError(f"Function {func.__name__} must have return type annotation")
        
        raw_bytes = await func(self, *args, **kwargs)
        
        data = self.decoder.decode(raw_bytes)
        return return_type.model_validate(data)
    
    return wrapper

class GameClient:
    def __init__(self, base_url: str):
        self.session = ClientSession(base_url=base_url)
        self.decoder = Decoder(dict)
        
    @decode_response
    async def create_game(self, schema: GameSchemaAdd) -> GameCreateResponse:
        async with self.session.post("/v1/games", json=schema.model_dump()) as resp:
            await self._raise_for_error(resp)
            return await resp.read()

    async def add_character(self, schema: CharacterSchemaAdd):
        async with self.session.post("/v1/characters", json=schema.model_dump()) as resp:
            await self._raise_for_error(resp)

    async def start_game(self, schema: GameSchemaStart):
        async with self.session.post(f"/v1/games/{schema.game_id}/start") as resp:
            await self._raise_for_error(resp)

    async def reveal_attribute(self, schema: CharacterSchemaReveal):
        async with self.session.post("/v1/characters/reveal", json=schema.model_dump()) as resp:
            await self._raise_for_error(resp)

    async def start_voting(self, schema: GameSchemaStartVoting):
        async with self.session.post(f"/v1/games/{schema.game_id}/voting/start") as resp:
            await self._raise_for_error(resp)
    
    async def vote(self, schema: CharacterSchemaVote):
        async with self.session.post("/v1/characters/vote", json=schema.model_dump()) as resp:
            await self._raise_for_error(resp)
    
    async def make_decision(self, schema: GameSchemaMakeDecision):
        async with self.session.post(
            f"/v1/games/{schema.game_id}/voting/make_decision",
            json=schema.model_dump(exclude={"game_id"})
        ) as resp:
            await self._raise_for_error(resp)

    async def _raise_for_error(self, resp: ClientResponse):
        if resp.status < 400:
            return
        body = await resp.json()
        error_code = body.get("error_code")
        if error_code and error_code in ERROR_CODE_MAP:
            raise ERROR_CODE_MAP[error_code]()
        resp.raise_for_status()

    async def close(self):
        await self.session.close()