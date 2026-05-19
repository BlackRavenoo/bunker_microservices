from enum import Enum
from typing import Any, Self
from pydantic import BaseModel, model_validator

from shared.src.enums import AttributeCategory, CharacterStatus, GameStatus, Gender

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
    item: UserAttributeValue[str]
    facts: list[UserAttributeValue[str]]

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

category_to_type = {
    AttributeCategory.BIOLOGY: tuple,
    AttributeCategory.HEALTH: str,
    AttributeCategory.PROFESSION: str,
    AttributeCategory.HOBBY: str,
    AttributeCategory.PHOBIA: str,
    AttributeCategory.FACT: list,
    AttributeCategory.ITEM: str,
}

class BatchUpdateAttributesDTO(BaseModel):
    id: int
    attributes: dict[AttributeCategory, Any]

    @model_validator(mode="after")
    def validate_values(self) -> Self:
        for category, value in self.attributes.items():
            expected_type = category_to_type[category]
            if not isinstance(value, expected_type):
                raise ValueError(
                    f"Category {category}: expected {expected_type}, got {type(value)}"
                )
        
        return self