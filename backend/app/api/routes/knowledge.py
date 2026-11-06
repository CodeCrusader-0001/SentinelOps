from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.document import Document
from backend.app.schemas.knowledge import DocumentCreate, DocumentResponse, SearchQuery, SearchResultResponse
from backend.app.rag.service import rag_service
from backend.app.services.audit_service import AuditService
from backend.app.api.deps import get_current_user, require_role
from backend.app.models.user import User

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])

@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    doc_in: DocumentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "IT Engineer"]))
):
    doc = Document(
        title=doc_in.title,
        category=doc_in.category,
        content=doc_in.content,
        metadata_json=doc_in.metadata_json
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Chunk and embed into FAISS
    chunks_count = rag_service.index_document(doc.id, doc.title, doc.category, doc.content)
    doc.chunk_count = chunks_count
    db.commit()

    AuditService.record(
        db=db,
        action="DOCUMENT_CREATED",
        target_resource="Document",
        resource_id=doc.id,
        user=current_user,
        details={"title": doc.title, "chunks": chunks_count},
        ip_address=request.client.host if request.client else None
    )

    return doc

@router.get("/documents", response_model=List[DocumentResponse])
def list_documents(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Document)
    if category:
        query = query.filter(Document.category == category)
    return query.order_by(Document.created_at.desc()).all()

@router.post("/search", response_model=List[SearchResultResponse])
def search_knowledge_base(
    search_query: SearchQuery,
    current_user: User = Depends(get_current_user)
):
    results = rag_service.search(
        query=search_query.query,
        top_k=search_query.top_k,
        threshold=search_query.threshold or 0.35
    )
    return [
        SearchResultResponse(
            document_id=r.document_id,
            document_title=r.document_title,
            chunk_content=r.chunk_content,
            similarity_score=r.similarity_score,
            source_reference=r.source_reference,
            metadata=r.metadata
        )
        for r in results
    ]

@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    rag_service.delete_document(doc.id)
    db.delete(doc)
    db.commit()

    AuditService.record(
        db=db,
        action="DOCUMENT_DELETED",
        target_resource="Document",
        resource_id=document_id,
        user=current_user,
        ip_address=request.client.host if request.client else None
    )
    return None

