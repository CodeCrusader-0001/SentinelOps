from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime

class LogLevelEnum(str):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    DEBUG = "DEBUG"

class LogCreate(BaseModel):
    application: str = Field(..., min_length=1, max_length=100)
    service: str = Field(..., min_length=1, max_length=100)
    level: str = Field(default="INFO", pattern="^(INFO|WARNING|ERROR|CRITICAL|DEBUG)$")
    message: str = Field(..., min_length=1)
    hostname: Optional[str] = Field(default=None, max_length=255)
    timestamp: Optional[datetime] = None
    metadata_json: Optional[Dict[str, Any]] = None

class LogBatchCreate(BaseModel):
    logs: List[LogCreate] = Field(..., min_length=1, max_length=1000)

class LogResponse(BaseModel):
    id: str
    timestamp: datetime
    application: str
    service: str
    level: str
    message: str
    hostname: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    processing_status: str
    incident_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class LogListResponse(BaseModel):
    total: int
    items: List[LogResponse]
    page: int
    size: int
