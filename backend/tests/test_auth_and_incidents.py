import uuid
import pytest
from fastapi.testclient import TestClient

def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "SentinelOps"

def test_login_seeded_admin(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@sentinelops.io", "password": "Admin@Sentinel2026!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "Admin"
    assert data["user"]["email"] == "admin@sentinelops.io"

def test_user_registration_and_auth_flow(client: TestClient):
    random_id = str(uuid.uuid4())[:8]
    email = f"engineer_{random_id}@sentinelops.io"
    password = "SecurePassword123!"
    
    # Register
    reg_resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": f"DevOps Engineer {random_id}",
            "role": "IT Engineer"
        }
    )
    assert reg_resp.status_code == 201
    user_data = reg_resp.json()
    assert user_data["email"] == email

    # Login
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Verify Current User
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == email

def test_log_ingestion_and_incident_lifecycle(client: TestClient):
    # Login as admin
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@sentinelops.io", "password": "Admin@Sentinel2026!"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Ingest Single Log
    log_resp = client.post(
        "/api/v1/logs",
        json={
            "application": "payment-gateway",
            "service": "billing-service",
            "level": "ERROR",
            "message": "Database connection pool timeout while acquiring connection",
            "hostname": "prod-billing-01",
            "metadata_json": {"timeout_ms": 5000}
        }
    )
    assert log_resp.status_code == 202
    log_id = log_resp.json()["id"]

    # 2. Ingest Batch Logs
    batch_resp = client.post(
        "/api/v1/logs/batch",
        json={
            "logs": [
                {
                    "application": "auth-service",
                    "service": "jwt-validator",
                    "level": "INFO",
                    "message": "Token refreshed successfully",
                    "hostname": "prod-auth-02"
                },
                {
                    "application": "auth-service",
                    "service": "jwt-validator",
                    "level": "CRITICAL",
                    "message": "Redis cluster unreachable during session revocation",
                    "hostname": "prod-auth-02"
                }
            ]
        }
    )
    assert batch_resp.status_code == 202
    assert len(batch_resp.json()) == 2

    # 3. Query Logs
    logs_list_resp = client.get("/api/v1/logs", headers=headers)
    assert logs_list_resp.status_code == 200
    assert logs_list_resp.json()["total"] >= 3

    # 4. Create Incident
    dedup_key = f"billing-db-pool-{uuid.uuid4()}"
    inc_resp = client.post(
        "/api/v1/incidents",
        headers=headers,
        json={
            "title": "Payment Gateway DB Connection Outage",
            "description": "Billing service cannot acquire database connections from pool.",
            "severity": "CRITICAL",
            "source": "Payment Monitor",
            "deduplication_key": dedup_key,
            "log_ids": [log_id]
        }
    )
    assert inc_resp.status_code == 201
    incident_id = inc_resp.json()["id"]
    assert inc_resp.json()["status"] == "OPEN"

    # 5. Deduplication check: submitting duplicate deduplication_key returns existing incident
    dup_resp = client.post(
        "/api/v1/incidents",
        headers=headers,
        json={
            "title": "Payment Gateway DB Connection Outage - Duplicate Alert",
            "description": "Second alert for same failure",
            "severity": "CRITICAL",
            "deduplication_key": dedup_key
        }
    )
    assert dup_resp.status_code == 201
    assert dup_resp.json()["id"] == incident_id

    # 6. Patch Incident Status
    patch_resp = client.patch(
        f"/api/v1/incidents/{incident_id}",
        headers=headers,
        json={"status": "INVESTIGATING"}
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "INVESTIGATING"

    # 7. Resolve Incident
    res_resp = client.post(
        f"/api/v1/incidents/{incident_id}/resolve",
        headers=headers,
        json={"resolution_notes": "Database connection pool size increased from 20 to 100."}
    )
    assert res_resp.status_code == 200
    assert res_resp.json()["status"] == "RESOLVED"

    # 8. Query Audit Logs
    audit_resp = client.get("/api/v1/audit", headers=headers)
    assert audit_resp.status_code == 200
    assert audit_resp.json()["total"] >= 1
