from typing import List, Tuple

import numpy as np
import pandas as pd

from app.repositories.business_lifestyle_repository import BusinessLifestyleRepository
from app.repositories.category_model_repository import CategoryModelRepository
from app.repositories.merchant_repository import MerchantRepository
from app.schemas.transaction import CategorizedTransaction, CategorizationResponse, EnrichedTransaction
from app.services.feature_builder import FeatureBuilder
from app.services.merchant_category_lookup import lookup_category_from_label
from app.utils.text_normalization import normalize_text

DICTIONARY_CONFIDENCE = 0.99
VALIDATED_THRESHOLD = 0.85
REVIEW_THRESHOLD = 0.50


class CategorizationService:
    """Ensemble classification: known merchant → dictionary. Unknown
    merchant → ML. category_subcategory is predicted as ONE combined
    target (not two separate models) so the model can never invent a
    combination it has never actually seen (e.g. "Food · Electronics").
    """

    def __init__(
        self,
        merchant_repository: MerchantRepository,
        business_lifestyle_repository: BusinessLifestyleRepository,
        category_model_repository: CategoryModelRepository,
    ):
        self._merchants = merchant_repository
        self._business_lifestyle = business_lifestyle_repository
        self._models = category_model_repository
        self._feature_builder = FeatureBuilder(
            vectorizer=category_model_repository.vectorizer,
            feature_columns=category_model_repository.feature_columns,
        )

    def categorize(self, transactions: List[EnrichedTransaction]) -> CategorizationResponse:
        df = pd.DataFrame([t.model_dump() for t in transactions])
        feature_matrix = self._feature_builder.build(df)

        categorized = [
            self._categorize_one(transactions[i], feature_matrix[i])
            for i in range(len(transactions))
        ]

        return self._build_response(categorized)

    def _categorize_one(self, txn: EnrichedTransaction, feature_row) -> CategorizedTransaction:
        libelle_norm = normalize_text(txn.libelle_brut)
        known = lookup_category_from_label(self._merchants, libelle_norm)

        if known is not None:
            category, subcategory = known
            business_purpose, lifestyle_tag = self._business_lifestyle.get_labels(category, subcategory)
            confidence = DICTIONARY_CONFIDENCE
        else:
            combo, combo_conf = self._predict("category_subcategory", feature_row)
            category, subcategory = self._split_combo(combo)
            business_purpose, bp_conf = self._predict("business_purpose", feature_row)
            lifestyle_tag, lt_conf = self._predict("lifestyle_tag", feature_row)
            confidence = min(combo_conf, bp_conf, lt_conf)

        return CategorizedTransaction(
            **txn.model_dump(),
            category=category,
            subcategory=subcategory,
            business_purpose=business_purpose,
            lifestyle_tag=lifestyle_tag,
            confidence=round(confidence, 4),
            status=self._compute_status(confidence),
        )
    @staticmethod
    def _compute_status(confidence: float) -> str:
        if confidence >= VALIDATED_THRESHOLD:
            return "validated"
        if confidence >= REVIEW_THRESHOLD:
            return "needs_review"
        return "unreliable"
    def _split_combo(self, combo: str) -> Tuple[str, str]:
        separator = self._models.combo_separator
        if separator in combo:
            category, subcategory = combo.split(separator, 1)
            return category, subcategory
        return combo, "Unknown"

    def _predict(self, target: str, feature_row) -> Tuple[str, float]:
        entry = self._models.get_model_entry(target)

        if entry["model"] is None:
            return entry["constant_value"], 1.0

        proba = entry["model"].predict_proba(feature_row)[0]
        best_index = int(np.argmax(proba))
        label = entry["label_encoder"].inverse_transform([best_index])[0]
        return label, float(proba[best_index])

    @staticmethod
    def _build_response(categorized: List[CategorizedTransaction]) -> CategorizationResponse:
        return CategorizationResponse(total=len(categorized), transactions=categorized)