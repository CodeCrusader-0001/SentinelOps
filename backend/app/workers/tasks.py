from typing import List, Dict, Any
from backend.app.workers.celery_app import celery_app
from backend.app.workers.pipeline import run_pipeline_sync
from backend.app.core.logging import logger

@celery_app.task(
    bind=True,
    name="tasks.process_log_batch",
    max_retries=3,
    default_retry_delay=5,
    retry_backoff=True,
    autoretry_for=(Exception,)
)
def process_log_batch_task(self, log_ids: List[str]) -> Dict[str, Any]:
    logger.info(f"Celery task process_log_batch started for {len(log_ids)} logs (Task ID: {self.request.id})")
    try:
        result = run_pipeline_sync(log_ids)
        logger.info(f"Celery task completed successfully: {result}")
        return result
    except Exception as exc:
        logger.error(f"Task process_log_batch failed: {exc}. Retrying...")
        raise self.retry(exc=exc)

@celery_app.task(
    bind=True,
    name="tasks.run_investigation",
    max_retries=2,
    default_retry_delay=10,
    retry_backoff=True
)
def run_investigation_task(self, incident_id: str) -> Dict[str, Any]:
    logger.info(f"Starting async AI investigation for incident {incident_id}")
    try:
        from backend.app.agents.workflow import run_investigation_pipeline_sync
        result = run_investigation_pipeline_sync(incident_id)
        return {"status": "success", "result": result}
    except Exception as exc:
        logger.error(f"Investigation task for {incident_id} failed: {exc}")
        raise self.retry(exc=exc)

@celery_app.task(
    bind=True,
    name="tasks.execute_remediation",
    max_retries=1
)
def execute_remediation_task(self, request_id: str) -> Dict[str, Any]:
    logger.info(f"Starting safe remediation execution task for request {request_id}")
    try:
        from backend.app.remediation.service import remediation_service
        result = remediation_service.execute_request_sync(request_id)
        return {"status": "success", "execution": result}
    except Exception as exc:
        logger.error(f"Remediation task for {request_id} failed: {exc}")
        return {"status": "failed", "error": str(exc)}

