from aiogram import F, Router, types
from aiogram.enums import ChatType
from aiogram.filters import Command, CommandObject

from services.tg_bot.app.consts import HELLO_TEXT, PRIVATE_CHAT_MESSAGE
from services.tg_bot.app.keyboards import join_button, start_menu
from services.tg_bot.app.schema import TelegramUser
from services.tg_bot.app.services.game import GameService
from shared.src.exceptions import EntityAlreadyExists, EntityNotFound, GameAlreadyStarted

router = Router(name="game")

@router.message(Command("start"), F.chat.type == ChatType.PRIVATE)
async def start_handler(
    message: types.Message,
    command: CommandObject,
    game_service: GameService
):
    if command.args is None:
        await message.answer(HELLO_TEXT, reply_markup=start_menu(message.bot.username))
    else:
        user = TelegramUser(
            _id=message.from_user.id,
            name=message.from_user.full_name
        )
        
        try:
            await game_service.join_game(
                user=user,
                game_id=command.args
            )
        except EntityNotFound:
            await message.reply("Игра не найдена")
        except EntityAlreadyExists:
            await message.reply("Вы уже в игре.")

@router.message(F.chat.type != ChatType.GROUP, F.chat.type != ChatType.SUPERGROUP)
async def private_chat_handler(message: types.Message):
    await message.reply(PRIVATE_CHAT_MESSAGE)

@router.message(Command("game"))
async def create_game(
    message: types.Message,
    game_service: GameService
):
    user = TelegramUser(
        _id=message.from_user.id,
        name=message.from_user.full_name
    )
    try:
        game_id = await game_service.create_game(
            user=user,
            chat_id=message.chat.id
        )

        text=f"🎮 Новая игра создана!\n\n" \
                f"🔑 Код игры: {game_id}"
        
        message = await message.answer(text, reply_markup=join_button(message.bot.username, game_id))
    except EntityAlreadyExists:
        await message.answer("Игра в этом чате уже существует!")

@router.message(Command("start"))
async def start_game(
    message: types.Message,
    game_service: GameService
):
    try:
        await game_service.start_game(message.chat.id)
    except GameAlreadyStarted:
        await message.answer("Игра уже началась!")