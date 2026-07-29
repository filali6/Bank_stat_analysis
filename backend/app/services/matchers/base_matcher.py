from abc import ABC, abstractmethod
from typing import Optional

from app.schemas.transaction import MatchResult


class Matcher(ABC):
    """The contract every merchant-matching technique must follow.

    Each matcher tries exactly ONE technique to recognize a merchant from
    an already-normalized label, and returns None when it isn't confident
    enough — which lets the next matcher in the chain take over. Adding a
    new technique later (e.g. a trained ML classifier) means writing one
    new class here and adding it to the chain; nothing else changes.
    """

    @abstractmethod
    def match(self, libelle_norm: str) -> Optional[MatchResult]:
        raise NotImplementedError
