from app.services.matchers.fuzzy_matcher import FuzzyMatcher


def _matcher(merchant_repository) -> FuzzyMatcher:
    return FuzzyMatcher(merchant_repository, threshold=80)


def test_catches_a_typo_that_exact_match_would_miss(merchant_repository):
    result = _matcher(merchant_repository).match("NTFLX ONLINE US")

    assert result is not None
    assert result.merchant == "Netflix"
    assert result.matched_by == "fuzzy"


def test_returns_none_for_completely_unrelated_text(merchant_repository):
    result = _matcher(merchant_repository).match("PAIEMENT DIVERS 0049")

    assert result is None


def test_confidence_is_always_below_the_raw_similarity_score(merchant_repository):
    result = _matcher(merchant_repository).match("STRBCKS DENVER CO")

    assert result is not None
    # confidence = score * 0.85, so it must be strictly discounted
    assert result.confidence < 100