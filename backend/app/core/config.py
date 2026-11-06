from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )

    # Project Identity
    PROJECT_NAME: str = "SentinelOps"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Security & Auth
    SECRET_KEY: str = "sentinelops_super_secure_jwt_secret_key_2026_enterprise_grade"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 # 24 hours
    
    # Database
    DATABASE_URL: str = "sqlite:///./sentinelops.db"
    
    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    
    # AI & Google Gemini
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-3.8-flash"
    GEMINI_TIMEOUT_SECONDS: int = 30
    GEMINI_MAX_RETRIES: int = 3
    
    # Anomaly Detection
    ANOMALY_DETECTOR_TYPE: str = "deeplog"
    DEEPLOG_MODEL_PATH: str = "backend/app/detection/models/deeplog_lstm.pth"
    DEEPLOG_VOCAB_PATH: str = "backend/app/detection/models/vocab.pkl"
    DEEPLOG_TOP_G: int = 5
    DEEPLOG_WINDOW_SIZE: int = 10
    
    # RAG & Knowledge Base
    RAG_EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    RAG_INDEX_PATH: str = "backend/app/rag/storage/faiss_index.bin"
    RAG_METADATA_PATH: str = "backend/app/rag/storage/metadata.pkl"
    RAG_SIMILARITY_THRESHOLD: float = 0.35
    RAG_TOP_K: int = 4
    
    # Remediation
    REMEDIATION_REQUIRE_APPROVAL: bool = True
    ALLOWED_REMEDIATION_ACTIONS: List[str] = [
        "restart_service",
        "clear_cache",
        "scale_workers",
        "run_health_check"
    ]
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

settings = Settings()
