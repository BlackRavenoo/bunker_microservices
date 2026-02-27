from enum import Enum
from pydantic import BaseModel

from shared.src.enums import CharacterStatus, GameStatus, Gender

class NumericOperation(Enum):
    SET = "set"
    INCREMENT = "increment"
    DECREMENT = "decrement"

class NumericFieldUpdate(BaseModel):
    value: int
    operation: NumericOperation = NumericOperation.SET

class NullableFieldUpdate[T](BaseModel):
    value: T | None

class UserAttributeValue[T](BaseModel):
    value: T
    is_revealed: bool = False

class CharacterAttributes(BaseModel):
    biology: UserAttributeValue[tuple[int, Gender]]
    health: UserAttributeValue[str]
    profession: UserAttributeValue[str]
    hobby: UserAttributeValue[str]
    phobia: UserAttributeValue[str]
    facts: list[UserAttributeValue[str]]
    items: list[UserAttributeValue[str]]

class GameUpdateDTO(BaseModel):
    status: GameStatus | None = None
    count_to_kick: NumericFieldUpdate | None = None
    places_count: NumericFieldUpdate | None = None
    force_voting: bool | None = None

class CharacterUpdateDTO(BaseModel):
    status: CharacterStatus | None = None
    needs_to_reveal: bool | None = None
    voted_for: NullableFieldUpdate | None = None

class CharacterBatchUpdateDTO(BaseModel):
    id: int
    status: CharacterStatus | None = None
    attributes: CharacterAttributes | None = None