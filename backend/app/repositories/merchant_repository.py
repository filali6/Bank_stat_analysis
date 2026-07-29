import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass(frozen=True)
class Merchant:
    """One entry of the merchant reference data — the 'ground truth'
    every matcher tries to recognize from a raw label.
    """

    name: str
    patterns: List[str]
    category: str
    subcategory: str
    channel: str
    type: str
    recurring: bool
    income: bool


class MerchantRepository:
    """Gives access to the merchant reference data.

    Today the data lives in a JSON file. Tomorrow it could come from a
    real database or an external service — nothing outside this class
    needs to know or change when that happens. That's the point of a
    repository: it isolates "where the data lives" from "how it's used".
    """

    def __init__(self, source_path: Path):
        self._source_path = source_path
        self._merchants: Optional[List[Merchant]] = None

    def get_all(self) -> List[Merchant]:
        if self._merchants is None:
            self._merchants = self._load()
        return self._merchants

    def _load(self) -> List[Merchant]:
        with open(self._source_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [Merchant(**entry) for entry in data["merchants"]]
