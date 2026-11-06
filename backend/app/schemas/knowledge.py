from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime

class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    category: str = Field(default="runbook", max_length=100)
    content: str = Field(..., min_length=10)
    metadata_json: Optional[Dict[str, Any]] = None

class DocumentResponse(BaseModel):
    id: str
    title: str
    category: str
    content: str
    file_path: Optional[str] = None
    chunk_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SearchQuery(BaseModel):
    query: str = Field(..., min_length=2)
    top_k: int = Field(default=4, ge=1, le=20)
    threshold: Optional[float] = Field(default=0.35, ge=0.0, le=1.0)

class SearchResultResponse(BaseModel):
    document_id: str
    document_title: str
    chunk_content: str
    similarity_score: float
    source_reference: str
    metadata: Dict[str, Any]

