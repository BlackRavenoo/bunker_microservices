from services.game_service.app.domain.actions.base import Action

class ChangeCatastropheAction(Action):
    def __init__(self, game_id: str):
        self.game_id = game_id

    async def execute(self, uow):
        await uow.games.generate_catastrophe(
            game_id=self.game_id
        )
    
    def is_valid(self):
        return True