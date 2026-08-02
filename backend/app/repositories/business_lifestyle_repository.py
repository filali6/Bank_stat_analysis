import json
from pathlib import Path
from typing import Dict, Tuple


class BusinessLifestyleRepository:
    """Gives access to the category/subcategory → business_purpose/
    lifestyle_tag mapping. Same repository pattern as MerchantRepository:
    the rest of the code doesn't know or care that this comes from a
    JSON file today.
    """

    DEFAULT = ("Personal", "Uncategorized")

    def __init__(self, source_path: Path):
        self._source_path = source_path
        self._mapping: Dict[Tuple[str, str], Tuple[str, str]] | None = None

    def get_labels(self, category: str, subcategory: str) -> Tuple[str, str]:
        if self._mapping is None:
            self._mapping = self._load()
        return self._mapping.get((category, subcategory), self.DEFAULT)

    def _load(self) -> Dict[Tuple[str, str], Tuple[str, str]]:
        with open(self._source_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {
            (entry["category"], entry["subcategory"]): (entry["business_purpose"], entry["lifestyle_tag"])
            for entry in data["mapping"]
        }