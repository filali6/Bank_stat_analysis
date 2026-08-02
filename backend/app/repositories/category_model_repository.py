from pathlib import Path
from typing import Any, Dict, Optional

import joblib


class CategoryModelRepository:
    """Loads the single bundle file produced by the offline training
    script: the fitted TF-IDF vectorizer, the expected feature columns,
    the trained models (or constant fallback) per target, and their
    label encoders. Loaded once and cached — never re-trained here.
    """

    def __init__(self, bundle_path: Path):
        self._bundle_path = bundle_path
        self._bundle: Optional[Dict[str, Any]] = None

    def _get_bundle(self) -> Dict[str, Any]:
        if self._bundle is None:
            self._bundle = joblib.load(self._bundle_path)
        return self._bundle

    @property
    def vectorizer(self):
        return self._get_bundle()["vectorizer"]

    @property
    def feature_columns(self):
        return self._get_bundle()["feature_columns"]

    def get_model_entry(self, target: str) -> Dict[str, Any]:
        """Returns {'model': ..., 'label_encoder': ..., 'constant_value': ...}
        for a given target ('category', 'subcategory', 'lifestyle_tag').
        """
        return self._get_bundle()["targets"][target]