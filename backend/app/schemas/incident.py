from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from backend.app.schemas.user import UserResponse
from backend.app.schemas.log import LogResponse
from backend.app.schemas.anomaly import AnomalyResponse

class IncidentCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=5)
    severity: str = Field(default="MEDIUM", pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    source: str = Field(default="Manual")
    deduplication_key: Optional[str] = None
    assigned_engineer_id: Optional[str] = None
    log_ids: Optional[List[str]] = None

class IncidentUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=255)
    description: Optional[str] = None
    severity: Optional[str] = Field(default=None, pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    status: Optional[str] = Field(default=None, pattern="^(OPEN|INVESTIGATING|PENDING_APPROVAL|REMEDIATING|RESOLVED|FAILED)$")
    assigned_engineer_id: Optional[str] = None

class IncidentAssignRequest(BaseModel):
    engineer_id: str

class IncidentResolveRequest(BaseModel):
    resolution_notes: Optional[str] = None

class IncidentResponse(BaseModel):
    id: str
    title: str
    description: str
    severity: str
    status: str
    source: str
    deduplication_key: Optional[str] = None
    assigned_engineer_id: Optional[str] = None
    assigned_engineer: Optional[UserResponse] = None
    created_at: datetime
    updated_at: datetime
    
    logs: Optional[List[LogResponse]] = None
    anomalies: Optional[List[AnomalyResponse]] = None

    model_config = ConfigDict(from_attributes=True)

class IncidentListResponse(BaseModel):
    total: int
    items: List[IncidentResponse]
    page: int
    size: int
