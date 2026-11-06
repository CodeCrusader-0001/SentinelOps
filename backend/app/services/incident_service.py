from typing import Optional, List, Tuple
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import or_
from backend.app.models.incident import Incident
from backend.app.models.log import Log
from backend.app.schemas.incident import IncidentCreate, IncidentUpdate

class IncidentService:
    @staticmethod
    def create_incident(db: Session, incident_in: IncidentCreate) -> Incident:
        # Deduplication check
        if incident_in.deduplication_key:
            existing = db.query(Incident).filter(
                Incident.deduplication_key == incident_in.deduplication_key,
                Incident.status.in_(["OPEN", "INVESTIGATING", "PENDING_APPROVAL", "REMEDIATING"])
            ).first()
            if existing:
                # Correlate logs to existing incident rather than duplicate
                if incident_in.log_ids:
                    db.query(Log).filter(Log.id.in_(incident_in.log_ids)).update(
                        {"incident_id": existing.id},
                        synchronize_session=False
                    )
                    db.commit()
                return existing

        incident = Incident(
            title=incident_in.title,
            description=incident_in.description,
            severity=incident_in.severity.upper(),
            status="OPEN",
            source=incident_in.source,
            deduplication_key=incident_in.deduplication_key,
            assigned_engineer_id=incident_in.assigned_engineer_id
        )
        db.add(incident)
        db.commit()
        db.refresh(incident)

        if incident_in.log_ids:
            db.query(Log).filter(Log.id.in_(incident_in.log_ids)).update(
                {"incident_id": incident.id},
                synchronize_session=False
            )
            db.commit()
            db.refresh(incident)

        return incident

    @staticmethod
    def get_by_id(db: Session, incident_id: str) -> Optional[Incident]:
        return db.query(Incident).filter(Incident.id == incident_id).first()

    @staticmethod
    def list_incidents(
        db: Session,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        assigned_engineer_id: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[int, List[Incident]]:
        query = db.query(Incident)
        if status:
            query = query.filter(Incident.status == status.upper())
        if severity:
            query = query.filter(Incident.severity == severity.upper())
        if assigned_engineer_id:
            query = query.filter(Incident.assigned_engineer_id == assigned_engineer_id)
        if search:
            query = query.filter(
                or_(
                    Incident.title.ilike(f"%{search}%"),
                    Incident.description.ilike(f"%{search}%"),
                    Incident.source.ilike(f"%{search}%")
                )
            )

        total = query.count()
        items = query.order_by(Incident.created_at.desc()).offset((page - 1) * size).limit(size).all()
        return total, items

    @staticmethod
    def update_incident(db: Session, incident: Incident, update_in: IncidentUpdate) -> Incident:
        if update_in.title is not None:
            incident.title = update_in.title
        if update_in.description is not None:
            incident.description = update_in.description
        if update_in.severity is not None:
            incident.severity = update_in.severity.upper()
        if update_in.status is not None:
            incident.status = update_in.status.upper()
        if update_in.assigned_engineer_id is not None:
            incident.assigned_engineer_id = update_in.assigned_engineer_id
            
        incident.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(incident)
        return incident

    @staticmethod
    def assign_incident(db: Session, incident: Incident, engineer_id: str) -> Incident:
        incident.assigned_engineer_id = engineer_id
        incident.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(incident)
        return incident

    @staticmethod
    def resolve_incident(db: Session, incident: Incident, resolution_notes: Optional[str] = None) -> Incident:
        incident.status = "RESOLVED"
        if resolution_notes:
            incident.description += f"\n\n[Resolution Note]: {resolution_notes}"
        incident.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(incident)
        return incident
