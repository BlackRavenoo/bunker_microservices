from services.game_service.app.domain.actions.base import Action
from services.game_service.app.domain.dto.update import BatchUpdateAttributesDTO
from shared.src.enums import ActionTarget, AttributeCategory

class ChangeAttributeAction(Action):
    def __init__(
        self,
        game_id: str,
        user_id: str,
        target_user_id: str | None,
        target: ActionTarget,
        category: AttributeCategory,
    ):
        self.game_id = game_id
        self.user_id = user_id
        self.target_user_id = target_user_id
        self.target = target
        self.category = category
    
    async def execute(self, uow):
        if self.target_user_id:
            ids = [self.target_user_id]
        else:
            ids = await uow.characters.get_character_ids(self.game_id)

        attrs_dict = await uow.attributes.get_random_attributes(
            categories=[(self.category, 1)],
            char_count=len(ids)
        )

        attrs = attrs_dict[self.category]

        await uow.characters.batch_update_attributes(
            updates=[
                BatchUpdateAttributesDTO(
                    id=id,
                    attributes={
                        self.category: attr
                    }
                )
                for (id, attr)
                in zip(ids, attrs)
            ]
        )

    def is_valid(self):        
        if self.target not in [
            ActionTarget.ALL,
            ActionTarget.ANY,
        ]:
            return False
        
        if self.target == ActionTarget.ANY\
            and self.target_user_id is None:
            return False
        
        if self.target == ActionTarget.ALL\
            and self.target_user_id:
            return False
        
        return True