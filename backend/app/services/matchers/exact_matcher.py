from typing import Optional

from app.repositories.merchant_repository import MerchantRepository
from app.schemas.transaction import MatchResult
from app.services.matchers.base_matcher import Matcher


class ExactMatcher(Matcher):
    """Level 1: is one of the merchant's known keywords a plain
    substring of the label? Fast and very reliable when it hits, but
    rigid — a single typo means no match at all.
    """

    def __init__(self, repository: MerchantRepository):
        self._repository = repository

    def match(self, libelle_norm: str) -> Optional[MatchResult]:
        for merchant in self._repository.get_all():
            for pattern in merchant.patterns:
                if pattern in libelle_norm:
                    return MatchResult(
                        merchant=merchant.name,
                        category=merchant.category,
                        subcategory=merchant.subcategory,
                        channel=merchant.channel,
                        type=merchant.type,
                        recurring=merchant.recurring,
                        income=merchant.income,
                        # Longer, more specific patterns earn more confidence.
                        confidence=min(95, 60 + len(pattern) * 2),
                        matched_by="exact",
                        pattern=pattern,
                    )
        return None
