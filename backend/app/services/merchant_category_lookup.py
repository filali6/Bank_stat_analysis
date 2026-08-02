from typing import Optional, Tuple

from app.repositories.merchant_repository import MerchantRepository

UNKNOWN = ("Unknown", "Unknown")


def lookup_category_from_label(repository: MerchantRepository, libelle_norm: str) -> Optional[Tuple[str, str]]:
    """Looks up (category, subcategory) directly from the transaction's
    own normalized text — not from the merchant name alone, which would
    be ambiguous when several merchant entries share the same name
    (e.g. "Bank" for both mortgage and car loan payments).

    Shared between the training script and CategorizationService so
    both always agree on exactly how a category is determined.
    """
    for merchant in repository.get_all():
        for pattern in merchant.patterns:
            if pattern in libelle_norm:
                return (merchant.category, merchant.subcategory)
    return None