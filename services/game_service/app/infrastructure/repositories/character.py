from typing import Any
from sqlalchemy import cast, func, insert, select, update, case, not_
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from services.game_service.app.domain.dto import UserAttributeDTO, CharacterDTO, CharacterWithoutAttrs
from services.game_service.app.domain.dto.update import NullableFieldUpdate
from services.game_service.app.domain.repositories.character import CharacterRepository
from services.game_service.app.infrastructure.db.models import Character
from shared.src.enums import AttributeCategory, CharacterStatus
from shared.src.exceptions import AttributeAlreadyRevealed, EntityAlreadyExists, EntityNotFound, NoRevealRequired, UnexpectedException

class SQLCharacterRepository(CharacterRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _fetch_characters(self, game_id: str, exсlude_kicked: bool = False) -> list[CharacterDTO]:
        characters_query = select(
            Character.id,
            Character.user_id,
            Character.name,
            (Character.status == CharacterStatus.Kicked).label('is_kicked'),
            Character.attributes
        )\
        .select_from(Character)\
        .where(Character.game_id == game_id)

        if exсlude_kicked:
            characters_query = characters_query.where(
                Character.status != CharacterStatus.Kicked
            )

        result = await self.session.execute(characters_query)

        characters_rows = result.all()

        characters_data = []
        for row in characters_rows:
            char = CharacterDTO(
                id=row.id,
                user_id=row.user_id,
                is_kicked=row.is_kicked,
                username=row.name,
                biology=UserAttributeDTO(**row.attributes["biology"]),
                health=UserAttributeDTO(**row.attributes["health"]),
                profession=UserAttributeDTO(**row.attributes["profession"]),
                hobby=UserAttributeDTO(**row.attributes["hobby"]),
                phobia=UserAttributeDTO(**row.attributes["phobia"]),
                facts=[UserAttributeDTO(**fact) for fact in row.attributes["facts"]],
                items=[UserAttributeDTO(**item) for item in row.attributes["items"]],
            )

            characters_data.append(char)

        return characters_data

    async def add_character(self, game_id: str, user_id: str, name: str):
        try:
            await self.session.execute(
                insert(Character).values(
                    game_id=game_id,
                    user_id=user_id,
                    name=name
                )
            )
        except IntegrityError:
            raise EntityAlreadyExists
        
    async def get_character_ids(self, game_id):
        character_ids = (await self.session.execute(
            select(Character.id)
                .where(Character.game_id == game_id)
                .order_by(Character.id)
        )).scalars().all()

        return [id for id in character_ids]
    
    async def update_characters(self, updates):
        await self.session.execute(
            update(Character),
            [
                update.model_dump(exclude_unset=True)
                for update in updates
            ]
        )

    async def update_active_characters_by_game_id(self, game_id, updates):
        values = {}

        for name, field in updates:
            if field is None:
                continue

            if isinstance(field, NullableFieldUpdate):
                values[name] = field.value
            else:
                values[name] = field
        
        await self.session.execute(
            update(Character)
            .where(
                Character.game_id == game_id,
                Character.status != CharacterStatus.Kicked    
            )
            .values(**values)
        )
        
    async def reveal_attribute(self, game_id: str, user_id: str, attribute: AttributeCategory, index: int | None) -> Any:
        if index is not None:
            attribute = attribute + 's'
            path = [attribute, str(index), "is_revealed"]
            value_expr = Character.attributes[attribute][index]["value"]
            where_condition = Character.attributes[attribute][index]["is_revealed"].as_boolean() == False # noqa: E712
        else:
            path = [attribute, "is_revealed"]
            value_expr = Character.attributes[attribute]["value"]
            where_condition = Character.attributes[attribute]["is_revealed"].as_boolean() == False # noqa: E712
        
        result = await self.session.scalar(
            update(Character)
            .where(
                Character.game_id == game_id,
                Character.user_id == user_id,
                Character.needs_to_reveal,
                where_condition
            )
            .values(
                attributes=func.jsonb_set(
                    Character.attributes,
                    path,
                    cast(True, JSONB)
                ),
                needs_to_reveal=False
            )
            .returning(value_expr)
        )

        if result is not None:
            return result

        check = await self.session.execute(
            select(
                Character.needs_to_reveal,
                case(
                    (where_condition, False),
                    else_=True
                ).label("is_already_revealed")
            ).where(
                Character.game_id == game_id,
                Character.user_id == user_id
            )
        )

        row = check.first()
        if row is None:
            raise EntityNotFound("Character not found")
        
        needs_to_reveal, is_already_revealed = row

        if not needs_to_reveal:
            raise NoRevealRequired()
        elif is_already_revealed:
            raise AttributeAlreadyRevealed()
        else:
            raise UnexpectedException()
    
    async def get_characters_without_attrs(self, game_id, user_ids):
        rows = await self.session.execute(
            select(
                Character.id,
                Character.user_id,
                Character.name,
                Character.voted_for,
                (Character.status == CharacterStatus.Kicked).label("is_kicked")
            ).where(
                Character.game_id == game_id,
                Character.user_id.in_(user_ids)
            )
        )

        by_user_id = {
            row.user_id: CharacterWithoutAttrs(
                id=row.id,
                user_id=row.user_id,
                username=row.name,
                is_kicked=row.is_kicked,
                voted_for=row.voted_for
            ) for row in rows
        }

        return [by_user_id[uid] for uid in user_ids]
        
    async def is_all_revealed(self, game_id: str) -> bool | None:
        res = await self.session.scalar(
            select(
                func.every(not_(Character.needs_to_reveal)).label("is_all_revealed")
            ).where(
                Character.game_id == game_id
            )
        )

        return res
    
    async def get_characters(self, game_id) -> list[CharacterDTO]:
        return await self._fetch_characters(game_id)
    
    async def get_active_characters(self, game_id) -> list[CharacterDTO]:
        return await self._fetch_characters(game_id, exсlude_kicked=True)

    async def vote(self, game_id, user_id, target_id):
        query = update(Character).where(
            Character.user_id == user_id,
            Character.game_id == game_id
        ).values(
            voted_for=target_id
        )

        await self.session.execute(query)