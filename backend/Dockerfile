FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (build-essential for C extensions, libpq for PostgreSQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency definitions
COPY backend/requirements.txt /app/requirements.txt

# Install python dependencies with pip cache disabled for lean container size
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and knowledge base
COPY backend /app/backend
COPY knowledge_base /app/knowledge_base
COPY alembic.ini /app/alembic.ini

# Set Python environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose FastAPI port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Launch uvicorn server
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

