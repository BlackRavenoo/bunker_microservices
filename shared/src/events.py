from msgspec import Struct

from shared.src.enums import AttributeCategory, Gender, VotingResult

PLAYER_JOINED = "player.joined"
GAME_STARTED = "game.started"
ATTRIBUTE_REVEALED = "attribute.revealed"
VOTING_STARTED = "voting.started"
PLAYER_VOTED = "player.voted"
VOTING_ENDED = "voting.ended"
ROUND_STARTED = "round.started"

class Attribute[T](Struct):
    value: T
    is_revealed: bool

class Character(Struct):
    user_id: str
    is_kicked: bool

    biology: Attribute[tuple[int, Gender]]
    health: Attribute[str]
    profession: Attribute[str]
    hobby: Attribute[str]
    phobia: Attribute[str]
    item: Attribute[str]
    facts: list[Attribute[str]]
    # actions: list[Action]

    username: str
    
class Catastrophe(Struct):
    name: str
    description: str

class Bunker(Struct):
    items: list[str]
    rooms: list[str]
    info: list[str]
    places_count: int

class Game(Struct):
    characters: list[Character]
    catastrophe: Catastrophe
    bunker: Bunker

class VoteDetail(Struct):
    id: int
    user_id: str
    name: str
    votes_count: int

class User(Struct):
    user_id: int
    name: str

# Events

class GameEvent(Struct):
    event_type: str
    game_id: str

class PlayerJoined(GameEvent, kw_only=True, omit_defaults=True):
    event_type: str = PLAYER_JOINED
    user: User

class GameStarted(GameEvent, kw_only=True, omit_defaults=True):
    event_type: str = GAME_STARTED
    game: Game

class AttributeRevealed[T](GameEvent, kw_only=True, omit_defaults=True):
    event_type: str = ATTRIBUTE_REVEALED
    user: User
    value: T
    is_all_revealed: bool
    category: AttributeCategory

class VotingStarted(GameEvent, kw_only=True, omit_defaults=True):
    event_type:str = VOTING_STARTED
    characters: list[Character]

class PlayerVoted(GameEvent, kw_only=True, omit_defaults=True):
    event_type: str = PLAYER_VOTED
    user: User
    target: User
    vote_details: list[VoteDetail]

class VotingEnded(GameEvent, kw_only=True, omit_defaults=True):
    event_type: str = VOTING_ENDED
    candidates_for_kick: list[VoteDetail]
    remaining_members: list[VoteDetail]
    voting_result: VotingResult
    game_ended: bool
    count_to_kick: int | None = None

class NewRoundStarted(GameEvent, kw_only=True, omit_defaults=True):
    event_type: str = ROUND_STARTED
    count_to_kick: int