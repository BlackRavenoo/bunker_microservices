from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from services.game_service.app.domain.dto import ActionCardDTO
from services.game_service.app.domain.repositories.action_card import ActionCardRepository
from services.game_service.app.infrastructure.db.models import ActionCard


class SQLActionCardRepository(ActionCardRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_random_action_cards(self, count):
        result = await self.session.execute(
            select(ActionCard).order_by(
                func.random()
            ).limit(count)
        )

        cards = result.scalars().all()

        return [
            ActionCardDTO(
                id=card.id,
                action=card.action,
                value=card.value,
                target=card.target,
                info=card.info
            )
            for card
            in cards
        ]

    async def get_card(self, id):
        result = await self.session.execute(
            select(ActionCard).where(
                ActionCard.id == id
            )
        )

        card = result.scalars().one_or_none()

        if card is None:
            return None
        
        return ActionCardDTO(
            id=id,
            action=card.action,
            value=card.value,
            target=card.target,
            info=card.info
        )