import csv
import io

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.core.dependencies import get_enrichment_service
from app.schemas.transaction import EnrichedTransaction, EnrichmentResponse, TransactionIn
from app.services.enrichment_service import EnrichmentService

router = APIRouter(prefix="/enrichment", tags=["enrichment"])


def _parse_transactions_csv(content: str) -> list[TransactionIn]:
    """Shared parsing logic between the JSON and CSV endpoints, so both
    stay consistent — one place to fix if the CSV format ever changes.
    """
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


@router.post("/enrich", response_model=EnrichmentResponse)
async def enrich_transactions(
    file: UploadFile = File(...),
    service: EnrichmentService = Depends(get_enrichment_service),
) -> EnrichmentResponse:
    """Accepts a CSV of raw transactions and returns them enriched as JSON.

    This is the endpoint the Angular frontend will call. Expected columns
    (case-insensitive, some aliases tolerated): date, libelle_brut (or
    description), montant (or amount), mcc_code.
    """
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Seuls les fichiers CSV sont acceptés pour le moment.")

    content = (await file.read()).decode("utf-8-sig")
    transactions = _parse_transactions_csv(content)

    if not transactions:
        raise HTTPException(status_code=400, detail="Le fichier ne contient aucune transaction exploitable.")

    return service.enrich(transactions)


@router.post("/enrich/csv")
async def enrich_transactions_as_csv(
    file: UploadFile = File(...),
    service: EnrichmentService = Depends(get_enrichment_service),
) -> StreamingResponse:
    """Same pipeline as /enrich, but returns a downloadable CSV instead of
    JSON. Handy for testing/inspecting results by hand before the Angular
    frontend exists — the frontend itself will use /enrich (JSON).
    """
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Seuls les fichiers CSV sont acceptés pour le moment.")

    content = (await file.read()).decode("utf-8-sig")
    transactions = _parse_transactions_csv(content)

    if not transactions:
        raise HTTPException(status_code=400, detail="Le fichier ne contient aucune transaction exploitable.")

    result = service.enrich(transactions)

    buffer = io.StringIO()
    fieldnames = list(EnrichedTransaction.model_fields.keys())
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for txn in result.transactions:
        writer.writerow(txn.model_dump())
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions_enriched.csv"},
    )