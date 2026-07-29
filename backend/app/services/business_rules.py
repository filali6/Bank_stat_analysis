from app.schemas.transaction import MatchResult


def apply_business_rules(montant: float, result: MatchResult) -> MatchResult:
    """Corrects or completes a matcher's guess using the transaction's
    amount sign — a signal that's independent from, and often more
    reliable than, the raw text itself.
    """
    updated = result.model_copy()

    if montant > 0 and updated.income:
        updated.type = "Income"
        return updated

    if montant > 0 and updated.merchant == "Unknown":
        updated.type = "Credit"
        return updated

    if updated.type == "Withdrawal":
        updated.channel = "ATM"

    if updated.type in ("Income", "Transfer", "Direct Debit"):
        updated.channel = "Transfer"

    return updated
