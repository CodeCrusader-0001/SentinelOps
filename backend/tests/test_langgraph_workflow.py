import pytest
from backend.app.database.session import SessionLocal
from backend.app.models.incident import Incident
from backend.app.models.log import Log
from backend.app.agents.workflow import run_investigation_pipeline_sync
from backend.app.remediation.service import remediation_service
from backend.app.models.user import User

def test_langgraph_investigation_agent_flow():
    db = SessionLocal()
    try:
        # Create incident with logs
        incident = Incident(
            title="Database Connection Exhaustion Under High Load",
            description="Active billing pool exhausted all slots during flash sale.",
            severity="CRITICAL",
            status="OPEN"
        )
        db.add(incident)
        db.commit()
        db.refresh(incident)

        log = Log(
            application="checkout",
            service="billing-service",
            level="ERROR",
            message="Database connection pool timeout while acquiring connection",
            incident_id=incident.id
        )
        db.add(log)
        db.commit()

        # Step 1: Run graph initial pass (should pause at Human Approval Gate)
        final_state = run_investigation_pipeline_sync(incident.id)

        assert final_state["title"] == incident.title
        assert len(final_state["step_history"]) >= 5
        assert any("Root Cause Analysis" in s for s in final_state["step_history"])
        assert final_state["approval_status"] == "PENDING"
        assert final_state["remediation_request_id"] is not None

        # Step 2: Simulate Human Engineer Approval
        admin_user = db.query(User).filter(User.email == "admin@sentinelops.io").first()
        req_id = final_state["remediation_request_id"]
        remediation_service.approve_request(db, req_id, admin_user)

        # Step 3: Resume Graph with approved status
        final_state["approval_status"] = "APPROVED"
        resumed_state = run_investigation_pipeline_sync(incident.id)
        # Verify that remediation executed and report finalized
        assert len(resumed_state["step_history"]) >= 7
    finally:
        db.close()

