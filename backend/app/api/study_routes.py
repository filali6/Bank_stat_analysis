from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_client_repository, get_study_service
from app.repositories.client_repository import ClientRepository,format_client_number
from app.schemas.study import ClientOut, SaveStudyRequest, StudyOut, StudySummary
from app.services.study_service import StudyService

router = APIRouter(tags=["studies"])


@router.get("/clients", response_model=List[ClientOut])
async def list_clients(repository: ClientRepository = Depends(get_client_repository)) -> List[ClientOut]:
    """For the client picker shown when starting a new study (FR-A2)."""
    return [
        ClientOut(
            id=c.id,
            client_number=format_client_number(c.id),
            label=c.label,
            created_at=c.created_at,
            monitoring_enabled=c.monitoring_enabled,
        )
        for c in repository.list_all()
    ]


@router.post("/studies", response_model=StudyOut)
async def save_study(
    payload: SaveStudyRequest,
    service: StudyService = Depends(get_study_service),
) -> StudyOut:
    """Persists a completed study, at the moment the analyst confirms
    a decision (FR-A16, FR-A17). Creates the client on the fly if
    `new_client_label` was given instead of an existing `client_id`.
    """
    try:
        return service.save_study(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/studies", response_model=List[StudySummary])
async def list_studies(service: StudyService = Depends(get_study_service)) -> List[StudySummary]:
    """Powers the Dashboard's study history table."""
    return service.list_studies()


@router.get("/studies/{study_id}", response_model=StudyOut)
async def get_study(study_id: int, service: StudyService = Depends(get_study_service)) -> StudyOut:
    """Not yet wired into the frontend — available for a future
    'reopen a past study' screen (FR-A12)."""
    try:
        return service.get_study(study_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))