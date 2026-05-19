from services.game_service.app.domain.actions.factory import create_action
from services.game_service.app.domain.dto import CharacterWithoutAttrs
from services.game_service.app.domain.uow import UnitOfWork
from services.game_service.app.infrastructure.messaging.rabbitmq import GamePublisher
from shared.src.enums import AttributeCategory
from shared.src.events import ActionCardUsed, AttributeRevealed, PlayerJoined, User
from shared.src.exceptions import InvalidAction


class CharacterService:
    def __init__(self, uow: UnitOfWork, publisher: GamePublisher):
        self.uow = uow
        self.publisher = publisher

    async def add_character(self, game_id: str, user_id: str, name: str):
        async with self.uow as uow:
            await uow.characters.add_character(
                game_id=game_id,
                user_id=user_id,
                name=name
            )

            await uow.commit()
        
        await self.publisher.publish(
            PlayerJoined(
                game_id=game_id,
                user=User(
                    user_id=user_id,
                    name=name
                )
            )
        )

    async def reveal_attribute(self, game_id: str, user_id: str, attribute: AttributeCategory, index: int | None):
        async with self.uow as uow:
            value = await uow.characters.reveal_attribute(
                game_id,
                user_id,
                attribute,
                index
            )

            char: CharacterWithoutAttrs = (await uow.characters.get_characters_without_attrs(
                game_id=game_id,
                user_ids=[user_id]
            ))[0]

            is_all_revealed = await uow.characters.is_all_revealed(game_id=game_id)

            await uow.commit()

        await self.publisher.publish(
            AttributeRevealed(
                game_id=game_id,
                user=User(
                    user_id=user_id,
                    name=char.username
                ),
                value=value,
                is_all_revealed=is_all_revealed,
                category=attribute
            )
        )

    async def use_action_card(
        self,
        game_id: str,
        user_id: str,
        card_id: int,
        target_user_id: str | None
    ):
        async with self.uow as uow:
            card = await uow.action_cards.get_card(
                id = card_id
            )

            action = create_action(
                card=card,
                game_id=game_id,
                user_id=user_id,
                target_user_id=target_user_id
            )

            if not action.is_valid():
                raise InvalidAction()

            await action.execute(uow)

            users = await uow.characters.get_characters_without_attrs(
                game_id=game_id,
                user_ids=[user_id, target_user_id]
            )

            await uow.commit()

        users = [
            User(
                user_id=user.user_id,
                name=user.username
            ) if user else None
            for user
            in users
        ]

        await self.publisher.publish(
            ActionCardUsed(
                game_id=game_id,
                user=users[0],
                target=users[1],
                action_card=card
            )
        )