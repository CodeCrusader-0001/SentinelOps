from fastapi import APIRouter, HTTPException, Depends
from celery.result import AsyncResult
from backend.app.workers.celery_app import celery_app
from backend.app.api.deps import get_current_user
from backend.app.models.user import User

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("/{task_id}")
def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """Checks the status and result of a background Celery task."""
    try:
        task_result = AsyncResult(task_id, app=celery_app)
        response = {
            "task_id": task_id,
            "status": task_result.status,
            "ready": task_result.ready(),
            "successful": task_result.successful() if task_result.ready() else None
        }
        if task_result.ready():
            try:
                response["result"] = task_result.result if not isinstance(task_result.result, Exception) else str(task_result.result)
            except Exception:
                response["result"] = None
        return response
    except Exception as e:
        return {
            "task_id": task_id,
            "status": "UNKNOWN",
            "message": str(e)
        }

