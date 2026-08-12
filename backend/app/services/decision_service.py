from typing import List

from app.repositories.decision_rules_repository import DecisionRules, DecisionRulesRepository, OpportunityRule
from app.schemas.transaction import (
    AffordabilityResult,
    ClientFeatures,
    ConsistencyCheck,
    CreditDecisionDetails,
    DecisionResult,
    KycDecisionDetails,
    LifestyleFeatures,
    OpportunitiesDecisionDetails,
    RiskAlert,
    RiskDecisionDetails,
    SuggestedProduct,
)


class DecisionService:
    """Turns the already-computed ClientFeatures + LifestyleFeatures
    into the output-specific view the analyst asked for at the start
    of the study (FR-A3). All thresholds, labels, and product rules
    live in DecisionRulesRepository (decision_rules.json) — nothing
    here is a hardcoded Python literal, same principle as
    LifestyleIntelligenceService.

    One deliberate boundary: alert severities ("low"/"medium"/"high")
    are a fixed vocabulary, not configurable data — the frontend's
    RiskAlert type hardcodes the same three values, so treating them
    as an open-ended JSON string would just move the coupling
    elsewhere without adding real flexibility.
    """

    def __init__(self, rules_repository: DecisionRulesRepository):
        self._rules_repository = rules_repository

    def compute(self, output_type: str, features: ClientFeatures, lifestyle: LifestyleFeatures) -> DecisionResult:
        rules = self._rules_repository.get_rules()

        if output_type == "credit":
            return self._compute_credit(features, lifestyle, rules)
        if output_type == "risk":
            return self._compute_risk(features, lifestyle, rules)
        if output_type == "kyc":
            return self._compute_kyc(features, lifestyle, rules)
        if output_type == "opportunities":
            return self._compute_opportunities(features, lifestyle, rules)
        raise ValueError(f"Unknown output_type: {output_type}")

    def check_affordability(self, features: ClientFeatures, loan_amount: float, duration_months: int) -> AffordabilityResult:
        ratio = self._rules_repository.get_rules().affordability.ratio
        disposable_income = self._disposable_income(features)
        monthly_payment = loan_amount / duration_months if duration_months > 0 else loan_amount
        max_affordable_payment = round(disposable_income * ratio, 2)

        return AffordabilityResult(
            monthly_payment=round(monthly_payment, 2),
            disposable_income=round(disposable_income, 2),
            max_affordable_payment=max_affordable_payment,
            affordable=monthly_payment <= max_affordable_payment,
        )

    # --- Credit underwriting -------------------------------------------------

    def _compute_credit(self, features: ClientFeatures, lifestyle: LifestyleFeatures, rules: DecisionRules) -> DecisionResult:
        credit = rules.credit
        credit_score = round(lifestyle.overall_lifestyle_index * credit.score_scale)

        if credit_score >= credit.approved_min:
            recommendation = credit.approved_label
        elif credit_score >= credit.review_min:
            recommendation = credit.review_label
        else:
            recommendation = credit.declined_label

        details = CreditDecisionDetails(
            credit_score=credit_score,
            recommendation=recommendation,
            repayment_capacity=round(self._disposable_income(features), 2),
        )
        return DecisionResult(
            output_type="credit",
            headline=f"Credit score {credit_score}/850 — {recommendation}",
            credit=details,
        )

    # --- Risk management -------------------------------------------------

    def _compute_risk(self, features: ClientFeatures, lifestyle: LifestyleFeatures, rules: DecisionRules) -> DecisionResult:
        risk = rules.risk
        alerts: List[RiskAlert] = []

        if features.monthly_income <= 0:
            alerts.append(RiskAlert(severity=risk.no_income_alert.severity, message=risk.no_income_alert.message))

        commitments_ratio = self._safe_ratio(features.recurring_commitments, features.monthly_income)
        for tier in risk.commitments_tiers:  # ordered from highest threshold to lowest, first match wins
            if commitments_ratio > tier.threshold:
                alerts.append(RiskAlert(severity=tier.severity, message=tier.message))
                break

        if features.atm_withdrawal_ratio > risk.atm_ratio_tier.threshold:
            alerts.append(RiskAlert(severity=risk.atm_ratio_tier.severity, message=risk.atm_ratio_tier.message))

        if features.savings_rate < risk.low_savings_tier.threshold:
            alerts.append(RiskAlert(severity=risk.low_savings_tier.severity, message=risk.low_savings_tier.message))

        if any(a.severity == "high" for a in alerts):
            risk_level = risk.high_risk_level
        elif alerts:
            risk_level = risk.medium_risk_level
        else:
            risk_level = risk.low_risk_level

        details = RiskDecisionDetails(risk_level=risk_level, alerts=alerts)
        return DecisionResult(
            output_type="risk",
            headline=f"Risk level: {risk_level} ({len(alerts)} alert(s))",
            risk=details,
        )

    # --- Customer insight / KYC -------------------------------------------------

    def _compute_kyc(self, features: ClientFeatures, lifestyle: LifestyleFeatures, rules: DecisionRules) -> DecisionResult:
        kyc = rules.kyc
        checks = [
            ConsistencyCheck(
                label=kyc.income_check_label,
                status=kyc.consistent_status if features.monthly_income > 0 else kyc.needs_review_status,
            ),
            ConsistencyCheck(
                label=kyc.spending_check_label,
                status=kyc.consistent_status if self._disposable_income(features) >= 0 else kyc.needs_review_status,
            ),
            ConsistencyCheck(
                label=kyc.segment_check_label,
                status=kyc.consistent_status if lifestyle.lifestyle_segment else kyc.needs_review_status,
            ),
        ]
        all_consistent = all(c.status == kyc.consistent_status for c in checks)

        details = KycDecisionDetails(
            consistency_checks=checks,
            profile_summary=(
                f"{lifestyle.lifestyle_segment} — monthly income {features.monthly_income:.0f}$, "
                f"savings rate {features.savings_rate:.0f}%"
            ),
        )
        return DecisionResult(
            output_type="kyc",
            headline="KYC status: " + ("Consistent" if all_consistent else "Needs review"),
            kyc=details,
        )

    # --- Identifying commercial opportunities -------------------------------------------------

    def _compute_opportunities(self, features: ClientFeatures, lifestyle: LifestyleFeatures, rules: DecisionRules) -> DecisionResult:
        values = {**features.model_dump(), **lifestyle.model_dump()}
        products: List[SuggestedProduct] = []

        for rule in rules.opportunities.rules:
            if self._matches(values.get(rule.field), rule):
                products.append(SuggestedProduct(name=rule.product_name, reason=rule.reason))

        if not products:
            products.append(
                SuggestedProduct(
                    name=rules.opportunities.default_product_name,
                    reason=rules.opportunities.default_product_reason,
                )
            )

        details = OpportunitiesDecisionDetails(suggested_products=products)
        return DecisionResult(
            output_type="opportunities",
            headline=f"{len(products)} product(s) suggested",
            opportunities=details,
        )

    @staticmethod
    def _matches(value, rule: OpportunityRule) -> bool:
        if value is None:
            return False
        if rule.operator == "equals":
            return value == rule.value
        if rule.operator == "greater_than":
            return value > rule.value
        if rule.operator == "less_than":
            return value < rule.value
        raise ValueError(f"Unknown operator: {rule.operator}")

    @staticmethod
    def _disposable_income(features: ClientFeatures) -> float:
        return features.monthly_income - features.recurring_commitments

    @staticmethod
    def _safe_ratio(part: float, whole: float) -> float:
        if whole == 0:
            return 0.0
        return part / whole