from aiogram.filters.callback_data import CallbackData

from shared.src.enums import AttributeCategory, MakeDecisionAction

class RevealCallback(CallbackData, prefix="reveal"):
    game_id: str
    attribute: AttributeCategory
    index: int | None = None

class UseActionCallback(CallbackData, prefix="use_action"):
    game_id: str
    index: int
    target: int | None = None

class VoteCallback(CallbackData, prefix="vote", sep="."):
    game_id: str
    target_id: str

class EndVotingCallback(CallbackData, prefix="end_voting"):
    game_id: str

class StartVotingCallback(CallbackData, prefix="start_voting"):
    game_id: str

class MakeDecisionCallback(CallbackData, prefix="decision"):
    game_id: str
    action: MakeDecisionAction