from app.schemas.transaction import CategorizedTransaction
from app.services.feature_engineering_service import FeatureEngineeringService


def _txn(**overrides) -> CategorizedTransaction:
    base = dict(
        transaction_id="T1",
        date="2026-06-01",
        libelle_brut="TEST",
        montant=-10.0,
        merchant="Test",
        payment_channel="Card POS",
        transaction_type="Purchase",
        recurring=False,
        income_flag=False,
        normalized_description="TEST",
        category="Shopping",
        subcategory="Other",
        business_purpose="Personal",
        lifestyle_tag="Discretionary Spending",
        confidence=0.9,
        status="validated",
    )
    base.update(overrides)
    return CategorizedTransaction(**base)


def test_empty_transactions_returns_all_zeros():
    result = FeatureEngineeringService().compute([])
    assert result.monthly_income == 0.0
    assert result.recurring_commitments == 0.0


def test_monthly_income_averages_only_the_3_most_recent_income_months():
    transactions = [
        _txn(date="2026-01-05", montant=4000, income_flag=True, category="Income"),
        _txn(date="2026-02-05", montant=5000, income_flag=True, category="Income"),
        _txn(date="2026-03-05", montant=6000, income_flag=True, category="Income"),
        _txn(date="2026-04-05", montant=7000, income_flag=True, category="Income"),
    ]
    result = FeatureEngineeringService().compute(transactions)
    # only Feb/Mar/Apr count — Jan is outside the 3-month recency window
    assert result.monthly_income == (5000 + 6000 + 7000) / 3


def test_savings_transfers_are_not_counted_as_recurring_commitments():
    """The bug: a recurring Savings transfer used to inflate
    recurring_commitments as if it were a bill."""
    transactions = [
        _txn(date="2026-06-01", montant=6000, income_flag=True, category="Income"),
        _txn(date="2026-06-03", montant=-1500, recurring=True, category="Savings"),
        _txn(date="2026-06-06", montant=-15.99, recurring=True, category="Entertainment"),
    ]
    result = FeatureEngineeringService().compute(transactions)
    # only the Netflix-like recurring bill counts, not the savings transfer
    assert result.recurring_commitments == 15.99


def test_recurring_commitments_are_averaged_by_month_not_summed_raw():
    """The bug: a raw sum over the whole file grew with however many
    months the file covered, instead of reflecting a true monthly figure."""
    transactions = [
        _txn(date="2026-01-01", montant=-500, recurring=True, category="Housing"),
        _txn(date="2026-02-01", montant=-500, recurring=True, category="Housing"),
        _txn(date="2026-03-01", montant=-500, recurring=True, category="Housing"),
    ]
    result = FeatureEngineeringService().compute(transactions)
    # averaged across the 3 months, not summed to 1500
    assert result.recurring_commitments == 500.0


def test_recurring_commitments_only_averages_the_3_most_recent_months():
    transactions = [
        _txn(date="2026-01-01", montant=-100, recurring=True, category="Housing"),
        _txn(date="2026-02-01", montant=-500, recurring=True, category="Housing"),
        _txn(date="2026-03-01", montant=-500, recurring=True, category="Housing"),
        _txn(date="2026-04-01", montant=-500, recurring=True, category="Housing"),
    ]
    result = FeatureEngineeringService().compute(transactions)
    # January (100) falls outside the 3-month recency window
    assert result.recurring_commitments == 500.0


def test_safe_ratio_handles_zero_income_without_crashing():
    transactions = [_txn(date="2026-06-01", montant=-50, category="Shopping")]
    result = FeatureEngineeringService().compute(transactions)
    assert result.savings_rate == 0.0