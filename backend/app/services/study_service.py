from typing import List

from app.db.models import Study
from app.repositories.client_repository import ClientRepository, format_client_number
from app.repositories.study_repository import StudyRepository
from app.schemas.study import SaveStudyRequest, StudyOut, StudySummary


class StudyService:
    """Orchestrates saving a completed study and reading them back.
    Thin by design — ClientRepository/StudyRepository already do the
    real persistence work; this just resolves the client and maps ORM
    rows to the API's Pydantic shapes.
    """

    def __init__(self, client_repository: ClientRepository, study_repository: StudyRepository):
        self._clients = client_repository
        self._studies = study_repository

    def save_study(self, payload: SaveStudyRequest) -> StudyOut:
        if not payload.client_id and not payload.new_client_label:
            raise ValueError("Either client_id or new_client_label must be provided")

        client = self._clients.get_or_create(payload.client_id, payload.new_client_label)

        study = Study(
            client_id=client.id,
            output_type=payload.output_type,
            enrichment_result=payload.enrichment_result,
            categorization_result=payload.categorization_result,
            client_features=payload.client_features,
            lifestyle_features=payload.lifestyle_features,
            decision_result=payload.decision_result,
            decision_choice=payload.decision_choice,
            decision_comment=payload.decision_comment,
        )
        study = self._studies.create(study)

        return self._to_study_out(study, client.label)

    def list_studies(self) -> List[StudySummary]:
        studies = self._studies.list_all()
        return [
            StudySummary(
                id=s.id,
                client_number=format_client_number(s.client_id),
                client_label=s.client.label,
                created_at=s.created_at,
                output_type=s.output_type,
                headline=s.decision_result.get("headline", ""),
                decision_choice=s.decision_choice,
            )
            for s in studies
        ]

    def get_study(self, study_id: int) -> StudyOut:
        study = self._studies.get_by_id(study_id)
        if study is None:
            raise ValueError(f"Study {study_id} not found")
        return self._to_study_out(study, study.client.label)

    @staticmethod
    def _to_study_out(study: Study, client_label: str) -> StudyOut:
        return StudyOut(
            id=study.id,
            client_id=study.client_id,
            client_number=format_client_number(study.client_id),
            client_label=client_label,
            created_at=study.created_at,
            output_type=study.output_type,
            source=study.source,
            enrichment_result=study.enrichment_result,
            categorization_result=study.categorization_result,
            client_features=study.client_features,
            lifestyle_features=study.lifestyle_features,
            decision_result=study.decision_result,
            decision_choice=study.decision_choice,
            decision_comment=study.decision_comment,
        )