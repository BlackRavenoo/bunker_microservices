from aiogram import Bot
from faststream import AckPolicy
from faststream.rabbit import RabbitBroker, RabbitQueue

from services.tg_bot.app.keyboards import reveal_menu, start_voting_menu, voting_keyboard
from services.tg_bot.app.messaging.broker import exchange
from services.tg_bot.app.schema import VotingCandidate
from services.tg_bot.app.services.game import GameService
from services.tg_bot.app.utils import format_candidates_list, get_category_str, get_formatted_name, get_year_str, is_user_from_tg
from shared.src.enums import Gender, VotingResult
from shared.src.events import ATTRIBUTE_REVEALED, GAME_ENDED, GAME_STARTED, PLAYER_JOINED, PLAYER_VOTED, ROUND_STARTED, VOTING_ENDED, VOTING_STARTED, AttributeRevealed, GameEnded, GameStarted, NewRoundStarted, PlayerJoined, PlayerVoted, VotingEnded, VotingStarted

def register_event_handlers(broker: RabbitBroker, bot: Bot, game_service: GameService):
    @broker.subscriber(
        RabbitQueue(PLAYER_JOINED, durable=True),
        exchange,
        ack_policy=AckPolicy.NACK_ON_ERROR
    )
    async def player_joined(event: PlayerJoined):
        game = await game_service.get_game(event.game_id)

        if not game:
            return
        
        chat_id = game.chat_id

        name = get_formatted_name(
            user_id=event.user_id,
            name=event.name
        )

        await bot.send_message(
            chat_id=chat_id,
            text=f"К игре присоединился {name}"
        )

    @broker.subscriber(
        RabbitQueue(GAME_STARTED, durable=True),
        exchange,
        ack_policy=AckPolicy.NACK_ON_ERROR
    )
    async def game_started(event: GameStarted):
        game = await game_service.get_game(event.game_id)

        if not game:
            return
        
        chat_id = game.chat_id

        for char in event.game.characters:
            if user_id := is_user_from_tg(char.user_id):
                await bot.send_message(
                    chat_id=user_id,
                    text="Ваш персонаж:\n\n" \
                        f"👥 Биология: {char.biology.value[1]}, {char.biology.value[0]}\n" \
                        f"❤️ Здоровье: {char.health.value}\n" \
                        f"💼 Профессия: {char.profession.value}\n" \
                        f"🎣 Хобби: {char.hobby.value}\n" \
                        f"😨 Фобия: {char.phobia.value}\n" \
                        f"📝 Факт 1: {char.facts[0].value}\n" \
                        f"📝 Факт 2: {char.facts[1].value}\n" \
                        f"🎒 Багаж: {char.items[0].value}\n\n",
                        # f"🃏 Карта действий 1: {char.actions[0].description}\n" \
                        # f"🃏 Карта действий 2: {char.actions[1].description}\n",
                    reply_markup=reveal_menu(game_id=event.game_id)
                )

        if chat_id is not None:
            text = f"""
Игра началась!

🔥 Катастрофа: {event.game.catastrophe.name}
Описание: {event.game.catastrophe.description}

🏠 Бункер расчитан на {event.game.bunker.places_count}.
Комнаты в бункере:
{", ".join(event.game.bunker.rooms)}
Предметы в бункере:
{", ".join(event.game.bunker.items)}"""


            await bot.send_message(
                chat_id=chat_id,
                text=text
            )

    @broker.subscriber(
        RabbitQueue(ATTRIBUTE_REVEALED, durable=True),
        exchange,
        ack_policy=AckPolicy.NACK_ON_ERROR
    )
    async def attribute_revealed(event: AttributeRevealed):
        game = await game_service.get_game(event.game_id)

        if not game:
            return

        chat_id = game.chat_id

        name = get_formatted_name(
            user_id=event.user_id,
            name=event.name
        )

        category_str = get_category_str(event.category) 

        if isinstance(event.value, list):
            gender = Gender(event.value[1])
            year_str = get_year_str(event.value[0])
            value = f"{gender}, {event.value[0]} {year_str}"
        else:
            value = event.value

        await bot.send_message(
            chat_id=chat_id,
            text=f"{name} открыл {category_str} - {value}"
        )

        if event.is_all_revealed:
            await bot.send_message(
                chat_id=chat_id,
                text="Все игроки открыли характерики.\n" \
                "Можете обсудить все и приступить к голосованию.",
                reply_markup=start_voting_menu(game_id=event.game_id)
            )

    @broker.subscriber(
        RabbitQueue(VOTING_STARTED, durable=True),
        exchange,
        ack_policy=AckPolicy.NACK_ON_ERROR
    )
    async def voting_started(event: VotingStarted):
        game = await game_service.get_game(event.game_id)

        if not game:
            return
        
        chat_id = game.chat_id

        characters_message = ""

        for i, character in enumerate(event.characters):
            name = get_formatted_name(
                user_id=character.user_id,
                name=character.username
            )

            message_part = f"{i + 1}. {name}:\n<code>"

            if character.biology.is_revealed:
                gender = Gender(character.biology.value[1])
                year_str = get_year_str(character.biology.value[0])
                message_part += f"Биология: {gender}, {character.biology.value[0]} {year_str}\n"
            
            mappings = {
                "Здоровье": character.health,
                "Профессия": character.profession,
                "Хобби": character.hobby,
                "Фобия": character.phobia,
            }

            for name, attr in mappings.items():
                if attr.is_revealed:
                    message_part += f"{name}: {attr.value}\n"

            for i, fact in enumerate(character.facts):
                if fact.is_revealed:
                    message_part += f"Факт №{i + 1}: {fact.value}\n"

            revealed_items = [item.value for item in character.items if item.is_revealed]

            if len(revealed_items) > 0:
                message_part += f"Багаж: {", ".join(revealed_items)}"
                
            message_part += "</code>"

            if len(characters_message) + len(message_part) < 4096:
                characters_message += message_part + "\n"
            else:
                await bot.send_message(
                    chat_id=chat_id,
                    text=characters_message
                )

                if len(message_part) < 4096:
                    characters_message = message_part
                else:
                    # TODO: log this and better do something to fix
                    await bot.send_message(
                        chat_id=chat_id,
                        text=f"Произошла ошибка при отображении карточки игрока {name}"
                    )
                    characters_message = ""

        if 0 < len(characters_message) < 4096:
            await bot.send_message(
                chat_id=chat_id,
                text=characters_message
            )

        candidates = [
            VotingCandidate(
                name=char.username,
                user_id=char.user_id,
                votes_count=0
            ) for char in event.characters
        ]

        message = await bot.send_message(
            chat_id=chat_id,
            text="Голосование началось.\n\n" \
                "Выберите игрока, которого хотите выгнать из игры.\n",
            reply_markup=voting_keyboard(
                game_id=event.game_id,
                candidates=candidates
            )
        )

        await game_service.update_message_id(
            chat_id=chat_id,
            message_id=message.message_id
        )

    @broker.subscriber(
        RabbitQueue(PLAYER_VOTED, durable=True),
        exchange,
        ack_policy=AckPolicy.NACK_ON_ERROR
    )
    async def player_voted(
        event: PlayerVoted
    ):
        game = await game_service.get_game(
            game_id=event.game_id
        )

        if not game:
            return

        candidates = [
            VotingCandidate(
                name=result.name,
                user_id=result.user_id,
                votes_count=result.votes_count
            ) for result in event.vote_details
        ]

        await bot.edit_message_reply_markup(
            chat_id=game.chat_id,
            message_id=game.message_id,
            reply_markup=voting_keyboard(
                game_id=game.game_id,
                candidates=candidates
            )
        )

    @broker.subscriber(
        RabbitQueue(VOTING_ENDED, durable=True),
        exchange,
        ack_policy=AckPolicy.NACK_ON_ERROR
    )
    async def voting_ended(
        event: VotingEnded
    ):
        game = await game_service.get_game(
            game_id=event.game_id
        )

        if not game:
            return
        
        all_details = sorted(event.candidates_for_kick + event.remaining_members, key=lambda x: -x.votes_count)

        voting_result_message = "\n".join(
            get_formatted_name(
                user_id=detail.user_id,
                name=detail.name
            ) + f": {detail.votes_count}" for detail in all_details
        )

        await bot.send_message(
            chat_id=game.chat_id,
            text=f"Результаты голосования:\n {voting_result_message}"
        )

        match event.voting_result:
            case VotingResult.KICK:
                if len(event.candidates_for_kick) == 1:
                    candidate = event.candidates_for_kick[0]

                    name = get_formatted_name(
                        user_id=candidate.user_id,
                        name=candidate.name
                    )
                    
                    await bot.send_message(
                        chat_id=game.chat_id,
                        text=f"Игрок {name} был кикнут по итогам голосования."
                    )
                else:
                    message = format_candidates_list(event.candidates_for_kick)

                    await bot.send_message(
                        chat_id=game.chat_id,
                        text=f"По итогам голосования были кикнуты игроки:\n{message}"
                    )
            case VotingResult.KICK_AND_REVOTE:
                candidate = event.candidates_for_kick[0]

                name = get_formatted_name(
                    user_id=candidate.user_id,
                    name=candidate.name
                )
                
                message = await bot.send_message(
                    chat_id=game.chat_id,
                    text=f"Игрок {name} был кикнут по итогам голосования.\n"
                        "Было кикнуто недостаточно игроков, поэтому голосование начнется опять.",
                    reply_markup=voting_keyboard(
                        game_id=event.game_id,
                        candidates=event.remaining_members
                    )
                )

                await game_service.update_message_id(
                    chat_id=game.chat_id,
                    message_id=message.message_id
                )
            case VotingResult.TIE_DECISION:
                await bot.send_message(
                    chat_id=game.chat_id,
                    text="Есть игроки, имеющие равное количество голосов.\n"
                        "Вы можете кикнуть их сразу, провести новое голосование "
                        "среди них или пропустить его.\n"
                )
            case VotingResult.REVOTE_DECISION:
                await bot.send_message(
                    chat_id=game.chat_id,
                    text="Есть игроки, имеющие равное количество голосов.\n"
                        "Вы можете провести новое голосование "
                        "среди них или пропустить его.\n"
                )
            case VotingResult.REVOTE:
                message = await bot.send_message(
                    chat_id=game.chat_id,
                    text="По итогам голосования никто не был кикнут.\n"
                        "Будет проведено повторное голосование.",
                    reply_markup=voting_keyboard(
                        game_id=event.game_id,
                        candidates=event.candidates_for_kick
                    )
                )

                await game_service.update_message_id(
                    chat_id=game.chat_id,
                    message_id=message.message_id
                )
        
        await bot.delete_message(
            chat_id=game.chat_id,
            message_id=game.message_id
        )

    @broker.subscriber(
        RabbitQueue(ROUND_STARTED, durable=True),
        exchange,
        ack_policy=AckPolicy.NACK_ON_ERROR
    )
    async def new_round_started(
        event: NewRoundStarted
    ):
        game = await game_service.get_game(
            game_id=event.game_id
        )

        if not game:
            return
        
        await bot.send_message(
            chat_id=game.chat_id,
            text=f"Начался новый раунд. В нем необходимо кикнуть {event.count_to_kick} игрока."
                "Можете начать вскрывать характеристики."
        )

    @broker.subscriber(
        RabbitQueue(GAME_ENDED, durable=True),
        exchange,
        ack_policy=AckPolicy.NACK_ON_ERROR
    )
    async def game_ended(
        event: GameEnded
    ):
        game = await game_service.get_game(
            game_id=event.game_id
        )

        if not game:
            return
        
        await bot.send_message(
            chat_id=game.chat_id,
            text="Игра закончена."
        )

        await game_service.delete_game(
            game_id=game.game_id
        )