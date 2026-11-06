import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.session import Base

class InvestigationReport(Base):
    __tablename__ = "investigation_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False
    )
    
    executive_summary: Mapped[str] = mapped_column(Text, nullable=False)
    root_cause: Mapped[str] = mapped_column(Text, nullable=False)
    supporting_evidence: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    relevant_runbooks: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    recommended_actions: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    
    severity_assessment: Mapped[str] = mapped_column(String(20), default="MEDIUM", nullable=False)
    risk_assessment: Mapped[str] = mapped_column(String(50), default="LOW", nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.85, nullable=False)
    uncertainty_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    post_mortem: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    raw_llm_response: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationship
    incident = relationship("Incident", back_populates="investigation_report")
