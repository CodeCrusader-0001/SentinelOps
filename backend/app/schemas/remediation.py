from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from backend.app.schemas.user import UserResponse

class RemediationExecutionResponse(BaseModel):
    id: str
    request_id: str
    status: str
    output: Dict[str, Any]
    error_message: Optional[str] = None
    recovery_verified: bool
    verification_details: Optional[Dict[str, Any]] = None
    executed_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class RemediationRequestResponse(BaseModel):
    id: str
    incident_id: str
    action_type: str
    parameters: Dict[str, Any]
    rationale: str
    risk_level: str
    status: str
    requested_by: Optional[str] = None
    approved_by: Optional[str] = None
    approved_by_user: Optional[UserResponse] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    execution: Optional[RemediationExecutionResponse] = None

    model_config = ConfigDict(from_attributes=True)

class RemediationRejectRequest(BaseModel):
    reason: Optional[str] = Field(default=None, description="Reason for rejecting the proposed remediation")

