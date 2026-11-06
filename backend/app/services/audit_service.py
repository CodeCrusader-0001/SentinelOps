from typing import Optional, Dict, Any, Tuple, List
from sqlalchemy.orm import Session
from backend.app.models.audit import AuditLog
from backend.app.models.user import User

class AuditService:
    @staticmethod
    def record(
        db: Session,
        action: str,
        target_resource: str,
        resource_id: Optional[str] = None,
        user: Optional[User] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        audit_entry = AuditLog(
            user_id=user.id if user else None,
            user_email=user.email if user else "system",
            action=action,
            target_resource=target_resource,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address
        )
        db.add(audit_entry)
        db.commit()
        db.refresh(audit_entry)
        return audit_entry

    @staticmethod
    def list_logs(
        db: Session,
        page: int = 1,
        size: int = 50,
        action: Optional[str] = None,
        target_resource: Optional[str] = None
    ) -> Tuple[int, List[AuditLog]]:
        query = db.query(AuditLog)
        if action:
            query = query.filter(AuditLog.action == action)
        if target_resource:
            query = query.filter(AuditLog.target_resource == target_resource)
            
        total = query.count()
        items = query.order_by(AuditLog.timestamp.desc()).offset((page - 1) * size).limit(size).all()
        return total, items
