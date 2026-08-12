import pytest

from app.schemas.transaction import ClientFeatures, LifestyleFeatures
from app.services.decision_service import DecisionService


def _features(**overrides) -> ClientFeatures:
    base = dict(
        monthly_income=5200,
        savings_rate=22,
        travel_spend_ratio=8,
        grocery_spend_ratio=14,
        recurring_commitments=1850,
        atm_withdrawal_ratio=4,
    )
    base.update(overrides)
    return ClientFeatures(**base)


def _lifestyle(**overrides) -> LifestyleFeatures:
    base = dict(
        lifestyle_segment="Affluent Professional",
        affluence_score=85,
        financial_discipline_score=100,
        travel_activity_index="Medium",
        family_responsibility_index="Medium",
        overall_lifestyle_index=92.5,
        reasons=["Revenu mensuel élevé (> 5000$)"],
    )
    base.update(overrides)
    return LifestyleFeatures(**base)


def test_credit_output_gives_a_score_and_recommendation():
    result = DecisionService().compute("credit", _features(), _lifestyle())

    assert result.output_type == "credit"
    assert result.credit is not None
    assert result.credit.credit_score == round(92.5 * 8.5)
    assert result.credit.recommendation == "Approved"
    assert result.risk is None and result.kyc is None and result.opportunities is None


def test_risk_output_flags_high_commitments():
    features = _features(monthly_income=1000, recurring_commitments=900)
    result = DecisionService().compute("risk", features, _lifestyle())

    assert result.output_type == "risk"
    assert result.risk is not None
    assert result.risk.risk_level in {"Medium", "High"}
    assert any("commitments" in a.message.lower() for a in result.risk.alerts)


def test_risk_output_is_low_for_a_healthy_client():
    result = DecisionService().compute("risk", _features(), _lifestyle())

    assert result.risk.risk_level == "Low"
    assert result.risk.alerts == []


def test_kyc_output_flags_zero_income_as_needing_review():
    features = _features(monthly_income=0, recurring_commitments=0)
    result = DecisionService().compute("kyc", features, _lifestyle())

    assert result.kyc is not None
    statuses = {c.label: c.status for c in result.kyc.consistency_checks}
    assert statuses["Income detected on statement"] == "needs_review"


def test_opportunities_output_suggests_travel_card_for_high_travel_index():
    result = DecisionService().compute(
        "opportunities", _features(), _lifestyle(travel_activity_index="High")
    )

    assert result.opportunities is not None
    names = [p.name for p in result.opportunities.suggested_products]
    assert "Premium Travel Card" in names


def test_opportunities_output_always_suggests_something():
    features = _features(savings_rate=0, atm_withdrawal_ratio=0)
    lifestyle = _lifestyle(travel_activity_index="Low", lifestyle_segment="Balanced Middle-Income")

    result = DecisionService().compute("opportunities", features, lifestyle)

    assert len(result.opportunities.suggested_products) >= 1


def test_unknown_output_type_raises():
    with pytest.raises(ValueError):
        DecisionService().compute("not_a_real_output", _features(), _lifestyle())


def test_affordable_loan_is_flagged_as_affordable():
    service = DecisionService()
    # disposable income = 5200 - 1850 = 3350, max payment = 3350 * 0.4 = 1340
    result = service.check_affordability(_features(), loan_amount=6000, duration_months=12)

    assert result.monthly_payment == 500.0
    assert result.affordable is True


def test_unaffordable_loan_is_flagged_as_not_affordable():
    service = DecisionService()
    result = service.check_affordability(_features(), loan_amount=60000, duration_months=6)

    assert result.affordable is False