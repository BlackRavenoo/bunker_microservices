from dataclasses import dataclass

@dataclass
class TelegramUser:
    _id: int
    name: str

    @property
    def id(self):
        return f"tg:{self._id}"
    
@dataclass
class VotingCandidate:
    name: str
    user_id: int
    votes_count: int