import pytest
from fastapi.testclient import TestClient
from backend.app.database.session import SessionLocal
from backend.app.models.incident import Incident
from backend.app.models.user import User
from backend.app.remediation.actions import RemediationExecutor
from backend.app.remediation.service import remediation_service

def test_remediation_executor_strict_allowlist():
    # Allowlisted action: restart_service
    success, out = RemediationExecutor.execute("restart_service", "billing-service", {})
    assert success is True
    assert out["status"] == "COMPLETED"

    # Allowlisted action: clear_cache
    success, out = RemediationExecutor.execute("clear_cache", "redis-cluster", {"cache_pattern": "sess:*"})
    assert success is True
    assert out["status"] == "COMPLETED"

    # Disallowed action: arbitrary command execution MUST be blocked
    success, out = RemediationExecutor.execute("bash_exec", "billing-service", {"cmd": "rm -rf /"})
    assert success is False
    assert "not permitted" in out["error"]

def test_remediation_approval_and_execution_lifecycle(client: TestClient):
    db = SessionLocal()
    try:
        # Create incident
        incident = Incident(
            title="Service latency spike remediation test",
            description="API latency test incident.",
            severity="MEDIUM",
            status="OPEN"
        )
        db.add(incident)
        db.commit()
        db.refresh(incident)

        # Create remediation request
        req = remediation_service.create_request(
            db=db,
            incident_id=incident.id,
            action_type="scale_workers",
            parameters={"replicas": 4, "target_service": "api-gateway"},
            rationale="Scale workers to mitigate request queue delay."
        )
        assert req.status == "PENDING"

        # Login as Admin
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@sentinelops.io", "password": "Admin@Sentinel2026!"}
        )
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Approve remediation via API
        app_resp = client.post(f"/api/v1/remediations/{req.id}/approve", headers=headers)
        assert app_resp.status_code == 200
        approved_data = app_resp.json()
        assert approved_data["status"] == "EXECUTED"
        assert approved_data["execution"]["recovery_verified"] is True
    finally:
        db.close()

