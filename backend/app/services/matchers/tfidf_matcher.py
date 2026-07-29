from typing import List, Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.repositories.merchant_repository import Merchant, MerchantRepository
from app.schemas.transaction import MatchResult
from app.services.matchers.base_matcher import Matcher


class TfidfMatcher(Matcher):
    """Level 3, last resort: compares a label to merchants by overall
    word-usage similarity rather than exact substrings, so it can catch
    generic/unfamiliar labels that share no exact keyword with anything
    (e.g. "LOCAL GYM NYC"). Slowest and least reliable of the three, so
    its confidence is deliberately capped lower than the other levels.
    """

    def __init__(self, repository: MerchantRepository, threshold: float = 0.3):
        self._repository = repository
        self._threshold = threshold
        self._vectorizer: Optional[TfidfVectorizer] = None
        self._matrix = None
        self._merchants: Optional[List[Merchant]] = None

    def _ensure_fitted(self) -> None:
        """Builds the TF-IDF vector space once, lazily, on first use —
        not on every request.
        """
        if self._vectorizer is not None:
            return

        merchants = self._repository.get_all()
        corpus = [
            f"{m.name} {' '.join(m.patterns)} {m.category} {m.subcategory}"
            for m in merchants
        ]

        self._vectorizer = TfidfVectorizer()
        self._matrix = self._vectorizer.fit_transform(corpus)
        self._merchants = merchants

    def match(self, libelle_norm: str) -> Optional[MatchResult]:
        self._ensure_fitted()

        vector = self._vectorizer.transform([libelle_norm])
        similarities = cosine_similarity(vector, self._matrix)[0]
        best_idx = int(np.argmax(similarities))
        best_score = float(similarities[best_idx])

        if best_score < self._threshold:
            return None

        merchant = self._merchants[best_idx]
        return MatchResult(
            merchant=merchant.name,
            category=merchant.category,
            subcategory=merchant.subcategory,
            channel=merchant.channel,
            type=merchant.type,
            recurring=merchant.recurring,
            income=merchant.income,
            confidence=int(best_score * 60),
            matched_by="tfidf",
            pattern=None,
        )
