from typing import List

import pytest

from app.repositories.merchant_repository import Merchant


class FakeMerchantRepository:
    """An in-memory stand-in for MerchantRepository. Matcher tests use
    this fixed, hand-picked merchant list instead of the real
    merchant_db.json — so they only fail when a matcher's own logic
    breaks, never because someone (rightfully) added, removed, or
    edited a merchant in the production data file.
    """

    def __init__(self, merchants: List[Merchant]):
        self._merchants = merchants

    def get_all(self) -> List[Merchant]:
        return self._merchants


@pytest.fixture
def merchant_repository() -> FakeMerchantRepository:
    return FakeMerchantRepository(
        [
            Merchant(
                name="Netflix",
                patterns=["NETFLIX", "NFLX*COM", "NFLX COM"],
                category="Entertainment",
                subcategory="Streaming",
                channel="Card Online",
                type="Subscription",
                recurring=True,
                income=False,
            ),
            Merchant(
                name="Starbucks",
                patterns=["STARBUCKS", "STRBCKS"],
                category="Food",
                subcategory="Coffee",
                channel="Card POS",
                type="Purchase",
                recurring=False,
                income=False,
            ),
            Merchant(
                name="Uber",
                patterns=["UBER"],
                category="Transport",
                subcategory="Rideshare",
                channel="Card Online",
                type="Purchase",
                recurring=False,
                income=False,
            ),
            Merchant(
                name="Planet Fitness",
                patterns=["PLANET FITNESS"],
                category="Health",
                subcategory="Gym",
                channel="Card POS",
                type="Subscription",
                recurring=True,
                income=False,
            ),
        ]
    )