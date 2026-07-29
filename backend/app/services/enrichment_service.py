from typing import List

from app.schemas.transaction import EnrichedTransaction, EnrichmentResponse, TransactionIn
from app.services.business_rules import apply_business_rules
from app.services.merchant_identifier import MerchantIdentifier
from app.services.recurrence_detector import detect_recurring
from app.utils.text_normalization import normalize_text

VALIDATED_THRESHOLD = 85
REVIEW_THRESHOLD = 50


class EnrichmentService:
    """Coordinates the full pipeline for a batch of transactions:
    normalize -> identify merchant -> business rules -> recurrence ->
    final confidence/status.

    This is the only place that knows the full sequence of steps; every
    other class in this codebase does exactly one job. That's on purpose:
    it's the one file to read to understand "what happens to a
    transaction", and the one file to change if that sequence changes.
    """

    def __init__(self, identifier: MerchantIdentifier):
        self._identifier = identifier

    def enrich(self, transactions: List[TransactionIn]) -> EnrichmentResponse:
        raw_results = [
            apply_business_rules(
                txn.montant,
                self._identifier.identify(normalize_text(txn.libelle_brut)),
            )
            for txn in transactions
        ]

        enriched = [
            self._build_enriched_transaction(transactions, raw_results, i)
            for i in range(len(transactions))
        ]

        return self._build_response(enriched)

    def _build_enriched_transaction(
        self,
        transactions: List[TransactionIn],
        raw_results: List,
        index: int,
    ) -> EnrichedTransaction:
        txn = transactions[index]
        result = raw_results[index]

        recurring_detected = detect_recurring(transactions, raw_results, index)
        recurring = result.recurring or recurring_detected

        confidence = result.confidence
        if recurring_detected and result.recurring:
            confidence = min(confidence + 10, 99)
        if result.merchant == "Unknown":
            confidence = 0

        normalized_description = (
            f"{result.merchant} {result.subcategory}"
            if result.merchant != "Unknown"
            else "Unknown"
        )

        return EnrichedTransaction(
            transaction_id=txn.transaction_id,
            date=txn.date,
            libelle_brut=txn.libelle_brut,
            montant=txn.montant,
            merchant=result.merchant,
            category=result.category,
            subcategory=result.subcategory,
            payment_channel=result.channel,
            transaction_type=result.type,
            recurring=recurring,
            income_flag=result.income,
            normalized_description=normalized_description,
            confidence=confidence,
            status=self._status_for(confidence),
            matched_by=result.matched_by,
        )

    @staticmethod
    def _status_for(confidence: int) -> str:
        if confidence >= VALIDATED_THRESHOLD:
            return "validated"
        if confidence >= REVIEW_THRESHOLD:
            return "review"
        return "unknown"

    @staticmethod
    def _build_response(enriched: List[EnrichedTransaction]) -> EnrichmentResponse:
        total = len(enriched)
        validated = sum(1 for e in enriched if e.status == "validated")
        review = sum(1 for e in enriched if e.status == "review")
        unknown = sum(1 for e in enriched if e.status == "unknown")
        average_confidence = round(sum(e.confidence for e in enriched) / total, 1) if total else 0.0

        return EnrichmentResponse(
            total=total,
            validated=validated,
            review=review,
            unknown=unknown,
            average_confidence=average_confidence,
            transactions=enriched,
        )
