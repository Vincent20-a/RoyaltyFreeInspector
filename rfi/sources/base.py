from abc import ABC, abstractmethod

from ..models import ContentItem


class Source(ABC):
    """Interfaccia comune: per aggiungere Pixabay, Pexels ecc. basta una nuova sottoclasse."""

    name: str = ""
    media_types: tuple = ()

    @abstractmethod
    def search(self, query: str, media_type: str, limit: int = 20) -> list[ContentItem]:
        ...
