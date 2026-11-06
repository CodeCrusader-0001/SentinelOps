from typing import Optional, List, Tuple
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import or_
from backend.app.models.log import Log
from backend.app.schemas.log import LogCreate

class LogService:
    @staticmethod
    def create_log(db: Session, log_in: LogCreate, processing_status: str = "PENDING") -> Log:
        log_obj = Log(
            application=log_in.application,
            service=log_in.service,
            level=log_in.level.upper(),
            message=log_in.message,
            hostname=log_in.hostname,
            timestamp=log_in.timestamp or datetime.now(timezone.utc),
            metadata_json=log_in.metadata_json,
            processing_status=processing_status
        )
        db.add(log_obj)
        db.commit()
        db.refresh(log_obj)
        return log_obj

    @staticmethod
    def create_batch(db: Session, logs_in: List[LogCreate], processing_status: str = "PENDING") -> List[Log]:
        log_objects = [
            Log(
                application=l.application,
                service=l.service,
                level=l.level.upper(),
                message=l.message,
                hostname=l.hostname,
                timestamp=l.timestamp or datetime.now(timezone.utc),
                metadata_json=l.metadata_json,
                processing_status=processing_status
            )
            for l in logs_in
        ]
        db.add_all(log_objects)
        db.commit()
        for l in log_objects:
            db.refresh(l)
        return log_objects

    @staticmethod
    def get_by_id(db: Session, log_id: str) -> Optional[Log]:
        return db.query(Log).filter(Log.id == log_id).first()

    @staticmethod
    def list_logs(
        db: Session,
        page: int = 1,
        size: int = 50,
        application: Optional[str] = None,
        service: Optional[str] = None,
        level: Optional[str] = None,
        processing_status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[int, List[Log]]:
        query = db.query(Log)
        if application:
            query = query.filter(Log.application == application)
        if service:
            query = query.filter(Log.service == service)
        if level:
            query = query.filter(Log.level == level.upper())
        if processing_status:
            query = query.filter(Log.processing_status == processing_status)
        if search:
            query = query.filter(
                or_(
                    Log.message.ilike(f"%{search}%"),
                    Log.service.ilike(f"%{search}%"),
                    Log.application.ilike(f"%{search}%")
                )
            )

        total = query.count()
        items = query.order_by(Log.timestamp.desc()).offset((page - 1) * size).limit(size).all()
        return total, items
