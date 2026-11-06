import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.session import Base

class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="MEDIUM", index=True, nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    status: Mapped[str] = mapped_column(String(50), default="OPEN", index=True, nullable=False) # OPEN, INVESTIGATING, PENDING_APPROVAL, REMEDIATING, RESOLVED, FAILED
    source: Mapped[str] = mapped_column(String(100), default="DeepLog Anomaly Detector", nullable=False)
    
    deduplication_key: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    
    assigned_engineer_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    assigned_engineer = relationship("User", back_populates="assigned_incidents", foreign_keys=[assigned_engineer_id])
    logs = relationship("Log", back_populates="incident", cascade="all, delete-orphan")
    anomalies = relationship("Anomaly", back_populates="incident")
    investigation_report = relationship("InvestigationReport", back_populates="incident", uselist=False, cascade="all, delete-orphan")
    remediation_requests = relationship("RemediationRequest", back_populates="incident", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_incidents_status_severity", "status", "severity"),
        Index("ix_incidents_created_desc", created_at.desc()),
    )
