import random
from services.game_service.app.domain.dto.update import CharacterAttributes, CharacterBatchUpdateDTO
from services.game_service.app.domain.uow import UnitOfWork
from services.game_service.app.infrastructure.messaging.rabbitmq import GamePublisher
from shared.src.events import Game, GameStarted
from shared.src.schemas.character import AttributeCategory


class GameService:
    def __init__(self, uow: UnitOfWork, publisher: GamePublisher):
        self.uow = uow
        self.publisher = publisher

    def _build_character_attributes(
        self,
        character_ids: list[int],
        attrs_by_category: dict[AttributeCategory, list],
        categories: list[tuple[AttributeCategory, int]]
    ) -> list[dict]:
        characters_updates = []
        for i, character_id in enumerate(character_ids):
            attributes = {}
            
            for category, count in categories:
                attrs = attrs_by_category[category]
                
                if category == AttributeCategory.FACT:
                    attributes["facts"] = [
                        {"value": attrs[i * 2], "is_revealed": False},
                        {"value": attrs[i * 2 + 1], "is_revealed": False}
                    ]
                elif category == AttributeCategory.ITEM:
                    attributes["items"] = [
                        {"value": attrs[i], "is_revealed": False}
                    ]
                else:
                    attr_name = category.value.lower()
                    attributes[attr_name] = {
                        "value": attrs[i],
                        "is_revealed": False
                    }
            
            age = random.randint(18, 99)
            gender = random.choice(["male", "female"])
            
            attributes["biology"] = {"value": (age, gender), "is_revealed": False}
            
            characters_updates.append(CharacterBatchUpdateDTO(
                id=character_id,
                attributes=CharacterAttributes(**attributes)
            ))

        return characters_updates

    async def create_game(self, host_id: str) -> str:
        async with self.uow as uow:
            game_id: str = await uow.games.create_game(host_id=host_id)

            await uow.commit()

        return game_id
    
    async def start_game(self, game_id: str):
        async with self.uow as uow:
            character_ids = await uow.characters.get_character_ids(
                game_id=game_id
            )

            char_count = len(character_ids)

            categories = [
                (AttributeCategory.HEALTH, 1),
                (AttributeCategory.PROFESSION, 1),
                (AttributeCategory.HOBBY, 1),
                (AttributeCategory.PHOBIA, 1),
                (AttributeCategory.FACT, 2),
                (AttributeCategory.ITEM, 1),
            ]

            attrs_by_category = await uow.attributes.get_random_attributes(
                categories=categories,
                char_count=char_count
            )

            characters_updates = self._build_character_attributes(
                character_ids,
                attrs_by_category,
                categories
            )

            await uow.characters.update_characters(
                updates=characters_updates
            )

            await uow.games.start_game(game_id)

            await uow.commit()

            game_result = await uow.games.get_game(game_id)

            chars_result = await uow.characters.get_characters(game_id)

        await self.publisher.publish(GameStarted(
            game_id=game_id,
            game=Game(
                characters=[char.into_shared() for char in chars_result],
                catastrophe=game_result["catastrophe"],
                bunker=game_result["bunker"]
            )
        ))
            