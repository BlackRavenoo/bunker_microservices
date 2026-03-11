from pydantic import BaseModel

from shared.src.enums import Gender, VotingResult
from shared.src.events import Character, VoteDetail

class CharacterWithoutAttrs(BaseModel):
    id: int
    user_id: str
    username: str
    is_kicked: bool
    voted_for: int | None

class UserAttributeDTO[T](BaseModel):
    value: T
    is_revealed: bool

class CharacterDTO(BaseModel):
    id: int
    user_id: str
    username: str
    is_kicked: bool
    biology: UserAttributeDTO[tuple[int, Gender]]
    health: UserAttributeDTO[str]
    profession: UserAttributeDTO[str]
    hobby: UserAttributeDTO[str]
    phobia: UserAttributeDTO[str]
    item: UserAttributeDTO[str]
    facts: list[UserAttributeDTO[str]]

    def into_shared(self) -> Character:
        return Character(**self.model_dump(exclude={'id'}))

class VotingParticipant(BaseModel):
    id: int
    user_id: str
    name: str
    votes_count: int
    is_voted: bool

    def into_shared(self) -> VoteDetail:
        return VoteDetail(
            **self.model_dump(exclude={'is_voted'})
        )

class VotingMetadata(BaseModel):
    count_to_kick: int
    places_count: int
    force_voting: bool

class VotingDistribution(BaseModel):
    result: VotingResult
    candidates_to_kick: list[VotingParticipant]
    remaining_members: list[VotingParticipant]