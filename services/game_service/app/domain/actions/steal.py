from services.game_service.app.domain.actions.base import Action
from shared.src.enums import AttributeCategory

class StealAction(Action):
    def __init__(
        self,
        game_id: str,
        user_id: str,
        target_user_id: str | None,
        category: AttributeCategory,
    ):
        self.game_id = game_id
        self.user_id = user_id
        self.target_user_id = target_user_id
        self.category = category

    async def execute(self, uow):
        uow.characters.swap_attributes(
            user_id=self.user_id,
            target_user_id=self.target_user_id,
            game_id=self.game_id,
            category=self.category
        )
    
    def is_valid(self):
        return self.user_id != self.target_user_id