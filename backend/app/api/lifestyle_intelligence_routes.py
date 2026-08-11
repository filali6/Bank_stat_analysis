from fastapi import APIRouter, Depends

from app.core.dependencies import get_lifestyle_intelligence_service
from app.schemas.transaction import ClientFeaturesInput, LifestyleFeatures
from app.services.lifestyle_intelligence_service import LifestyleIntelligenceService

router = APIRouter(prefix="/lifestyle-intelligence", tags=["lifestyle-intelligence"])


@router.post("/compute", response_model=LifestyleFeatures)
async def compute_lifestyle(
    payload: ClientFeaturesInput,
    service: LifestyleIntelligenceService = Depends(get_lifestyle_intelligence_service),
) -> LifestyleFeatures:
    """Takes the ClientFeatures already produced by
    /feature-engineering/compute and turns them into a scorecard +
    lifestyle segment — no re-computation of the previous steps, just
    chains onto their result.
    """
    return service.compute(payload.features)