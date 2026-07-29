from app.schemas.transaction import MatchResult
from app.services.business_rules import apply_business_rules


def _unknown_result() -> MatchResult:
    return MatchResult(
        merchant="Unknown", category="Unknown", subcategory="Unknown",
        channel="Unknown", type="Unknown", recurring=False, income=False,
        confidence=0,
    )


def test_positive_amount_on_income_merchant_becomes_income():
    result = MatchResult(
        merchant="Employer", category="Income", subcategory="Salary",
        channel="Transfer", type="Purchase", recurring=True, income=True,
        confidence=90,
    )

    updated = apply_business_rules(3200.0, result)

    assert updated.type == "Income"


def test_positive_amount_on_unknown_merchant_becomes_credit():
    updated = apply_business_rules(50.0, _unknown_result())

    assert updated.type == "Credit"


def test_withdrawal_channel_is_forced_to_atm():
    result = MatchResult(
        merchant="ATM", category="Cash", subcategory="Withdrawal",
        channel="Card POS", type="Withdrawal", recurring=False, income=False,
        confidence=80,
    )

    updated = apply_business_rules(-100.0, result)

    assert updated.channel == "ATM"


def test_negative_amount_on_unknown_merchant_stays_unknown():
    updated = apply_business_rules(-50.0, _unknown_result())

    assert updated.merchant == "Unknown"
