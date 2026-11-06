from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.remediation import RemediationRequest
from backend.app.schemas.remediation import (
    RemediationRequestResponse,
    RemediationRejectRequest,
    RemediationExecutionResponse
)
from backend.app.remediation.service import remediation_service
from backend.app.api.deps import get_current_user, require_role
from backend.app.models.user import User

router = APIRouter(prefix="/remediations", tags=["Remediation"])

@router.get("", response_model=List[RemediationRequestResponse])
def list_remediation_requests(
    incident_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(RemediationRequest)
    if incident_id:
        query = query.filter(RemediationRequest.incident_id == incident_id)
    if status:
        query = query.filter(RemediationRequest.status == status.upper())
    return query.order_by(RemediationRequest.created_at.desc()).all()

@router.get("/{request_id}", response_model=RemediationRequestResponse)
def get_remediation_request(
    request_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    req = db.query(RemediationRequest).filter(RemediationRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Remediation request not found")
    return req

@router.post("/{request_id}/approve", response_model=RemediationRequestResponse)
def approve_remediation(
    request_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "IT Engineer"]))
):
    try:
        approved = remediation_service.approve_request(db, request_id, current_user)
        # Immediately trigger execution upon human approval
        remediation_service.execute_request_sync(approved.id)
        db.refresh(approved)
        return approved
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/{request_id}/reject", response_model=RemediationRequestResponse)
def reject_remediation(
    request_id: str,
    reject_in: RemediationRejectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "IT Engineer"]))
):
    try:
        rejected = remediation_service.reject_request(db, request_id, current_user, reject_in.reason)
        return rejected
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

