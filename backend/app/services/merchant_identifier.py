from typing import List

from app.schemas.transaction import MatchResult
from app.services.matchers.base_matcher import Matcher


class MerchantIdentifier:
    """Runs a chain of matchers in order and returns the first hit.

    This is the Chain of Responsibility pattern: each matcher gets a
    chance to answer, and if it can't, the next one tries. To add a new
    matching technique later, write one new Matcher class and add it to
    the list passed in here — this class and every existing matcher stay
    untouched (Open/Closed principle).
    """

    def __init__(self, matchers: List[Matcher]):
        self._matchers = matchers

    def identify(self, libelle_norm: str) -> MatchResult:
        for matcher in self._matchers:
            result = matcher.match(libelle_norm)
            if result is not None:
                return result

        return MatchResult(
            merchant="Unknown",
            category="Unknown",
            subcategory="Unknown",
            channel="Unknown",
            type="Unknown",
            recurring=False,
            income=False,
            confidence=0,
            matched_by=None,
            pattern=None,
        )
