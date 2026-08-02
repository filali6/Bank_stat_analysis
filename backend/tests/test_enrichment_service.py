from app.core.dependencies import get_enrichment_service
from app.schemas.transaction import TransactionIn


def test_pipeline_enriches_a_known_recurring_merchant():
    service = get_enrichment_service()
    transactions = [
        TransactionIn(transaction_id="TXN000000", date="2025-10-05", libelle_brut="NETFLIX.COM IE", montant=-15.49),
        TransactionIn(transaction_id="TXN000001", date="2025-11-05", libelle_brut="NFLX*COM IE", montant=-15.49),
        TransactionIn(transaction_id="TXN000002", date="2025-12-05", libelle_brut="NETFLIX.COM IE", montant=-15.49),
    ]

    response = service.enrich(transactions)

    assert response.total == 3
    last_txn = response.transactions[-1]
    assert last_txn.merchant == "Netflix"
    # Confirmed by 2 prior occurrences within 90 days -> recurring detected
    assert last_txn.recurring is True


def test_pipeline_flags_unrecognized_labels_as_unknown():
    service = get_enrichment_service()
    transactions = [
        TransactionIn(transaction_id="TXN000000", date="2025-11-05", libelle_brut="PAIEMENT DIVERS 0049", montant=-52.30),
    ]

    response = service.enrich(transactions)

    txn = response.transactions[0]
    assert txn.merchant == "Unknown"
    


def test_pipeline_marks_positive_unknown_amount_as_credit():
    service = get_enrichment_service()
    transactions = [
        TransactionIn(transaction_id="TXN000000", date="2025-11-05", libelle_brut="REFUND MISC 123", montant=25.0),
    ]

    response = service.enrich(transactions)

    assert response.transactions[0].transaction_type == "Credit"
