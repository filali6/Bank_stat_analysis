from app.services.matchers.exact_matcher import ExactMatcher


def test_finds_known_merchant_by_keyword(merchant_repository):
    result = ExactMatcher(merchant_repository).match("NETFLIX.COM IE")

    assert result is not None
    assert result.merchant == "Netflix"
    assert result.matched_by == "exact"
    assert result.confidence > 0


def test_returns_none_when_no_keyword_matches(merchant_repository):
    result = ExactMatcher(merchant_repository).match("PAIEMENT DIVERS 0049")

    assert result is None


def test_longer_pattern_gives_higher_confidence(merchant_repository):
    matcher = ExactMatcher(merchant_repository)

    short_pattern_result = matcher.match("UBER PARIS FR")
    long_pattern_result = matcher.match("PLANET FITNESS DENVER CO")

    assert short_pattern_result is not None
    assert long_pattern_result is not None
    assert long_pattern_result.confidence >= short_pattern_result.confidence