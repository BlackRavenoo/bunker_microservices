from abc import abstractmethod, ABC

from shared.src.enums import AttributeCategory

class AttributeRepository(ABC):
    @abstractmethod
    async def get_random_attributes(
        self,
        categories: list[tuple[AttributeCategory, int]],
        char_count: int
    ) -> dict[AttributeCategory, list]:
        pass