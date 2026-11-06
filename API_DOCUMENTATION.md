# SentinelOps REST API Documentation

SentinelOps exposes a high-throughput, asynchronous RESTful API built on FastAPI. This document outlines the available endpoints, authentication mechanisms, request/response schemas, and error conventions.

The interactive Swagger UI is accessible at `http://localhost:8000/docs` and Redoc at `http://localhost:8000/redoc`.

---

## 1. Global Conventions

### Base URL
All API v1 routes are mounted under the `/api/v1` prefix:
```
http://localhost:8000/api/v1
```

### Authentication Header
Protected endpoints require an `Authorization` header containing an active JWT bearer token:
```http
Authorization: Bearer <jwt_access_token>
```

### Correlation ID
Clients may supply an optional `X-Correlation-ID` header. If absent, the backend assigns a UUID v4 and returns it in the response headers for distributed request tracing.

---

## 2. Authentication Endpoints (`/api/v1/auth`)

### 2.1 User Registration
- **Method**: `POST`
- **Path**: `/api/v1/auth/register`
- **Access**: Public
- **Request Body**:
  ```json
  {
    "email": "engineer@sentinelops.io",
    "password": "SecurePassword123!",
    "full_name": "Jane Doe",
    "role": "IT Engineer"
  }
  ```
- **Response** (`201 Created`):
  ```json
  {
    "id": 2,
    "email": "engineer@sentinelops.io",
    "full_name": "Jane Doe",
    "role": "IT Engineer",
    "is_active": true,
    "created_at": "2026-11-06T02:00:00Z"
  }
  ```

### 2.2 User Login (JSON Body)
- **Method**: `POST`
- **Path**: `/api/v1/auth/login`
- **Access**: Public
- **Request Body**:
  ```json
  {
    "email": "admin@sentinelops.io",
    "password": "admin"
  }
  ```
- **Response** (`200 OK`):
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "email": "admin@sentinelops.io",
      "full_name": "System Administrator",
      "role": "Admin",
      "is_active": true
    }
  }
  ```

### 2.3 Current User Info
- **Method**: `GET`
- **Path**: `/api/v1/auth/me`
- **Access**: Authenticated (`Viewer`, `IT Engineer`, `Admin`)
- **Response** (`200 OK`):
  ```json
  {
    "id": 1,
    "email": "admin@sentinelops.io",
    "full_name": "System Administrator",
    "role": "Admin",
    "is_active": true,
    "created_at": "2026-11-06T02:00:00Z"
  }
  ```

---

## 3. Log Ingestion Endpoints (`/api/v1/logs`)

### 3.1 Ingest Single Log
- **Method**: `POST`
- **Path**: `/api/v1/logs`
- **Access**: Public / Ingestion Service
- **Request Body**:
  ```json
  {
    "application": "payment-gateway",
    "service": "billing-service",
    "level": "ERROR",
    "message": "Database connection pool timeout while acquiring connection",
    "hostname": "srv-prod-east-01",
    "metadata": {"pool_size": 20, "active_conns": 20}
  }
  ```
- **Response** (`202 Accepted`):
  ```json
  {
    "message": "Log ingested successfully",
    "log_id": 42,
    "status": "QUEUED"
  }
  ```

### 3.2 Ingest Log Batch
- **Method**: `POST`
- **Path**: `/api/v1/logs/batch`
- **Access**: Public / Ingestion Service
- **Request Body**:
  ```json
  {
    "logs": [
      {
        "application": "payment-gateway",
        "service": "billing-service",
        "level": "INFO",
        "message": "Batch payment job started"
      },
      {
        "application": "payment-gateway",
        "service": "billing-service",
        "level": "ERROR",
        "message": "Connection refused to redis:6379"
      }
    ]
  }
  ```
- **Response** (`202 Accepted`):
  ```json
  {
    "message": "Batch ingested successfully",
    "count": 2,
    "log_ids": [43, 44],
    "task_id": "7b8f04c1-e37a-4b92-9457-3f33827178c1"
  }
  ```

### 3.3 Query Ingested Logs
- **Method**: `GET`
- **Path**: `/api/v1/logs`
- **Access**: Authenticated
- **Query Parameters**:
  - `application` (string, optional)
  - `service` (string, optional)
  - `level` (string, optional: `INFO`, `WARNING`, `ERROR`, `CRITICAL`, `DEBUG`)
  - `limit` (integer, default: 50, max: 200)
  - `offset` (integer, default: 0)

---

## 4. Incident Management Endpoints (`/api/v1/incidents`)

### 4.1 List Incidents
- **Method**: `GET`
- **Path**: `/api/v1/incidents`
- **Access**: Authenticated
- **Query Parameters**:
  - `status` (`OPEN`, `INVESTIGATING`, `PENDING_APPROVAL`, `REMEDIATING`, `RESOLVED`, `FAILED`)
  - `severity` (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`)
  - `limit` (integer, default: 50)
  - `offset` (integer, default: 0)

### 4.2 Get Incident Details
- **Method**: `GET`
- **Path**: `/api/v1/incidents/{incident_id}`
- **Access**: Authenticated
- **Response** (`200 OK`):
  ```json
  {
    "id": 1,
    "title": "Anomaly detected in billing-service: Database connection timeout",
    "description": "Exceeded database pool limit",
    "severity": "CRITICAL",
    "status": "OPEN",
    "source": "DEEPLOG_ANOMALY_DETECTOR",
    "assigned_to": null,
    "created_at": "2026-11-06T02:05:00Z",
    "anomalies": [...],
    "investigation_reports": [...],
    "remediation_requests": [...]
  }
  ```

### 4.3 Trigger AI LangGraph Investigation
- **Method**: `POST`
- **Path**: `/api/v1/incidents/{incident_id}/investigate`
- **Access**: `Admin`, `IT Engineer`
- **Response** (`202 Accepted`):
  ```json
  {
    "message": "AI investigation initiated via LangGraph",
    "incident_id": 1,
    "task_id": "c1f76d91-..."
  }
  ```

### 4.4 Assign Incident
- **Method**: `POST`
- **Path**: `/api/v1/incidents/{incident_id}/assign`
- **Access**: `Admin`, `IT Engineer`
- **Query Parameter**: `assigned_to` (string, user email)

### 4.5 Resolve Incident
- **Method**: `POST`
- **Path**: `/api/v1/incidents/{incident_id}/resolve`
- **Access**: `Admin`, `IT Engineer`

---

## 5. RAG Knowledge Base Endpoints (`/api/v1/knowledge`)

### 5.1 Search Runbooks (Semantic Vector Search)
- **Method**: `POST`
- **Path**: `/api/v1/knowledge/search`
- **Access**: Authenticated
- **Request Body**:
  ```json
  {
    "query": "Database connection pool timeout exhausted",
    "top_k": 3
  }
  ```
- **Response** (`200 OK`):
  ```json
  {
    "query": "Database connection pool timeout exhausted",
    "results": [
      {
        "document_id": 1,
        "document_title": "Database Connection Pool Exhaustion Runbook",
        "chunk_content": "### Symptoms: \n- Error log indicates remaining connection slots are reserved...",
        "similarity_score": 0.8421,
        "metadata": {"category": "database", "priority": "high"}
      }
    ]
  }
  ```

### 5.2 Upload Runbook Document
- **Method**: `POST`
- **Path**: `/api/v1/knowledge/documents`
- **Access**: `Admin`, `IT Engineer`
- **Request Body**:
  ```json
  {
    "title": "Custom Microservice Outage Runbook",
    "content": "# Runbook content...",
    "source_file": "runbooks/custom.md",
    "metadata": {"service": "custom"}
  }
  ```

---

## 6. Remediation Endpoints (`/api/v1/remediations`)

### 6.1 List Remediation Requests
- **Method**: `GET`
- **Path**: `/api/v1/remediations`
- **Access**: Authenticated

### 6.2 Human Approval Gate (Authorize Mitigation)
- **Method**: `POST`
- **Path**: `/api/v1/remediations/{request_id}/approve`
- **Access**: `Admin`, `IT Engineer`
- **Response** (`200 OK`):
  ```json
  {
    "message": "Remediation request approved and queued for execution",
    "request_id": 1,
    "status": "APPROVED",
    "task_id": "4b68e982-..."
  }
  ```

### 6.3 Reject Remediation Request
- **Method**: `POST`
- **Path**: `/api/v1/remediations/{request_id}/reject`
- **Access**: `Admin`, `IT Engineer`
- **Query Parameter**: `reason` (string, optional)

---

## 7. Monitoring & Operational Endpoints

### 7.1 Prometheus Metrics
- **Method**: `GET`
- **Path**: `/metrics`
- **Access**: Public / Prometheus Scraper
- **Format**: Prometheus exposition text format (standard OpenMetrics).

### 7.2 Service Health Check
- **Method**: `GET`
- **Path**: `/health`
- **Access**: Public
- **Response** (`200 OK`):
  ```json
  {
    "status": "healthy",
    "database": "connected",
    "rag_index_size": 32,
    "timestamp": "2026-11-06T02:00:00Z"
  }
  ```

