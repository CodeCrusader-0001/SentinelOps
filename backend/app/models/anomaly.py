import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.session import Base

class Anomaly(Base):
    __tablename__ = "anomalies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False
    )
    service: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    anomaly_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    actual_event: Mapped[str] = mapped_column(String(255), nullable=False)
    predicted_events: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    detection_method: Mapped[str] = mapped_column(String(50), default="deeplog", nullable=False) # deeplog or rule_based
    supporting_evidence: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    incident_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("incidents.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Relationship
    incident = relationship("Incident", back_populates="anomalies")
