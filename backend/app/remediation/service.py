from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy.orm import Session

from backend.app.models.remediation import RemediationRequest, RemediationExecution
from backend.app.models.incident import Incident
from backend.app.models.user import User
from backend.app.remediation.actions import RemediationExecutor
from backend.app.services.audit_service import AuditService
from backend.app.database.session import SessionLocal
from backend.app.core.logging import logger

class RemediationService:
    @staticmethod
    def create_request(
        db: Session,
        incident_id: str,
        action_type: str,
        parameters: Dict[str, Any],
        rationale: str,
        requested_by: str = "LangGraph Agent"
    ) -> RemediationRequest:
        req = RemediationRequest(
            incident_id=incident_id,
            action_type=action_type,
            parameters=parameters,
            rationale=rationale,
            requested_by=requested_by,
            status="PENDING"
        )
        db.add(req)
        db.commit()
        db.refresh(req)
        logger.info(f"Created remediation request {req.id} for incident {incident_id}: {action_type}")
        return req

    @staticmethod
    def approve_request(db: Session, request_id: str, user: User) -> RemediationRequest:
        req = db.query(RemediationRequest).filter(RemediationRequest.id == request_id).first()
        if not req:
            raise ValueError("Remediation request not found")

        req.status = "APPROVED"
        req.approved_by = user.id
        req.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(req)

        AuditService.record(
            db=db,
            action="REMEDIATION_APPROVED",
            target_resource="RemediationRequest",
            resource_id=req.id,
            user=user,
            details={"action_type": req.action_type, "incident_id": req.incident_id}
        )
        return req

    @staticmethod
    def reject_request(db: Session, request_id: str, user: User, reason: Optional[str] = None) -> RemediationRequest:
        req = db.query(RemediationRequest).filter(RemediationRequest.id == request_id).first()
        if not req:
            raise ValueError("Remediation request not found")

        req.status = "REJECTED"
        req.rejection_reason = reason or "Rejected by human engineer review."
        req.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(req)

        AuditService.record(
            db=db,
            action="REMEDIATION_REJECTED",
            target_resource="RemediationRequest",
            resource_id=req.id,
            user=user,
            details={"reason": req.rejection_reason}
        )
        return req

    @staticmethod
    def execute_request_sync(request_id: str) -> Dict[str, Any]:
        """
        Executes approved remediation action safely, verifies recovery,
        and logs audit trail.
        """
        db = SessionLocal()
        try:
            req = db.query(RemediationRequest).filter(RemediationRequest.id == request_id).first()
            if not req:
                return {"status": "FAILED", "error": "Request not found"}

            if req.status != "APPROVED":
                return {"status": "BLOCKED", "error": f"Request status is '{req.status}'. Must be APPROVED."}

            target = req.parameters.get("target_service") or req.parameters.get("service_name") or "default-service"
            
            # Create Execution record
            execution = RemediationExecution(
                request_id=req.id,
                status="RUNNING",
                executed_at=datetime.now(timezone.utc)
            )
            db.add(execution)
            db.commit()

            # Execute safe allowlisted action
            success, output = RemediationExecutor.execute(req.action_type, target, req.parameters)

            # Recovery verification step: execute health check
            _, health_output = RemediationExecutor.run_health_check(target, {"endpoint": "/health"})
            recovery_verified = health_output.get("healthy", False)

            execution.status = "SUCCESS" if success else "FAILED"
            execution.output = output
            execution.recovery_verified = recovery_verified
            execution.verification_details = health_output
            execution.completed_at = datetime.now(timezone.utc)

            req.status = "EXECUTED" if success else "FAILED"
            req.updated_at = datetime.now(timezone.utc)

            # Update Incident status if recovered
            incident = db.query(Incident).filter(Incident.id == req.incident_id).first()
            if incident and recovery_verified:
                incident.status = "RESOLVED"
                incident.description += f"\n\n[Auto-Resolved via Remediation]: {output.get('message', '')}"
                incident.updated_at = datetime.now(timezone.utc)

            db.commit()
            db.refresh(execution)

            AuditService.record(
                db=db,
                action="REMEDIATION_EXECUTED",
                target_resource="RemediationExecution",
                resource_id=execution.id,
                details={
                    "request_id": req.id,
                    "action_type": req.action_type,
                    "success": success,
                    "recovery_verified": recovery_verified
                }
            )

            logger.info(f"Remediation executed for request {request_id}. Success: {success}, Recovery: {recovery_verified}")
            return {
                "execution_id": execution.id,
                "status": execution.status,
                "recovery_verified": recovery_verified,
                "output": output
            }
        finally:
            db.close()

remediation_service = RemediationService()

