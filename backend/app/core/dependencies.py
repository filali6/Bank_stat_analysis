from functools import lru_cache

from app.core.config import settings
from app.repositories.merchant_repository import MerchantRepository
from app.services.enrichment_service import EnrichmentService
from app.services.matchers.exact_matcher import ExactMatcher
from app.services.matchers.fuzzy_matcher import FuzzyMatcher
from app.services.matchers.tfidf_matcher import TfidfMatcher
from app.services.merchant_identifier import MerchantIdentifier

"""This is the ONE place in the codebase where concrete classes are
wired together. Everywhere else, code depends on the Matcher interface
or on MerchantIdentifier — never on ExactMatcher/FuzzyMatcher/TfidfMatcher
directly (Dependency Inversion). To add a 4th matcher later, add one line
to the list below; nothing else in the app needs to change.

FastAPI's Depends() calls these functions to inject dependencies into
route handlers, and @lru_cache means each object is built only once.
"""


@lru_cache
def get_merchant_repository() -> MerchantRepository:
    return MerchantRepository(settings.merchant_db_path)


@lru_cache
def get_merchant_identifier() -> MerchantIdentifier:
    repository = get_merchant_repository()
    return MerchantIdentifier(
        [
            ExactMatcher(repository),
            FuzzyMatcher(repository, threshold=settings.fuzzy_threshold),
            TfidfMatcher(repository, threshold=settings.tfidf_threshold),
        ]
    )


@lru_cache
def get_enrichment_service() -> EnrichmentService:
    return EnrichmentService(get_merchant_identifier())
