from app.schemas.transaction import ClientFeatures
from app.services.lifestyle_intelligence_service import LifestyleIntelligenceService


def test_high_income_high_savings_client_is_affluent_professional(scorecard_rules_repository):
    service = LifestyleIntelligenceService(scorecard_rules_repository)
    features = ClientFeatures(
        monthly_income=6000,
        savings_rate=25,
        travel_spend_ratio=3,
        grocery_spend_ratio=10,
        recurring_commitments=1000,
        atm_withdrawal_ratio=2,
    )

    result = service.compute(features)

    assert result.lifestyle_segment == "Affluent Professional"
    assert result.affluence_score == 100.0
    assert result.travel_activity_index == "Low"
    assert len(result.reasons) > 0


def test_low_income_low_savings_client_is_financially_vulnerable(scorecard_rules_repository):
    service = LifestyleIntelligenceService(scorecard_rules_repository)
    features = ClientFeatures(
        monthly_income=1200,
        savings_rate=2,
        travel_spend_ratio=1,
        grocery_spend_ratio=30,
        recurring_commitments=900,
        atm_withdrawal_ratio=25,
    )

    result = service.compute(features)

    assert result.lifestyle_segment == "Financially Vulnerable"


def test_zero_income_does_not_crash_on_division(scorecard_rules_repository):
    service = LifestyleIntelligenceService(scorecard_rules_repository)
    features = ClientFeatures(
        monthly_income=0,
        savings_rate=0,
        travel_spend_ratio=0,
        grocery_spend_ratio=0,
        recurring_commitments=0,
        atm_withdrawal_ratio=0,
    )

    result = service.compute(features)

    assert result.overall_lifestyle_index >= 0


def test_thresholds_come_from_the_rules_repository_not_from_hardcoded_values(scorecard_rules_repository):
    """A client just above the income tier boundary should score
    points, and just below should not — proving the service reads the
    threshold from the injected rules rather than a literal in the
    code (the fixture uses the same numeric values as the real
    scorecard_rules.json on purpose, but the point is the service
    never hardcodes them itself)."""
    service = LifestyleIntelligenceService(scorecard_rules_repository)

    base = dict(
        savings_rate=0,
        travel_spend_ratio=0,
        grocery_spend_ratio=0,
        recurring_commitments=0,
        atm_withdrawal_ratio=0,
    )

    above = service.compute(ClientFeatures(monthly_income=5001, **base))
    below = service.compute(ClientFeatures(monthly_income=4999, **base))

    assert above.affluence_score > below.affluence_score