import pytest
from fastapi.testclient import TestClient
from backend.app.rag.chunking import TextChunker
from backend.app.rag.service import rag_service

def test_text_chunking():
    sample_text = """# Header 1
Line one of procedure.
Line two of procedure.
Line three of procedure.
Line four of procedure.
Line five of procedure.
Line six of procedure.
Line seven of procedure."""
    chunks = TextChunker.chunk_document(
        document_id="doc-123",
        document_title="Sample Runbook",
        category="runbook",
        text=sample_text,
        chunk_size=100,
        chunk_overlap=30
    )
    assert len(chunks) >= 2
    assert chunks[0].document_id == "doc-123"
    assert "Line" in chunks[0].content

def test_rag_retrieval_and_thresholding():
    # Search for database pool failure
    results = rag_service.search("Database connection pool timeout exhausted", top_k=3, threshold=0.30)
    assert len(results) > 0
    top_result = results[0]
    assert "Database" in top_result.document_title or "connection" in top_result.chunk_content.lower()
    assert top_result.similarity_score >= 0.30

    # Search for an irrelevant topic (should be filtered out by threshold)
    irrelevant = rag_service.search("How to bake chocolate chip cookies in an oven", top_k=3, threshold=0.60)
    assert len(irrelevant) == 0

def test_knowledge_api_endpoints(client: TestClient):
    # Login as admin
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@sentinelops.io", "password": "Admin@Sentinel2026!"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. List documents (should have 8 seeded runbooks)
    docs_resp = client.get("/api/v1/knowledge/documents", headers=headers)
    assert docs_resp.status_code == 200
    docs = docs_resp.json()
    assert len(docs) >= 8

    # 2. Search via API
    search_resp = client.post(
        "/api/v1/knowledge/search",
        headers=headers,
        json={"query": "Out of memory Java heap exhausted", "top_k": 2, "threshold": 0.25}
    )
    assert search_resp.status_code == 200
    search_results = search_resp.json()
    assert len(search_results) > 0
    assert any("Memory" in r["document_title"] for r in search_results)

