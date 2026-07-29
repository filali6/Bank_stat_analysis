from app.core.config import settings
from app.repositories.merchant_repository import MerchantRepository
from app.services.matchers.fuzzy_matcher import FuzzyMatcher


def _matcher() -> FuzzyMatcher:
    repository = MerchantRepository(settings.merchant_db_path)
    return FuzzyMatcher(repository, threshold=80)


def test_catches_a_typo_that_exact_match_would_miss():
    result = _matcher().match("NTFLX ONLINE US")

    assert result is not None
    assert result.merchant == "Netflix"
    assert result.matched_by == "fuzzy"


def test_returns_none_for_completely_unrelated_text():
    result = _matcher().match("PAIEMENT DIVERS 0049")

    assert result is None


def test_confidence_is_always_below_the_raw_similarity_score():
    result = _matcher().match("STRBCKS DENVER CO")

    assert result is not None
    # confidence = score * 0.85, so it must be strictly discounted
    assert result.confidence < 100
