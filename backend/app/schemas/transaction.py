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
    

class ClientFeatures(BaseModel):
    """The 6 outputs of the Feature Engineering step — pure statistics
    computed over a client's full categorized transaction history, no
    machine learning involved (unlike Categorization)."""

    monthly_income: float
    savings_rate: float
    travel_spend_ratio: float
    grocery_spend_ratio: float
    recurring_commitments: float
    atm_withdrawal_ratio: float
    

class CategorizedTransactionsInput(BaseModel):
    """Wraps a list of already-categorized transactions — used to CHAIN
    Feature Engineering onto the previous step's result, instead of
    re-running Enrichment+Categorization from scratch."""

    transactions: List[CategorizedTransaction]

class LifestyleFeatures(BaseModel):
    """The 6 outputs of the Lifestyle Intelligence step — a scorecard
    and rule-based interpretation of the client's already-computed
    financial indicators. No ML: explainability comes "by construction"
    (each score is returned together with the reasons that produced
    it), unlike Categorization where SHAP would explain a real trained
    model after the fact.
    """

    lifestyle_segment: str
    affluence_score: float
    financial_discipline_score: float
    travel_activity_index: str
    family_responsibility_index: str
    overall_lifestyle_index: float
    reasons: List[str]


class ClientFeaturesInput(BaseModel):
    """Wraps the Feature Engineering result — used to chain Lifestyle
    Intelligence onto the previous step, same pattern as
    CategorizedTransactionsInput."""

    features: ClientFeatures