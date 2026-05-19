from services.game_service.app.domain.actions.base import Action
from shared.src.enums import ActionTarget, AttributeCategory

class RevealAction(Action):
    def __init__(
        self,
        game_id: str,
        user_id: str,
        target_user_id: str,
        target: ActionTarget,
        category: AttributeCategory,
    ):
        self.game_id = game_id
        self.user_id = user_id
        self.target_user_id = target_user_id
        self.target = target
        self.category = category

    async def execute(self, uow):
        uow.characters.reveal_attribute(
            game_id=self.game_id,
            user_id=self.target_user_id,
            attribute=self.category
        )

    def is_valid(self):
        if self.target in [ActionTarget.ALL, ActionTarget.NONE]:
            return False
        
        if self.target == ActionTarget.NOT_SELF:
            return self.user_id == self.target_user_id
        
        return True