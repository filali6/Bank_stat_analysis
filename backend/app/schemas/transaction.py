from typing import List, Optional

from pydantic import BaseModel


class TransactionIn(BaseModel):
    """A raw transaction, as it comes out of a bank statement export."""

    transaction_id: str
    date: str
    libelle_brut: str
    montant: float
    mcc_code: Optional[str] = None


class MatchResult(BaseModel):
    """What a single matcher (or the identifier chain) found out about
    a label — before business rules and recurrence detection touch it.
    """

    merchant: str
    category: str
    subcategory: str
    channel: str
    type: str
    recurring: bool
    income: bool
    confidence: int
    matched_by: Optional[str] = None
    pattern: Optional[str] = None


class EnrichedTransaction(BaseModel):
    """The final, enriched transaction — this is the shape the frontend
    (Angular) will consume, one row per transaction in the results table.
    """

    transaction_id: str
    date: str
    libelle_brut: str
    montant: float
    merchant: str
    payment_channel: str
    transaction_type: str
    recurring: bool
    income_flag: bool
    normalized_description: str


class EnrichmentResponse(BaseModel):
    """The full API response for a batch: summary stats + the enriched
    rows. Computing the summary server-side means every client (Angular
    today, maybe a mobile app tomorrow) gets the same numbers for free.
    """

    total: int
    transactions: List[EnrichedTransaction]
class CategorizedTransaction(EnrichedTransaction):
    """Extends EnrichedTransaction with the Categorization step's
    outputs — matches the schema's second stage exactly."""

    category: str
    subcategory: str
    business_purpose: str
    lifestyle_tag: str
    confidence: float


class CategorizationResponse(BaseModel):
    total: int
    transactions: List[CategorizedTransaction]