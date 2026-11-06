from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.schemas.audit import AuditLogListResponse
from backend.app.services.audit_service import AuditService
from backend.app.api.deps import require_role
from backend.app.models.user import User

router = APIRouter(prefix="/audit", tags=["Audit Logs"])

@router.get("", response_model=AuditLogListResponse)
def list_audit_logs(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    action: Optional[str] = None,
    target_resource: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "IT Engineer"]))
):
    total, items = AuditService.list_logs(
        db=db,
        page=page,
        size=size,
        action=action,
        target_resource=target_resource
    )
    return {
        "total": total,
        "items": items,
        "page": page,
        "size": size
    }
