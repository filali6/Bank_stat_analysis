from app.core.config import settings
from app.repositories.merchant_repository import MerchantRepository
from app.services.matchers.exact_matcher import ExactMatcher


def _matcher() -> ExactMatcher:
    repository = MerchantRepository(settings.merchant_db_path)
    return ExactMatcher(repository)


def test_finds_known_merchant_by_keyword():
    result = _matcher().match("NETFLIX.COM IE")

    assert result is not None
    assert result.merchant == "Netflix"
    assert result.matched_by == "exact"
    assert result.confidence > 0


def test_returns_none_when_no_keyword_matches():
    result = _matcher().match("PAIEMENT DIVERS 0049")

    assert result is None


def test_longer_pattern_gives_higher_confidence():
    short_pattern_result = _matcher().match("UBER PARIS FR")
    long_pattern_result = _matcher().match("PLANET FITNESS DENVER CO")

    assert long_pattern_result.confidence >= short_pattern_result.confidence
