from aiogram import F, Router
from aiogram.types import CallbackQuery

from services.tg_bot.app.callbacks.factory import RevealCallback, StartVotingCallback, VoteCallback, MakeDecisionCallback
from services.tg_bot.app.consts import HELLO_TEXT
from services.tg_bot.app.keyboards import UseActionCallback, info_menu, start_menu
from services.tg_bot.app.services.game import GameService
from shared.src.exceptions import AttributeAlreadyRevealed, InvalidVotingStateError, NoRevealRequired, UserAlreadyKicked, UserAlreadyVoted, VotingAlreadyStarted, VotingTargetNotFound

router = Router()

@router.callback_query(F.data == "info_menu")
async def info_menu_callback(callback: CallbackQuery):
    await callback.bot.edit_message_text(
        text="Some text",
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=info_menu()
    )

@router.callback_query(F.data == "start_menu")
async def start_menu_callback(callback: CallbackQuery):
    await callback.bot.edit_message_text(
        text=HELLO_TEXT,
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=start_menu(callback.bot.username)
    )

@router.callback_query(UseActionCallback.filter())
async def use_action_callback(callback: CallbackQuery, callback_data: UseActionCallback):
    await callback.answer(f"Use action {callback_data.index + 1} clicked in {callback_data.game_id}")

@router.callback_query(RevealCallback.filter())
async def reveal_callback(
    callback: CallbackQuery,
    callback_data: RevealCallback,
    game_service: GameService,
):
    try:
        await game_service.reveal_attribute(
            user_id=callback.from_user.id,
            **callback_data.model_dump()
        )
    except AttributeAlreadyRevealed:
        await callback.answer("Этот атрибут уже открыт!", show_alert=True)
    except NoRevealRequired:
        await callback.answer("Тебе не нужно открывать атрибут в этом раунде!", show_alert=True)

@router.callback_query(StartVotingCallback.filter())
async def start_voting(
    callback: CallbackQuery,
    callback_data: StartVotingCallback,
    game_service: GameService
):
    try:
        await game_service.start_voting(callback_data.game_id)
    except VotingAlreadyStarted:
        await callback.answer("Голосование уже начато!", show_alert=True)

@router.callback_query(VoteCallback.filter())
async def vote(
    callback: CallbackQuery,
    callback_data: VoteCallback,
    game_service: GameService,
):
    try:
        await game_service.vote(
            game_id=callback_data.game_id,
            user_id=callback.from_user.id,
            target_id=callback_data.target_id,
        )
    except UserAlreadyVoted:
        await callback.answer("Вы уже проголосовали!", show_alert=True)
    except VotingTargetNotFound:
        await callback.answer("Цель голосования не найдена.", show_alert=True)
    except UserAlreadyKicked:
        await callback.answer("Вы уже выгнаны.", show_alert=True)

@router.callback_query(MakeDecisionCallback.filter())
async def make_decision(
    callback: CallbackQuery,
    callback_data: MakeDecisionCallback,
    game_service: GameService,
):
    try:
        await game_service.make_decision(
            game_id=callback_data.game_id,
            action=callback_data.action
        )
    except InvalidVotingStateError:
        await callback.answer("Ты не сможешь сделать это в данный момент.", show_alert=True)