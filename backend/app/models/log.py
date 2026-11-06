import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, Text, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.session import Base

class Log(Base):
    __tablename__ = "logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False
    )
    application: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    service: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    level: Mapped[str] = mapped_column(String(20), index=True, nullable=False) # INFO, WARNING, ERROR, CRITICAL, DEBUG
    message: Mapped[str] = mapped_column(Text, nullable=False)
    hostname: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    processing_status: Mapped[str] = mapped_column(String(50), default="PENDING", index=True, nullable=False)
    
    incident_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("incidents.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Relationship
    incident = relationship("Incident", back_populates="logs")

    __table_args__ = (
        Index("ix_logs_service_level", "service", "level"),
        Index("ix_logs_timestamp_desc", timestamp.desc()),
    )
