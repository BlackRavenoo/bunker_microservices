from services.game_service.app.domain.actions.add_info import AddInfoAction
from services.game_service.app.domain.actions.base import Action
from services.game_service.app.domain.actions.change_attribute import ChangeAttributeAction
from services.game_service.app.domain.actions.change_catastrophe import ChangeCatastropheAction
from services.game_service.app.domain.actions.reveal import RevealAction
from services.game_service.app.domain.actions.steal import StealAction
from services.game_service.app.domain.dto import ActionCardDTO
from shared.src.enums import ActionType, ActionValue


def create_action(cls, card: ActionCardDTO, game_id: str, user_id: str, target_user_id: str | None) -> Action:
    match card.action:
        case ActionType.CHANGE if card.value == ActionValue.CATASTROPHE:
            return ChangeCatastropheAction(
                game_id=game_id
            )
        case ActionType.CHANGE:
            return ChangeAttributeAction(
                game_id=game_id,
                user_id=user_id,
                target_user_id=target_user_id,
                target=card.target,
                category=card.value.into_category()
            )
        case ActionType.STEAL:
            return StealAction(
                game_id=game_id,
                user_id=user_id,
                target_user_id=target_user_id,
                category=card.value.into_category()
            )
        case ActionType.REVEAL:
            return RevealAction(
                game_id=game_id,
                user_id=user_id,
                target_user_id=target_user_id,
                target=card.target,
                category=card.value.into_category()
            )
        case ActionType.INFO:
            return AddInfoAction(
                game_id=game_id
            )
        
    raise ValueError(f"Unknown type of action: {card.action} {card.value} {card.target}")