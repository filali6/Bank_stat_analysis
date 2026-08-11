from typing import List

from app.repositories.scorecard_rules_repository import ScorecardRules, ScorecardRulesRepository, Tier
from app.schemas.transaction import ClientFeatures, LifestyleFeatures


class LifestyleIntelligenceService:
    """Turns the client-level financial indicators (Feature Engineering)
    into a scorecard, a lifestyle segment, and composite indices.

    All thresholds, points, and segment names live in
    ScorecardRulesRepository (scorecard_rules.json) — nothing here is a
    hardcoded Python literal, so scoring can be retuned without a code
    change. Explainability comes "by construction": any tier that
    scores points can carry a reason, returned alongside the scores
    instead of relying on a tool like SHAP to guess it after the fact
    (that approach belongs to Categorization, the only step with a
    real trained model).
    """

    def __init__(self, rules_repository: ScorecardRulesRepository):
        self._rules_repository = rules_repository

    def compute(self, features: ClientFeatures) -> LifestyleFeatures:
        rules = self._rules_repository.get_rules()
        reasons: List[str] = []

        affluence_score = self._compute_affluence(features, rules, reasons)
        discipline_score = self._compute_discipline(features, rules, reasons)
        travel_index = self._compute_travel_index(features, rules, reasons)
        family_index = self._compute_family_index(features, rules, reasons)
        overall_index = round((affluence_score + discipline_score) / 2, 1)
        segment = self._compute_segment(affluence_score, discipline_score, rules)

        return LifestyleFeatures(
            lifestyle_segment=segment,
            affluence_score=affluence_score,
            financial_discipline_score=discipline_score,
            travel_activity_index=travel_index,
            family_responsibility_index=family_index,
            overall_lifestyle_index=overall_index,
            reasons=reasons,
        )

    def _compute_affluence(self, f: ClientFeatures, rules: ScorecardRules, reasons: List[str]) -> float:
        score = 0.0
        score += self._apply_min_tiers(f.monthly_income, rules.affluence_income_tiers, reasons)
        score += self._apply_min_tiers(f.savings_rate, rules.affluence_savings_tiers, reasons)

        commitments_ratio = self._safe_ratio(f.recurring_commitments, f.monthly_income)
        score += self._apply_max_tiers(commitments_ratio, rules.affluence_commitments_tiers, reasons)

        return round(min(score, rules.score_cap), 1)

    def _compute_discipline(self, f: ClientFeatures, rules: ScorecardRules, reasons: List[str]) -> float:
        score = 0.0
        score += self._apply_min_tiers(f.savings_rate, rules.discipline_savings_tiers, reasons)
        score += self._apply_max_tiers(f.atm_withdrawal_ratio, rules.discipline_atm_tiers, reasons)

        commitments_ratio = self._safe_ratio(f.recurring_commitments, f.monthly_income)
        score += self._apply_max_tiers(commitments_ratio, rules.discipline_commitments_tiers, reasons)

        return round(min(score, rules.score_cap), 1)

    def _compute_travel_index(self, f: ClientFeatures, rules: ScorecardRules, reasons: List[str]) -> str:
        travel = rules.travel_index
        if f.travel_spend_ratio > travel.high_min:
            reasons.append(travel.high_reason)
            return "High"
        if f.travel_spend_ratio > travel.medium_min:
            return "Medium"
        return "Low"

    def _compute_family_index(self, f: ClientFeatures, rules: ScorecardRules, reasons: List[str]) -> str:
        """Proxy indicator: no direct family data is available from a
        bank statement alone, so we estimate responsibility level from
        the weight of fixed recurring commitments relative to income —
        higher fixed obligations often correlate with dependents/housing
        responsibilities. Clearly a proxy, not a certainty.
        """
        family = rules.family_index
        commitments_ratio = self._safe_ratio(f.recurring_commitments, f.monthly_income)
        if commitments_ratio > family.high_min_ratio:
            reasons.append(family.high_reason)
            return "High"
        if commitments_ratio > family.medium_min_ratio:
            return "Medium"
        return "Low"

    def _compute_segment(self, affluence: float, discipline: float, rules: ScorecardRules) -> str:
        segments = rules.segments
        if affluence >= segments.affluent_threshold and discipline >= segments.affluent_threshold:
            return segments.affluent_professional
        if affluence >= segments.affluent_threshold and discipline < segments.affluent_threshold:
            return segments.high_earner_low_discipline
        if affluence < segments.vulnerable_threshold and discipline >= segments.affluent_threshold:
            return segments.frugal_saver
        if affluence < segments.vulnerable_threshold and discipline < segments.vulnerable_threshold:
            return segments.financially_vulnerable
        return segments.balanced_middle_income

    @staticmethod
    def _apply_min_tiers(value: float, tiers: List[Tier], reasons: List[str]) -> float:
        """Tiers ordered from highest threshold to lowest — the first
        tier the value exceeds wins. Used for "the more, the better"
        metrics like income or savings rate."""
        for tier in tiers:
            if value > tier.threshold:
                if tier.reason:
                    reasons.append(tier.reason)
                return tier.points
        return 0.0

    @staticmethod
    def _apply_max_tiers(value: float, tiers: List[Tier], reasons: List[str]) -> float:
        """Tiers ordered from lowest threshold to highest — the first
        tier the value stays under wins. Used for "the less, the
        better" metrics like cash withdrawal ratio or debt load."""
        for tier in tiers:
            if value < tier.threshold:
                if tier.reason:
                    reasons.append(tier.reason)
                return tier.points
        return 0.0

    @staticmethod
    def _safe_ratio(part: float, whole: float) -> float:
        if whole == 0:
            return 0.0
        return part / whole