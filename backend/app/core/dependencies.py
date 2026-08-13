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
from app.services.lifestyle_intelligence_service import LifestyleIntelligenceService
from app.repositories.scorecard_rules_repository import ScorecardRulesRepository
from app.repositories.decision_rules_repository import DecisionRulesRepository
from app.services.decision_service import DecisionService
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.repositories.client_repository import ClientRepository
from app.repositories.study_repository import StudyRepository
from app.services.study_service import StudyService



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

@lru_cache
def get_scorecard_rules_repository() -> ScorecardRulesRepository:
    return ScorecardRulesRepository(settings.scorecard_rules_path)

@lru_cache
def get_lifestyle_intelligence_service() -> LifestyleIntelligenceService:
    return LifestyleIntelligenceService(get_scorecard_rules_repository())
@lru_cache
def get_decision_rules_repository() -> DecisionRulesRepository:
    return DecisionRulesRepository(settings.decision_rules_path)

@lru_cache
def get_decision_service() -> DecisionService:
    return DecisionService(get_decision_rules_repository())

def get_db():
    """One SQLAlchemy Session per request — not a singleton, unlike
    the file-backed repositories above. FastAPI closes it automatically
    once the request finishes, even if an error was raised."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_client_repository(db: Session = Depends(get_db)) -> ClientRepository:
    return ClientRepository(db)


def get_study_repository(db: Session = Depends(get_db)) -> StudyRepository:
    return StudyRepository(db)


def get_study_service(
    client_repository: ClientRepository = Depends(get_client_repository),
    study_repository: StudyRepository = Depends(get_study_repository),
) -> StudyService:
    return StudyService(client_repository, study_repository)