from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from services.tg_bot.app.callbacks.factory import RevealCallback, UseActionCallback, StartVotingCallback, VoteCallback
from services.tg_bot.app.schema import VotingCandidate
from shared.src.enums import AttributeCategory


def start_menu(bot_username: str):
    buttons = [
        [
            InlineKeyboardButton(text="☢️Добавить бота в свой чат", url=f"https://t.me/{bot_username}?startgroup=true"),
        ],
        [
            InlineKeyboardButton(text="Подробнее", callback_data="info_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def info_menu():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="start_menu")]])

def join_button(bot_name, public_id):
    buttons = [
        [
            InlineKeyboardButton(text="Присоединиться к игре", url=f"https://t.me/{bot_name}?start={public_id}"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def reveal_menu(game_id: str):
    buttons = [
        [
            InlineKeyboardButton(text="👥 Открыть биологию", callback_data=RevealCallback(game_id=game_id, attribute=AttributeCategory.BIOLOGY).pack()),
            InlineKeyboardButton(text="❤️ Открыть здоровье", callback_data=RevealCallback(game_id=game_id, attribute=AttributeCategory.HEALTH).pack()),
        ],
        [
            InlineKeyboardButton(text="💼 Открыть профессию", callback_data=RevealCallback(game_id=game_id, attribute=AttributeCategory.PROFESSION).pack()),
            InlineKeyboardButton(text="🎣 Открыть хобби", callback_data=RevealCallback(game_id=game_id, attribute=AttributeCategory.HOBBY).pack()),
        ],
        [
            InlineKeyboardButton(text="😨 Показать фобию", callback_data=RevealCallback(game_id=game_id, attribute=AttributeCategory.PHOBIA).pack()),
            InlineKeyboardButton(text="🎒 Показать багаж", callback_data=RevealCallback(game_id=game_id, attribute=AttributeCategory.ITEM, index=0).pack()),
        ], # Надо генерить багаж, т.к. может быть как 0, так и больше 1
        [
            InlineKeyboardButton(text="📝 Показать факт 1", callback_data=RevealCallback(game_id=game_id, attribute=AttributeCategory.FACT, index=0).pack()),
            InlineKeyboardButton(text="📝 Показать факт 2", callback_data=RevealCallback(game_id=game_id, attribute=AttributeCategory.FACT, index=1).pack()),
        ],
        [
            InlineKeyboardButton(text="🃏 Карта действий 1", callback_data=UseActionCallback(game_id=game_id, index=0).pack()),
            InlineKeyboardButton(text="🃏 Карта действий 2", callback_data=UseActionCallback(game_id=game_id, index=1).pack()),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def start_voting_menu(game_id: str):
    buttons = [
        [
            InlineKeyboardButton(text="Начать голосование", callback_data=StartVotingCallback(game_id=game_id).pack())
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def voting_keyboard(game_id: str, candidates: list[VotingCandidate]):
    sorted_candidates = sorted(candidates, key=lambda x: x.user_id)
    
    buttons = [
        InlineKeyboardButton(
            text=f"{result.name}: {result.votes_count}",
            callback_data=VoteCallback(
                game_id=game_id,
                target_id=result.user_id
            ).pack()
        ) for result in sorted_candidates
    ]

    return InlineKeyboardMarkup(inline_keyboard=[buttons])