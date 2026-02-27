from shared.src.enums import AttributeCategory
from shared.src.events import VoteDetail

_category_enum_to_str = {
    AttributeCategory.BIOLOGY: "биологию",
    AttributeCategory.HEALTH: "здоровье",
    AttributeCategory.PROFESSION: "профессию",
    AttributeCategory.HOBBY: "хобби",
    AttributeCategory.PHOBIA: "фобию",
    AttributeCategory.FACT: "факт",
    AttributeCategory.ITEM: "предмет",
}

def is_user_from_tg(user_id: str) -> str | None:
    if user_id.startswith("tg:"):
        return user_id[3:]
    
def get_category_str(cat: AttributeCategory) -> str:
    return _category_enum_to_str[cat]

def get_year_str(n: int):
    last_digit = n % 10
    
    if last_digit == 1:
        return "год"
    elif last_digit in [2, 3, 4]:
        return "года"
    else:
        return "лет"
    
def get_formatted_name(user_id: str, name: str) -> str:
    if user_id := is_user_from_tg(user_id):
        return f'<a href="tg://user?id={user_id}">{name}</a>'
    else:
        return name

def format_candidates_list(candidates: list[VoteDetail]) -> str:
    return "\n".join(
        get_formatted_name(
            user_id=candidate.user_id,
            name=candidate.name
        ) for candidate in candidates
    )