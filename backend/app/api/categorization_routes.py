from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.enrichment_routes import _parse_transactions_csv
from app.core.dependencies import get_categorization_service, get_enrichment_service
from app.schemas.transaction import CategorizationResponse
from app.services.categorization_service import CategorizationService
from app.services.enrichment_service import EnrichmentService

router = APIRouter(prefix="/categorization", tags=["categorization"])


@router.post("/categorize", response_model=CategorizationResponse)
async def categorize_transactions(
    file: UploadFile = File(...),
    enrichment: EnrichmentService = Depends(get_enrichment_service),
    categorization: CategorizationService = Depends(get_categorization_service),
) -> CategorizationResponse:
    """Runs the full pipeline in one call: Enrichment then
    Categorization. Keeps the two steps as separate services/classes —
    this route is just the composition of both, matching the two
    stages of the schema.
    """
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Seuls les fichiers CSV sont acceptés pour le moment.")

    content = (await file.read()).decode("utf-8-sig")
    transactions = _parse_transactions_csv(content)

    if not transactions:
        raise HTTPException(status_code=400, detail="Le fichier ne contient aucune transaction exploitable.")

    enriched = enrichment.enrich(transactions)
    return categorization.categorize(enriched.transactions)