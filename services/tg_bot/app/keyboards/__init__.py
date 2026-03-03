from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from services.tg_bot.app.callbacks.factory import MakeDecisionCallback, RevealCallback, UseActionCallback, StartVotingCallback, VoteCallback
from services.tg_bot.app.schema import VotingCandidate
from shared.src.enums import AttributeCategory, MakeDecisionAction


def start_menu(bot_username: str) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="☢️Добавить бота в свой чат", url=f"https://t.me/{bot_username}?startgroup=true"),
        ],
        [
            InlineKeyboardButton(text="Подробнее", callback_data="info_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def info_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="start_menu")]])

def join_button(bot_name, public_id) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="Присоединиться к игре", url=f"https://t.me/{bot_name}?start={public_id}"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def reveal_menu(game_id: str) -> InlineKeyboardMarkup:
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
        ], # TODO: Надо генерить багаж, т.к. может быть как 0, так и больше 1
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

def start_voting_menu(game_id: str) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="Начать голосование", callback_data=StartVotingCallback(game_id=game_id).pack())
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def voting_keyboard(game_id: str, candidates: list[VotingCandidate]) -> InlineKeyboardMarkup:
    sorted_candidates = sorted(candidates, key=lambda x: x.user_id)

    buttons_per_row = 2
    rows = []
    for i in range(0, len(sorted_candidates), buttons_per_row):
        row = [
            InlineKeyboardButton(
                text=f"{result.name}: {result.votes_count}",
                callback_data=VoteCallback(
                    game_id=game_id,
                    target_id=result.user_id
                ).pack()
            ) for result in sorted_candidates[i:i + buttons_per_row]
        ]
        rows.append(row)

    return InlineKeyboardMarkup(inline_keyboard=rows)

def revote_decision_keyboard(game_id: str) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(
            text="Пропустить ход",
            callback_data=MakeDecisionCallback(
                game_id=game_id,
                action=MakeDecisionAction.SKIP
            )
        ),
        InlineKeyboardButton(
            text="Провести голосование еще раз",
            callback_data=MakeDecisionCallback(
                game_id=game_id,
                action=MakeDecisionAction.REVOTE
            )
        )
    ]

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [button] for button in buttons
        ]
    )

def tie_decision_keyboard(game_id: str) -> InlineKeyboardMarkup:
    keyboard = revote_decision_keyboard(game_id)

    keyboard.inline_keyboard.append(
        [InlineKeyboardButton(
            text="Кикнуть всех кандидатов",
            callback_data=MakeDecisionCallback(
                game_id=game_id,
                action=MakeDecisionAction.KICK_ALL
            )
        )]
    )

    return keyboard