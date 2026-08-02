from typing import List, Optional, Tuple

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


class CategorizationService:
    """Ensemble classification: if the merchant's category is already
    known with certainty from merchant_db.json, use it directly (fast,
    reliable). Otherwise, ask the trained ML models to guess — this is
    the same "known dictionary first, ML as fallback" principle already
    used in EnrichmentService's matcher chain, applied one level up.
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

        return CategorizationResponse(total=len(categorized), transactions=categorized)

    def _categorize_one(self, txn: EnrichedTransaction, feature_row) -> CategorizedTransaction:
        libelle_norm = normalize_text(txn.libelle_brut)
        known = lookup_category_from_label(self._merchants, libelle_norm)

        if known is not None:
            category, subcategory = known
            business_purpose, lifestyle_tag = self._business_lifestyle.get_labels(category, subcategory)
            confidence = DICTIONARY_CONFIDENCE
        else:
            category, cat_conf = self._predict("category", feature_row)
            subcategory, sub_conf = self._predict("subcategory", feature_row)
            lifestyle_tag, lt_conf = self._predict("lifestyle_tag", feature_row)
            # business_purpose has no real variation in our training data yet
            # (always "Personal") — kept as an honest constant rather than a
            # fake ML prediction. Revisit once training data includes
            # professional transactions.
            business_purpose = "Personal"
            confidence = min(cat_conf, sub_conf, lt_conf)

        return CategorizedTransaction(
            **txn.model_dump(),
            category=category,
            subcategory=subcategory,
            business_purpose=business_purpose,
            lifestyle_tag=lifestyle_tag,
            confidence=round(confidence, 4),
        )

    def _predict(self, target: str, feature_row) -> Tuple[str, float]:
        entry = self._models.get_model_entry(target)

        if entry["model"] is None:
            return entry["constant_value"], 1.0

        proba = entry["model"].predict_proba(feature_row)[0]
        best_index = int(np.argmax(proba))
        label = entry["label_encoder"].inverse_transform([best_index])[0]
        return label, float(proba[best_index])