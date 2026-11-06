from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks, Request
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
    IncidentAssignRequest,
    IncidentResolveRequest,
    IncidentResponse,
    IncidentListResponse,
)
from backend.app.services.incident_service import IncidentService
from backend.app.services.audit_service import AuditService
from backend.app.api.deps import get_current_user, require_role
from backend.app.models.user import User

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
def create_incident(
    incident_in: IncidentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "IT Engineer"]))
):
    incident = IncidentService.create_incident(db, incident_in)
    AuditService.record(
        db=db,
        action="INCIDENT_CREATED",
        target_resource="Incident",
        resource_id=incident.id,
        user=current_user,
        details={"title": incident.title, "severity": incident.severity},
        ip_address=request.client.host if request.client else None
    )
    return incident

@router.get("", response_model=IncidentListResponse)
def list_incidents(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    severity: Optional[str] = None,
    assigned_engineer_id: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total, items = IncidentService.list_incidents(
        db=db,
        page=page,
        size=size,
        status=status,
        severity=severity,
        assigned_engineer_id=assigned_engineer_id,
        search=search
    )
    return {
        "total": total,
        "items": items,
        "page": page,
        "size": size
    }

@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(
    incident_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    incident = IncidentService.get_by_id(db, incident_id)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found."
        )
    return incident

@router.patch("/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: str,
    update_in: IncidentUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "IT Engineer"]))
):
    incident = IncidentService.get_by_id(db, incident_id)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found."
        )
    updated = IncidentService.update_incident(db, incident, update_in)
    AuditService.record(
        db=db,
        action="INCIDENT_UPDATED",
        target_resource="Incident",
        resource_id=incident.id,
        user=current_user,
        details=update_in.model_dump(exclude_unset=True),
        ip_address=request.client.host if request.client else None
    )
    return updated

@router.post("/{incident_id}/assign", response_model=IncidentResponse)
def assign_incident(
    incident_id: str,
    assign_in: IncidentAssignRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "IT Engineer"]))
):
    incident = IncidentService.get_by_id(db, incident_id)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found."
        )
    assigned = IncidentService.assign_incident(db, incident, assign_in.engineer_id)
    AuditService.record(
        db=db,
        action="INCIDENT_ASSIGNED",
        target_resource="Incident",
        resource_id=incident.id,
        user=current_user,
        details={"assigned_engineer_id": assign_in.engineer_id},
        ip_address=request.client.host if request.client else None
    )
    return assigned

@router.post("/{incident_id}/resolve", response_model=IncidentResponse)
def resolve_incident(
    incident_id: str,
    resolve_in: IncidentResolveRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "IT Engineer"]))
):
    incident = IncidentService.get_by_id(db, incident_id)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found."
        )
    resolved = IncidentService.resolve_incident(db, incident, resolve_in.resolution_notes)
    AuditService.record(
        db=db,
        action="INCIDENT_RESOLVED",
        target_resource="Incident",
        resource_id=incident.id,
        user=current_user,
        details={"notes": resolve_in.resolution_notes},
        ip_address=request.client.host if request.client else None
    )
    return resolved

@router.post("/{incident_id}/investigate")
def trigger_investigation(
    incident_id: str,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "IT Engineer"]))
):
    incident = IncidentService.get_by_id(db, incident_id)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found."
        )
        
    incident.status = "INVESTIGATING"
    db.commit()
    
    AuditService.record(
        db=db,
        action="INCIDENT_INVESTIGATION_TRIGGERED",
        target_resource="Incident",
        resource_id=incident.id,
        user=current_user,
        ip_address=request.client.host if request.client else None
    )
    
    # Asynchronously execute LangGraph investigation agent
    try:
        from backend.app.workers.tasks import run_investigation_task
        task = run_investigation_task.delay(incident.id)
        task_id = task.id
    except Exception:
        from backend.app.agents.workflow import run_investigation_pipeline_sync
        background_tasks.add_task(run_investigation_pipeline_sync, incident.id)
        task_id = "local-background-task"
        
    return {
        "status": "Investigation dispatched",
        "incident_id": incident.id,
        "task_id": task_id
    }
