from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.schemas.log import LogCreate, LogBatchCreate, LogResponse, LogListResponse
from backend.app.services.log_service import LogService
from backend.app.api.deps import get_current_user
from backend.app.models.user import User

router = APIRouter(prefix="/logs", tags=["Logs"])

def trigger_log_processing_pipeline(log_ids: List[str]):
    """Dispatches log batch to Celery worker if available, or processes via background thread."""
    from backend.app.workers.celery_app import is_broker_available
    from backend.app.workers.pipeline import run_pipeline_sync
    
    if is_broker_available():
        try:
            from backend.app.workers.tasks import process_log_batch_task
            process_log_batch_task.delay(log_ids)
            return
        except Exception:
            pass
            
    # Standalone / developer / offline worker fallback
    run_pipeline_sync(log_ids)

@router.post("", response_model=LogResponse, status_code=status.HTTP_202_ACCEPTED)
def ingest_log(
    log_in: LogCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    log = LogService.create_log(db, log_in, processing_status="PENDING")
    background_tasks.add_task(trigger_log_processing_pipeline, [log.id])
    return log

@router.post("/batch", response_model=List[LogResponse], status_code=status.HTTP_202_ACCEPTED)
def ingest_log_batch(
    batch_in: LogBatchCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    logs = LogService.create_batch(db, batch_in.logs, processing_status="PENDING")
    log_ids = [l.id for l in logs]
    background_tasks.add_task(trigger_log_processing_pipeline, log_ids)
    return logs

@router.get("", response_model=LogListResponse)
def list_logs(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    application: Optional[str] = None,
    service: Optional[str] = None,
    level: Optional[str] = None,
    processing_status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total, items = LogService.list_logs(
        db=db,
        page=page,
        size=size,
        application=application,
        service=service,
        level=level,
        processing_status=processing_status,
        search=search
    )
    return {
        "total": total,
        "items": items,
        "page": page,
        "size": size
    }

@router.get("/{log_id}", response_model=LogResponse)
def get_log(
    log_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    log = LogService.get_by_id(db, log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log record not found."
        )
    return log
