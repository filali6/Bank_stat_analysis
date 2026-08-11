from app.repositories.business_lifestyle_repository import BusinessLifestyleRepository
from app.repositories.merchant_repository import MerchantRepository
from app.services.merchant_category_lookup import lookup_category_from_label
from app.utils.text_normalization import normalize_text
from app.core.config import settings


def test_known_merchant_resolves_category_from_dictionary():
    repository = MerchantRepository(settings.merchant_db_path)
    result = lookup_category_from_label(repository, normalize_text("NETFLIX.COM IE"))

    assert result == ("Entertainment", "Streaming")


def test_business_lifestyle_mapping_has_a_default_for_unknown_pairs():
    repository = BusinessLifestyleRepository(settings.business_lifestyle_mapping_path)
    result = repository.get_labels("Nonexistent", "Category")

    assert result == ("Personal", "Uncategorized")