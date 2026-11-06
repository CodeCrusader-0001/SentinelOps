import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from backend.app.database.session import Base

class UserRole(str, enum.Enum):
    ADMIN = "Admin"
    IT_ENGINEER = "IT Engineer"
    VIEWER = "Viewer"

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default=UserRole.IT_ENGINEER.value, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
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
    assigned_incidents = relationship("Incident", back_populates="assigned_engineer", foreign_keys="Incident.assigned_engineer_id")
    audit_logs = relationship("AuditLog", back_populates="user")
    remediations_approved = relationship("RemediationRequest", back_populates="approved_by_user", foreign_keys="RemediationRequest.approved_by")
