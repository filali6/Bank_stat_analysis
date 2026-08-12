from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_decision_service
from app.schemas.transaction import AffordabilityRequest, AffordabilityResult, DecisionRequest, DecisionResult
from app.services.decision_service import DecisionService

router = APIRouter(prefix="/decision", tags=["decision"])

VALID_OUTPUT_TYPES = {"credit", "risk", "kyc", "opportunities"}


@router.post("/compute", response_model=DecisionResult)
async def compute_decision(
    payload: DecisionRequest,
    service: DecisionService = Depends(get_decision_service),
) -> DecisionResult:
    """Takes the output type chosen at the start of the study (FR-A3)
    plus the ClientFeatures/LifestyleFeatures already computed, and
    returns the matching decision view.
    """
    if payload.output_type not in VALID_OUTPUT_TYPES:
        raise HTTPException(status_code=400, detail=f"Unknown output_type: {payload.output_type}")
    return service.compute(payload.output_type, payload.features, payload.lifestyle)


@router.post("/check-affordability", response_model=AffordabilityResult)
async def check_affordability(
    payload: AffordabilityRequest,
    service: DecisionService = Depends(get_decision_service),
) -> AffordabilityResult:
    """FR-A7: enter a loan amount and duration to check if it's
    affordable. Separate from /compute so the analyst can try several
    amounts without recomputing the whole decision."""
    if payload.duration_months <= 0:
        raise HTTPException(status_code=400, detail="duration_months must be greater than 0")
    return service.check_affordability(payload.features, payload.loan_amount, payload.duration_months)