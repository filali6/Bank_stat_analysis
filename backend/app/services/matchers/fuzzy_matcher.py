from typing import Optional

from rapidfuzz import fuzz

from app.repositories.merchant_repository import MerchantRepository
from app.schemas.transaction import MatchResult
from app.services.matchers.base_matcher import Matcher


class FuzzyMatcher(Matcher):
    """Level 2: tolerant to typos and truncated labels (e.g. "NTFLX"
    instead of "NETFLIX"). Only runs when ExactMatcher has already
    failed — it's slower since it compares against every known pattern.
    """

    def __init__(self, repository: MerchantRepository, threshold: int = 80):
        self._repository = repository
        self._threshold = threshold

    def match(self, libelle_norm: str) -> Optional[MatchResult]:
        best_score = 0
        best_merchant = None
        best_pattern = None

        for merchant in self._repository.get_all():
            for pattern in merchant.patterns:
                score = fuzz.partial_ratio(pattern, libelle_norm)
                if score > best_score:
                    best_score = score
                    best_merchant = merchant
                    best_pattern = pattern

        if best_merchant is None or best_score < self._threshold:
            return None

        return MatchResult(
            merchant=best_merchant.name,
            category=best_merchant.category,
            subcategory=best_merchant.subcategory,
            channel=best_merchant.channel,
            type=best_merchant.type,
            recurring=best_merchant.recurring,
            income=best_merchant.income,
            # A fuzzy hit is always trusted a bit less than an exact one,
            # even at an equal raw score.
            confidence=int(best_score * 0.85),
            matched_by="fuzzy",
            pattern=best_pattern,
        )
