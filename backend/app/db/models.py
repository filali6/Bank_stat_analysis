from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Client(Base):
    

    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    monitoring_enabled: Mapped[bool] = mapped_column(default=False)

    studies: Mapped[List["Study"]] = relationship(back_populates="client", cascade="all, delete-orphan")


class Study(Base):
    

    __tablename__ = "studies"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    output_type: Mapped[str] = mapped_column(String(50))
    source: Mapped[str] = mapped_column(String(50), default="csv_upload")

    enrichment_result: Mapped[dict] = mapped_column(JSON)
    categorization_result: Mapped[dict] = mapped_column(JSON)
    client_features: Mapped[dict] = mapped_column(JSON)
    lifestyle_features: Mapped[dict] = mapped_column(JSON)
    decision_result: Mapped[dict] = mapped_column(JSON)

    decision_choice: Mapped[str] = mapped_column(String(20))
    decision_comment: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)

    client: Mapped["Client"] = relationship(back_populates="studies")