from datetime import datetime, timedelta
from typing import List

from app.schemas.transaction import MatchResult, TransactionIn


def detect_recurring(
    transactions: List[TransactionIn],
    results: List[MatchResult],
    index: int,
    window_days: int = 90,
    amount_tolerance: float = 0.10,
) -> bool:
    """Looks back through this client's own transaction history to
    confirm a recurring payment, instead of relying only on the merchant
    database's generic "this is usually recurring" flag. Confirming it
    with real history is stronger evidence than a general assumption.
    """
    current_result = results[index]
    if current_result.merchant == "Unknown":
        return False

    current_txn = transactions[index]
    current_date = datetime.fromisoformat(current_txn.date)
    current_amount = abs(current_txn.montant)
    window_start = current_date - timedelta(days=window_days)

    similar_count = 0
    for i, (txn, result) in enumerate(zip(transactions, results)):
        if i == index or result.merchant != current_result.merchant:
            continue

        txn_date = datetime.fromisoformat(txn.date)
        if not (window_start <= txn_date < current_date):
            continue

        diff_ratio = abs(abs(txn.montant) - current_amount) / current_amount
        if diff_ratio <= amount_tolerance:
            similar_count += 1

    return similar_count >= 1
