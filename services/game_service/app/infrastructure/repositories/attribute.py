from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from services.game_service.app.domain.repositories.attribute import AttributeRepository
from services.game_service.app.infrastructure.db.models import Attribute

class SQLAttributeRepository(AttributeRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_random_attributes(self, categories, char_count):
        subqueries = []
        
        for category, count in categories:
            limited_subq = (
                select(Attribute.value)
                .where(Attribute.category == category)
                .order_by(func.random())
                .limit(count * char_count)
            ).subquery()
            
            subq = (
                select(
                    func.array_agg(limited_subq.c.value.label(category.value))
                )
            ).scalar_subquery()
            
            subqueries.append(subq)

        result = (await self.session.execute(
            select(*subqueries)
        )).one()

        attrs_by_category = {
            category: result[i]
            for i, (category, _) in enumerate(categories)
        }

        return attrs_by_category