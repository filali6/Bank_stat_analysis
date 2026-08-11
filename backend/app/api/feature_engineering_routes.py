from fastapi import APIRouter, Depends

from app.core.dependencies import get_feature_engineering_service
from app.schemas.transaction import CategorizedTransactionsInput, ClientFeatures
from app.services.feature_engineering_service import FeatureEngineeringService

router = APIRouter(prefix="/feature-engineering", tags=["feature-engineering"])


@router.post("/compute", response_model=ClientFeatures)
async def compute_features(
    payload: CategorizedTransactionsInput,
    feature_engineering: FeatureEngineeringService = Depends(get_feature_engineering_service),
) -> ClientFeatures:
    """Takes the transactions already produced by /categorization/categorize
    and computes the 6 client-level indicators — no re-computation of
    the previous steps, just chains onto their result.
    """
    return feature_engineering.compute(payload.transactions)