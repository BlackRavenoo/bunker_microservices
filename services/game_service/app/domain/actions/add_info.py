from services.game_service.app.domain.actions.change_attribute import Action


class AddInfoAction(Action):
    def __init__(
        self,
        game_id: str
    ):
        self.game_id = game_id

    async def execute(self, uow):
        uow.games.add_bunker_elements(
            
        )

    def is_valid(self):
        return True