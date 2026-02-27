from dataclasses import dataclass

@dataclass
class Game:
    chat_id: int
    game_id: int
    message_id: int | None