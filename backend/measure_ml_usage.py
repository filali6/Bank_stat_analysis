"""Mesure, sur un vrai relevé CSV, quelle part des transactions est
résolue par le dictionnaire (merchant_db.json) vs par le modèle ML.

Usage :
    python measure_ml_usage.py chemin/vers/mon_releve.csv

Utilise exactement le même parsing CSV et les mêmes services que
l'application réelle (voir app/api/enrichment_routes.py) — le résultat
reflète donc fidèlement ce qui se passerait en uploadant ce même
fichier dans l'app.
"""
import csv
import io
import sys

from app.core.config import settings
from app.repositories.merchant_repository import MerchantRepository
from app.repositories.business_lifestyle_repository import BusinessLifestyleRepository
from app.repositories.category_model_repository import CategoryModelRepository
from app.services.matchers.exact_matcher import ExactMatcher
from app.services.matchers.fuzzy_matcher import FuzzyMatcher
from app.services.matchers.tfidf_matcher import TfidfMatcher
from app.services.merchant_identifier import MerchantIdentifier
from app.services.enrichment_service import EnrichmentService
from app.services.categorization_service import CategorizationService
from app.schemas.transaction import TransactionIn


def parse_transactions_csv(content: str) -> list[TransactionIn]:
    """Copie exacte de la fonction utilisée par /enrichment/enrich."""
    reader = csv.DictReader(io.StringIO(content))
    return [
        TransactionIn(
            transaction_id=f"TXN{i:06d}",
            date=(row.get("date") or "").strip(),
            libelle_brut=(row.get("libelle_brut") or row.get("description") or "").strip(),
            montant=float(row.get("montant") or row.get("amount") or 0),
            mcc_code=row.get("mcc_code") or None,
        )
        for i, row in enumerate(reader)
        if (row.get("libelle_brut") or row.get("description"))
    ]


def main(csv_path: str) -> None:
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        content = f.read()

    transactions = parse_transactions_csv(content)
    if not transactions:
        print("Aucune transaction exploitable trouvée dans ce fichier.")
        return

    merchant_repo = MerchantRepository(settings.merchant_db_path)
    identifier = MerchantIdentifier([
        ExactMatcher(merchant_repo),
        FuzzyMatcher(merchant_repo, threshold=settings.fuzzy_threshold),
        TfidfMatcher(merchant_repo, threshold=settings.tfidf_threshold),
    ])
    enrichment_service = EnrichmentService(identifier)

    business_lifestyle_repo = BusinessLifestyleRepository(settings.business_lifestyle_mapping_path)
    model_repo = CategoryModelRepository(settings.category_model_bundle_path)
    categorization_service = CategorizationService(merchant_repo, business_lifestyle_repo, model_repo)

    enrichment_result = enrichment_service.enrich(transactions)
    categorization_result = categorization_service.categorize(enrichment_result.transactions)

    dictionary_count = sum(1 for t in categorization_result.transactions if t.confidence >= 0.99)
    ml_count = len(categorization_result.transactions) - dictionary_count
    total = len(categorization_result.transactions)

    print(f"Fichier analysé : {csv_path}")
    print(f"Total transactions : {total}")
    print()
    print(f"Résolues via le DICTIONNAIRE : {dictionary_count} ({dictionary_count / total * 100:.1f}%)")
    print(f"Résolues via le MODÈLE ML :    {ml_count} ({ml_count / total * 100:.1f}%)")

    if ml_count > 0:
        print()
        print("Exemples de transactions passées par le ML :")
        shown = 0
        for t in categorization_result.transactions:
            if t.confidence < 0.99 and shown < 5:
                print(f"  - {t.libelle_brut!r} -> {t.category} / {t.subcategory} (confiance {t.confidence:.2f})")
                shown += 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage : python measure_ml_usage.py chemin/vers/mon_releve.csv")
        sys.exit(1)
    main(sys.argv[1])