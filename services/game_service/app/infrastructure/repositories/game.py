from sqlalchemy import ScalarSelect, insert, literal, text, union_all, update, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from services.game_service.app.domain.dto import VotingParticipant, VotingMetadata
from services.game_service.app.domain.dto.update import NumericFieldUpdate, NumericOperation
from services.game_service.app.domain.repositories.game import GameRepository
from services.game_service.app.infrastructure.db.models import BunkerElement, Catastrophe, Character, Game, GameBunkerElement
from shared.src.enums import BunkerElementType, CharacterStatus, GameStatus
from shared.src.exceptions import EntityNotFound, GameAlreadyStarted, VotingAlreadyStarted

class SQLGameRepository(GameRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _random_catastrophe_subquery(self) -> ScalarSelect[int]:
        return select(Catastrophe.id).where(
            Catastrophe.is_active
        ).order_by(func.random()).limit(1).scalar_subquery()

    async def create_game(self, host_id: str) -> str:
        result = await self.session.execute(
            insert(Game).values(
                host_id=host_id,
            )
            .returning(Game.id)
        )

        game_id = result.scalar_one()

        return game_id
    
    async def start_game(self, game_id: str):
        subquery = self._random_catastrophe_subquery()

        places_subquery = (
            select(func.count(Character.id) / 2)
            .where(Character.game_id == game_id)
            .scalar_subquery()
        )

        res = await self.session.execute(
            update(Game).where(
                Game.id == game_id,
                Game.status == GameStatus.BeforeStart
            ).values(
                catastrophe_id=subquery,
                status=GameStatus.Discussion,
                places_count=places_subquery
            )
        )

        if res.rowcount == 0:
            raise GameAlreadyStarted()

        items_subq = (
            select(BunkerElement.id)
            .where(BunkerElement.category == BunkerElementType.ITEM)
            .order_by(func.random())
            .limit(2)
        )

        rooms_subq = (
            select(BunkerElement.id)
            .where(BunkerElement.category == BunkerElementType.ROOM)
            .order_by(func.random())
            .limit(2)
        )

        combined_subq = union_all(items_subq, rooms_subq).subquery()

        await self.session.execute(
            insert(GameBunkerElement).from_select(
                ["game_id", "bunker_element_id"],
                select(literal(game_id), combined_subq.c.id)
            )
        )
    
    async def get_game(self, game_id: str): # TODO: указать тип
        game_query = select(
            func.json_build_object(
                "name", Catastrophe.name,
                "description", Catastrophe.description
            ).label('catastrophe'),
            func.json_build_object(
                "items", func.coalesce(
                    func.json_agg(
                        BunkerElement.value
                    ).filter(BunkerElement.category == BunkerElementType.ITEM),
                    text("'[]'::json")
                ),
                "rooms", func.coalesce(
                    func.json_agg(
                        BunkerElement.value
                    ).filter(BunkerElement.category == BunkerElementType.ROOM),
                    text("'[]'::json")
                ),
                "info", func.coalesce(
                    func.json_agg(
                        BunkerElement.value
                    ).filter(BunkerElement.category == BunkerElementType.INFO),
                    text("'[]'::json")
                ),
                "places_count", Game.places_count
            ).label("bunker")
        )\
        .select_from(Game)\
        .outerjoin(Catastrophe)\
        .outerjoin(GameBunkerElement)\
        .outerjoin(BunkerElement)\
        .where(Game.id == game_id)\
        .group_by(Game.id, Catastrophe.id)

        result = await self.session.execute(game_query)

        game_data = result.one()

        return {
            "catastrophe": game_data.catastrophe,
            "bunker": game_data.bunker,
        }

    async def generate_catastrophe(self, game_id: str):
        subquery = self._random_catastrophe_subquery()

        await self.session.execute(
            update(Game).where(
                Game.id == game_id
            ).values(catastrophe_id=subquery)
        )

    async def start_voting(self, game_id: str):
        select_query = select(
            Game.status
        ).where(
            Game.id == game_id
        )

        status = await self.session.scalar(select_query)
        
        if status is None:
            raise EntityNotFound()
        elif status != GameStatus.Discussion:
            raise VotingAlreadyStarted()

        await self.session.execute(
            update(Game).where(
                Game.id == game_id
            ).values(status=GameStatus.Voting)
        )

    async def get_voting_participants(self, game_id: str):
        inner_char = aliased(Character)
        
        votes_subquery = (
            select(func.count())
            .select_from(inner_char)
            .where(inner_char.voted_for == Character.id)
            .correlate(Character)
            .scalar_subquery()
        )
        
        query = select(
            Character.id,
            Character.user_id,
            Character.name,
            votes_subquery.label("votes_count"),
            Character.voted_for.is_not(None).label("is_voted")
        ).where(
            Character.game_id == game_id,
            Character.status != CharacterStatus.Kicked
        )
        
        rows = await self.session.execute(query)

        results = [
            VotingParticipant(**row._mapping)
            for row in rows
        ]

        return results
    
    async def get_voting_metadata(self, game_id):
        query = select(
            Game.count_to_kick,
            Game.places_count,
            Game.force_voting
        ).where(
            Game.id == game_id
        )

        res = (await self.session.execute(query)).one()

        return VotingMetadata(
            count_to_kick=res.count_to_kick,
            places_count=res.places_count,
            force_voting=res.force_voting
        )

    async def update_game(self, game_id, update_data):
        set_fields = {}

        for name, field in update_data:
            if field is None:
                continue

            if isinstance(field, NumericFieldUpdate):
                if field.operation == NumericOperation.SET:
                    set_fields[name] = field.value
                elif field.operation in (NumericOperation.INCREMENT, NumericOperation.DECREMENT):
                    col = getattr(Game, name)
                    sign = 1 if field.operation == NumericOperation.INCREMENT else -1
                    set_fields[name] = col + (field.value * sign)
            else:
                set_fields[name] = field

        await self.session.execute(
            update(Game).where(
                Game.id == game_id
            ).values(
                **set_fields
            )
        )