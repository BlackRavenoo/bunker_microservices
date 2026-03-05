from enum import Enum

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"

    def __str__(self):
        match self:
            case Gender.MALE:
                return "Мужчина"
            case Gender.FEMALE:
                return "Женщина"

class CharacterStatus(Enum):
    Alive = 0
    Protected = 1
    Kicked = 2

class GameStatus(Enum):
    BeforeStart = 0
    Discussion = 1
    Voting = 2
    Decision = 3
    End = 4

class BunkerElementType(Enum):
    ITEM = 0
    ROOM = 1
    INFO = 2

class AttributeCategory(str, Enum):
    BIOLOGY = "biology"
    HEALTH = "health"
    PROFESSION = "profession"
    HOBBY = "hobby"
    PHOBIA = "phobia"
    FACT = "fact"
    ITEM = "item"

class ActionType(Enum):
    CHANGE = 0
    STEAL = 1
    REVEAL = 2
    INFO = 3

class ActionValue(Enum):
    BIOLOGY = "biology"
    HEALTH = "health"
    PROFESSION = "profession"
    HOBBY = "hobby"
    PHOBIA = "phobia"
    ITEM = "item"
    CATASTROPHE = "catastrophe"
    TEXT = "text"

class ActionTarget(Enum):
    ANY = 0
    ALL = 1
    NOT_SELF = 2
    NONE = 3

class VotingResult(Enum):
    KICK = 0            # Character(s) kicked
    TIE_DECISION = 1    # Kick both, revote or skip
    REVOTE_DECISION = 2 # Revote or skip
    KICK_AND_REVOTE = 3 # Kick and revote to kick another
    REVOTE = 4          # Revote to kick another

class MakeDecisionAction(Enum):
    SKIP = 0
    KICK_ALL = 1
    REVOTE = 2