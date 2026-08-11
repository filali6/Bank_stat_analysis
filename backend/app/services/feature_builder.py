from typing import List

import pandas as pd
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer

from app.utils.text_normalization import normalize_text


class FeatureBuilder:
    """Turns raw enriched transactions into the numeric matrix the ML
    models expect: TF-IDF on the label + a few extra known signals
    (payment channel, type, amount, recurring). Used both by the
    training script (to build the training matrix) and by
    CategorizationService (to build features for a live transaction) —
    one place that guarantees both use the exact same transformation.
    """

    def __init__(self, vectorizer: TfidfVectorizer, feature_columns: List[str]):
        self._vectorizer = vectorizer
        self._feature_columns = feature_columns

    def build(self, df: pd.DataFrame):
        libelle_norm = df["libelle_brut"].apply(normalize_text)
        text_features = self._vectorizer.transform(libelle_norm)

        extra = pd.get_dummies(df[["payment_channel", "transaction_type"]])
        extra["montant_abs"] = df["montant"].abs()
        extra["recurring_flag"] = df["recurring"].astype(int)

        # Reindex to the exact columns seen during training, in the same
        # order — a transaction with a channel never seen during training
        # would otherwise silently break the model's expected input shape.
        extra = extra.reindex(columns=self._feature_columns, fill_value=0).astype(float)

        return hstack([text_features, extra.values]).tocsr()