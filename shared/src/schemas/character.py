from pydantic import BaseModel

from shared.src.enums import AttributeCategory

class CharacterSchemaBase(BaseModel):
    game_id: str
    user_id: str

class CharacterSchemaAdd(CharacterSchemaBase):
    name: str

class CharacterSchemaReveal(CharacterSchemaBase):
    attribute: AttributeCategory
    index: int | None

class CharacterSchemaVote(CharacterSchemaBase):
    target_user_id: str