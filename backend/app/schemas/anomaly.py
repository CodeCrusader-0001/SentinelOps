from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime

class AnomalyResponse(BaseModel):
    id: str
    timestamp: datetime
    service: str
    anomaly_score: float
    actual_event: str
    predicted_events: Optional[str] = None
    detection_method: str
    supporting_evidence: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    incident_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
