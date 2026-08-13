from typing import List

import pytest

from app.repositories.merchant_repository import Merchant
from app.repositories.scorecard_rules_repository import (
    FamilyIndexRules,
    ScorecardRules,
    SegmentRules,
    Tier,
    TravelIndexRules,
)
from app.repositories.decision_rules_repository import (
    AffordabilityRules,
    AlertTier,
    CreditRules,
    DecisionRules,
    KycRules,
    OpportunitiesRules,
    OpportunityRule,
    RiskRules,
    SimpleAlert,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base


class FakeMerchantRepository:
    """An in-memory stand-in for MerchantRepository. Matcher tests use
    this fixed, hand-picked merchant list instead of the real
    merchant_db.json — so they only fail when a matcher's own logic
    breaks, never because someone (rightfully) added, removed, or
    edited a merchant in the production data file.
    """

    def __init__(self, merchants: List[Merchant]):
        self._merchants = merchants

    def get_all(self) -> List[Merchant]:
        return self._merchants


@pytest.fixture
def merchant_repository() -> FakeMerchantRepository:
    return FakeMerchantRepository(
        [
            Merchant(
                name="Netflix",
                patterns=["NETFLIX", "NFLX*COM", "NFLX COM"],
                category="Entertainment",
                subcategory="Streaming",
                channel="Card Online",
                type="Subscription",
                recurring=True,
                income=False,
            ),
            Merchant(
                name="Starbucks",
                patterns=["STARBUCKS", "STRBCKS"],
                category="Food",
                subcategory="Coffee",
                channel="Card POS",
                type="Purchase",
                recurring=False,
                income=False,
            ),
            Merchant(
                name="Uber",
                patterns=["UBER"],
                category="Transport",
                subcategory="Rideshare",
                channel="Card Online",
                type="Purchase",
                recurring=False,
                income=False,
            ),
            Merchant(
                name="Planet Fitness",
                patterns=["PLANET FITNESS"],
                category="Health",
                subcategory="Gym",
                channel="Card POS",
                type="Subscription",
                recurring=True,
                income=False,
            ),
        ]
    )
class FakeScorecardRulesRepository:
    """An in-memory stand-in for ScorecardRulesRepository. Lifestyle
    Intelligence tests use a fixed, known ruleset instead of the real
    scorecard_rules.json — so they only fail when the scoring logic
    itself is broken, never because a bank retuned a threshold.
    """

    def __init__(self, rules: ScorecardRules):
        self._rules = rules

    def get_rules(self) -> ScorecardRules:
        return self._rules


@pytest.fixture
def scorecard_rules_repository() -> FakeScorecardRulesRepository:
    return FakeScorecardRulesRepository(
        ScorecardRules(
            score_cap=100,
            affluence_income_tiers=[
                Tier(threshold=5000, points=40, reason="High income"),
                Tier(threshold=3000, points=25, reason=None),
                Tier(threshold=1500, points=10, reason=None),
            ],
            affluence_savings_tiers=[
                Tier(threshold=20, points=30, reason="High savings rate"),
                Tier(threshold=10, points=15, reason=None),
            ],
            affluence_commitments_tiers=[
                Tier(threshold=0.3, points=30, reason=None),
                Tier(threshold=0.5, points=15, reason=None),
            ],
            discipline_savings_tiers=[
                Tier(threshold=20, points=40, reason=None),
                Tier(threshold=10, points=20, reason=None),
            ],
            discipline_atm_tiers=[
                Tier(threshold=5, points=30, reason="Low cash usage"),
                Tier(threshold=15, points=15, reason=None),
            ],
            discipline_commitments_tiers=[
                Tier(threshold=0.4, points=30, reason=None),
                Tier(threshold=0.6, points=15, reason=None),
            ],
            travel_index=TravelIndexRules(high_min=15, medium_min=5, high_reason="High travel activity"),
            family_index=FamilyIndexRules(
                high_min_ratio=0.5, medium_min_ratio=0.25, high_reason="High fixed commitments"
            ),
            segments=SegmentRules(
                affluent_threshold=70,
                vulnerable_threshold=40,
                affluent_professional="Affluent Professional",
                high_earner_low_discipline="High Earner, Low Discipline",
                frugal_saver="Frugal Saver",
                financially_vulnerable="Financially Vulnerable",
                balanced_middle_income="Balanced Middle-Income",
            ),
        )
    )

class FakeDecisionRulesRepository:
    """An in-memory stand-in for DecisionRulesRepository. Decision
    tests use a fixed, known ruleset instead of the real
    decision_rules.json — so they only fail when DecisionService's
    logic itself is broken, never because a bank retuned a threshold
    or renamed a product.
    """

    def __init__(self, rules: DecisionRules):
        self._rules = rules

    def get_rules(self) -> DecisionRules:
        return self._rules


@pytest.fixture
def decision_rules_repository() -> FakeDecisionRulesRepository:
    return FakeDecisionRulesRepository(
        DecisionRules(
            credit=CreditRules(
                score_scale=8.5,
                approved_min=700,
                review_min=550,
                approved_label="Approved",
                review_label="Review recommended",
                declined_label="Not recommended",
            ),
            affordability=AffordabilityRules(ratio=0.4),
            risk=RiskRules(
                no_income_alert=SimpleAlert(severity="high", message="No income detected on this statement"),
                commitments_tiers=[
                    AlertTier(threshold=0.6, severity="high", message="Recurring commitments exceed 60% of income"),
                    AlertTier(threshold=0.4, severity="medium", message="Recurring commitments exceed 40% of income"),
                ],
                atm_ratio_tier=AlertTier(threshold=20, severity="medium", message="High cash withdrawal activity"),
                low_savings_tier=AlertTier(threshold=2, severity="medium", message="Very low or negative savings rate"),
                high_risk_level="High",
                medium_risk_level="Medium",
                low_risk_level="Low",
            ),
            kyc=KycRules(
                income_check_label="Income detected on statement",
                spending_check_label="Spending stays within income",
                segment_check_label="Lifestyle segment assigned",
                consistent_status="consistent",
                needs_review_status="needs_review",
            ),
            opportunities=OpportunitiesRules(
                rules=[
                    OpportunityRule(
                        field="travel_activity_index", operator="equals", value="High",
                        product_name="Premium Travel Card", reason="High travel spending detected",
                    ),
                    OpportunityRule(
                        field="savings_rate", operator="greater_than", value=15,
                        product_name="Investment Account", reason="Strong savings behavior",
                    ),
                    OpportunityRule(
                        field="atm_withdrawal_ratio", operator="greater_than", value=15,
                        product_name="Overdraft Protection", reason="Frequent cash withdrawals",
                    ),
                    OpportunityRule(
                        field="lifestyle_segment", operator="equals", value="Affluent Professional",
                        product_name="Premium Banking Package", reason="Affluent client profile",
                    ),
                ],
                default_product_name="Standard Savings Account",
                default_product_reason="Default suggestion — no strong signal detected",
            ),
        )
    )

@pytest.fixture
def db_session():
    """A fresh, isolated in-memory SQLite database per test — never
    touches the real app.db file, and every test starts with empty
    tables (no leftover data from a previous test or a real run).
    """
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()