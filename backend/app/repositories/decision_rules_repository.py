import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union


@dataclass(frozen=True)
class CreditRules:
    score_scale: float
    approved_min: float
    review_min: float
    approved_label: str
    review_label: str
    declined_label: str


@dataclass(frozen=True)
class AffordabilityRules:
    ratio: float


@dataclass(frozen=True)
class SimpleAlert:
    severity: str
    message: str


@dataclass(frozen=True)
class AlertTier:
    """A threshold that fires an alert with a given severity/message
    once crossed. commitments_tiers is a list checked in order (first
    match wins); atm_ratio_tier and low_savings_tier are single
    thresholds, each compared in its own direction (see DecisionService).
    """

    threshold: float
    severity: str
    message: str


@dataclass(frozen=True)
class RiskRules:
    no_income_alert: SimpleAlert
    commitments_tiers: List[AlertTier]
    atm_ratio_tier: AlertTier
    low_savings_tier: AlertTier
    high_risk_level: str
    medium_risk_level: str
    low_risk_level: str


@dataclass(frozen=True)
class KycRules:
    income_check_label: str
    spending_check_label: str
    segment_check_label: str
    consistent_status: str
    needs_review_status: str


@dataclass(frozen=True)
class OpportunityRule:
    """One row of the product catalog: if `field` (read off the
    combined ClientFeatures + LifestyleFeatures values) satisfies
    `operator` against `value`, suggest `product_name`."""

    field: str
    operator: str  # "equals" | "greater_than" | "less_than"
    value: Union[str, float]
    product_name: str
    reason: str


@dataclass(frozen=True)
class OpportunitiesRules:
    rules: List[OpportunityRule]
    default_product_name: str
    default_product_reason: str


@dataclass(frozen=True)
class DecisionRules:
    """Every tunable number, label, and product rule used by
    DecisionService — nothing here is a Python literal in the service
    anymore, same principle as ScorecardRulesRepository for Lifestyle
    Intelligence.
    """

    credit: CreditRules
    affordability: AffordabilityRules
    risk: RiskRules
    kyc: KycRules
    opportunities: OpportunitiesRules


class DecisionRulesRepository:
    """Gives access to the Decision step's rules. Same repository
    pattern as MerchantRepository / ScorecardRulesRepository: the
    service doesn't know or care that this comes from a JSON file
    today.
    """

    def __init__(self, source_path: Path):
        self._source_path = source_path
        self._rules: Optional[DecisionRules] = None

    def get_rules(self) -> DecisionRules:
        if self._rules is None:
            self._rules = self._load()
        return self._rules

    def _load(self) -> DecisionRules:
        with open(self._source_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        credit = CreditRules(**data["credit"])
        affordability = AffordabilityRules(**data["affordability"])

        risk_data = data["risk"]
        risk = RiskRules(
            no_income_alert=SimpleAlert(**risk_data["no_income_alert"]),
            commitments_tiers=[AlertTier(**t) for t in risk_data["commitments_tiers"]],
            atm_ratio_tier=AlertTier(**risk_data["atm_ratio_tier"]),
            low_savings_tier=AlertTier(**risk_data["low_savings_tier"]),
            high_risk_level=risk_data["high_risk_level"],
            medium_risk_level=risk_data["medium_risk_level"],
            low_risk_level=risk_data["low_risk_level"],
        )

        kyc = KycRules(**data["kyc"])

        opp_data = data["opportunities"]
        opportunities = OpportunitiesRules(
            rules=[OpportunityRule(**r) for r in opp_data["rules"]],
            default_product_name=opp_data["default_product_name"],
            default_product_reason=opp_data["default_product_reason"],
        )

        return DecisionRules(
            credit=credit,
            affordability=affordability,
            risk=risk,
            kyc=kyc,
            opportunities=opportunities,
        )