from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class ClientOut(BaseModel):
    id: int
    label: str
    created_at: datetime
    monitoring_enabled: bool

    model_config = {"from_attributes": True}


class SaveStudyRequest(BaseModel):
    """Persists one completed study — sent once, when the analyst
    confirms a decision (FR-A16, FR-A17). Exactly one of client_id /
    new_client_label must be set: pick an existing client (FR-A2's
    'file' already exists) or create a new one on the fly.
    """

    client_id: Optional[int] = None
    new_client_label: Optional[str] = None

    output_type: str
    enrichment_result: Dict[str, Any]
    categorization_result: Dict[str, Any]
    client_features: Dict[str, Any]
    lifestyle_features: Dict[str, Any]
    decision_result: Dict[str, Any]

    decision_choice: str
    decision_comment: Optional[str] = None


class StudyOut(BaseModel):
    id: int
    client_id: int
    client_label: str
    created_at: datetime
    output_type: str
    source: str
    enrichment_result: Dict[str, Any]
    categorization_result: Dict[str, Any]
    client_features: Dict[str, Any]
    lifestyle_features: Dict[str, Any]
    decision_result: Dict[str, Any]
    decision_choice: str
    decision_comment: Optional[str] = None


class StudySummary(BaseModel):
    """The lightweight shape the Dashboard's study table actually
    needs — avoids sending every step's full JSON blob just to list
    rows."""

    id: int
    client_label: str
    created_at: datetime
    output_type: str
    headline: str
    decision_choice: str