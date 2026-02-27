from pydantic import BaseModel

from shared.src.enums import TieDecisionAction

class GameSchemaAdd(BaseModel):
    host_id: str

class GameSchemaStart(BaseModel):
    game_id: str

class GameSchemaEnd(BaseModel):
    game_id: str

class GameSchemaStartVoting(BaseModel):
    game_id: str

class GameSchemaMakeDecision(BaseModel):
    action: TieDecisionAction

# Responses

class GameCreateResponse(BaseModel):
    game_id: str

class GameGetResponse(BaseModel):
    ...