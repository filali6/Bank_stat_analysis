from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.db.models import Study


class StudyRepository:
    """Reads and writes Study rows."""

    def __init__(self, db: Session):
        self._db = db

    def create(self, study: Study) -> Study:
        self._db.add(study)
        self._db.commit()
        self._db.refresh(study)
        return study

    def get_by_id(self, study_id: int) -> Optional[Study]:
        return (
            self._db.query(Study)
            .options(joinedload(Study.client))
            .filter(Study.id == study_id)
            .one_or_none()
        )

    def list_all(self) -> List[Study]:
        """Newest first, with the client already loaded — the
        Dashboard needs the client's label for every row."""
        return list(
            self._db.query(Study)
            .options(joinedload(Study.client))
            .order_by(Study.created_at.desc())
            .all()
        )

    def list_for_client(self, client_id: int) -> List[Study]:
        return list(
            self._db.query(Study)
            .filter(Study.client_id == client_id)
            .order_by(Study.created_at.desc())
            .all()
        )