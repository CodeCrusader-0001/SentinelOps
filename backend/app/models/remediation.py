import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.session import Base

class RemediationRequest(Base):
    __tablename__ = "remediation_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    
    action_type: Mapped[str] = mapped_column(String(100), nullable=False) # restart_service, clear_cache, scale_workers, run_health_check
    parameters: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(50), default="LOW", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", index=True, nullable=False) # PENDING, APPROVED, REJECTED, EXECUTED, FAILED
    
    requested_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True) # "LangGraph Agent" or User ID
    approved_by: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
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

    # Relationships
    incident = relationship("Incident", back_populates="remediation_requests")
    approved_by_user = relationship("User", back_populates="remediations_approved", foreign_keys=[approved_by])
    execution = relationship("RemediationExecution", back_populates="request", uselist=False, cascade="all, delete-orphan")


class RemediationExecution(Base):
    __tablename__ = "remediation_executions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("remediation_requests.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False
    )
    
    status: Mapped[str] = mapped_column(String(50), default="RUNNING", nullable=False) # RUNNING, SUCCESS, FAILED
    output: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recovery_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verification_details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    executed_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationship
    request = relationship("RemediationRequest", back_populates="execution")
