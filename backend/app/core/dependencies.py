from functools import lru_cache

from app.core.config import settings
from app.repositories.merchant_repository import MerchantRepository
from app.services.enrichment_service import EnrichmentService
from app.services.matchers.exact_matcher import ExactMatcher
from app.services.matchers.fuzzy_matcher import FuzzyMatcher
from app.services.matchers.tfidf_matcher import TfidfMatcher
from app.services.merchant_identifier import MerchantIdentifier
from app.repositories.business_lifestyle_repository import BusinessLifestyleRepository
from app.repositories.category_model_repository import CategoryModelRepository
from app.services.categorization_service import CategorizationService
from app.services.feature_engineering_service import FeatureEngineeringService

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

@lru_cache
def get_business_lifestyle_repository() -> BusinessLifestyleRepository:
    return BusinessLifestyleRepository(settings.business_lifestyle_mapping_path)


@lru_cache
def get_category_model_repository() -> CategoryModelRepository:
    return CategoryModelRepository(settings.category_model_bundle_path)


@lru_cache
def get_categorization_service() -> CategorizationService:
    return CategorizationService(
        merchant_repository=get_merchant_repository(),
        business_lifestyle_repository=get_business_lifestyle_repository(),
        category_model_repository=get_category_model_repository(),
    )
@lru_cache
def get_feature_engineering_service() -> FeatureEngineeringService:
    return FeatureEngineeringService()