from collections import defaultdict
from typing import List

from app.schemas.transaction import CategorizedTransaction, ClientFeatures


class FeatureEngineeringService:
    """Aggregates a client's full categorized history into single
    financial indicators. Pure statistics (sums, ratios, time-based
    grouping) — no ML, unlike EnrichmentService/CategorizationService.
    """

    def compute(self, transactions: List[CategorizedTransaction]) -> ClientFeatures:
        if not transactions:
            return ClientFeatures(
                monthly_income=0.0, savings_rate=0.0, travel_spend_ratio=0.0,
                grocery_spend_ratio=0.0, recurring_commitments=0.0, atm_withdrawal_ratio=0.0,
            )

        monthly_income = self._compute_monthly_income(transactions)
        total_expenses = sum(abs(t.montant) for t in transactions if t.montant < 0)

        savings_total = sum(abs(t.montant) for t in transactions if t.category == "Savings" and t.montant < 0)
        travel_total = sum(abs(t.montant) for t in transactions if t.category == "Travel")
        grocery_total = sum(abs(t.montant) for t in transactions if t.category == "Groceries")
        recurring_total = sum(abs(t.montant) for t in transactions if t.recurring and t.montant < 0)
        atm_total = sum(abs(t.montant) for t in transactions if t.transaction_type == "Withdrawal")

        return ClientFeatures(
            monthly_income=round(monthly_income, 2),
            savings_rate=self._safe_ratio(savings_total, monthly_income),
            travel_spend_ratio=self._safe_ratio(travel_total, total_expenses),
            grocery_spend_ratio=self._safe_ratio(grocery_total, total_expenses),
            recurring_commitments=round(recurring_total, 2),
            atm_withdrawal_ratio=self._safe_ratio(atm_total, total_expenses),
        )

    def _compute_monthly_income(self, transactions: List[CategorizedTransaction]) -> float:
        """Time-series aggregation + trend analysis: group income by
        month, then average only the 3 most recent months instead of
        the whole history — reflects the client's recent situation
        rather than a flat, possibly outdated, average.
        """
        income_by_month = defaultdict(float)
        for t in transactions:
            if t.income_flag and t.montant > 0:
                month_key = t.date[:7]  # "YYYY-MM"
                income_by_month[month_key] += t.montant

        if not income_by_month:
            return 0.0

        months_sorted = sorted(income_by_month.keys())
        recent_months = months_sorted[-3:]
        recent_values = [income_by_month[m] for m in recent_months]
        return sum(recent_values) / len(recent_values)

    @staticmethod
    def _safe_ratio(part: float, whole: float) -> float:
        if whole == 0:
            return 0.0
        return round((part / whole) * 100, 2)