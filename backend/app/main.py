import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app, Counter, Histogram

from backend.app.core.config import settings
from backend.app.core.logging import setup_logging, logger
from backend.app.database.session import engine, Base, SessionLocal
from backend.app import models
from backend.app.services.user_service import UserService

from backend.app.api.routes import auth, logs, incidents, audit, tasks, knowledge, remediations

# Setup logging
setup_logging(settings.LOG_LEVEL)

# Prometheus Metrics
REQUEST_COUNT = Counter(
    "sentinelops_http_requests_total",
    "Total HTTP requests handled by SentinelOps",
    ["method", "endpoint", "status_code"]
)
REQUEST_LATENCY = Histogram(
    "sentinelops_http_request_duration_seconds",
    "Latency of HTTP requests in seconds",
    ["endpoint"]
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist and seed default accounts
    logger.info("Initializing SentinelOps Database schema...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        UserService.seed_default_users(db)
        logger.info("Default Admin and IT Engineer accounts ensured.")
        from backend.app.rag.service import rag_service
        rag_service.seed_default_runbooks(db)
        logger.info("Default Runbooks checked and seeded.")
    finally:
        db.close()
        
    logger.info("SentinelOps Core Engine initialized successfully.")
    yield
    logger.info("SentinelOps Core Engine shutting down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="SentinelOps — AI-Powered Enterprise IT Operations and Incident Management Platform",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Correlation ID and Performance Middleware
@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id
    
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Response-Time"] = f"{duration * 1000:.2f}ms"
    
    # Record Prometheus metrics
    endpoint = request.url.path
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=endpoint,
        status_code=response.status_code
    ).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
    
    return response

# Prometheus ASGI Endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Health Check
@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

# Register API v1 Routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(logs.router, prefix=settings.API_V1_PREFIX)
app.include_router(incidents.router, prefix=settings.API_V1_PREFIX)
app.include_router(audit.router, prefix=settings.API_V1_PREFIX)
app.include_router(tasks.router, prefix=settings.API_V1_PREFIX)
app.include_router(knowledge.router, prefix=settings.API_V1_PREFIX)
app.include_router(remediations.router, prefix=settings.API_V1_PREFIX)
