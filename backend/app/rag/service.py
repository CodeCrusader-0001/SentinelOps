import os
import glob
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.rag.base import SearchResult
from backend.app.rag.chunking import TextChunker
from backend.app.rag.embedding import EmbeddingEngine
from backend.app.rag.faiss_store import FAISSVectorStore
from backend.app.models.document import Document
from backend.app.core.config import settings
from backend.app.core.logging import logger

class RAGService:
    def __init__(self):
        self.embedder = EmbeddingEngine(settings.RAG_EMBEDDING_MODEL)
        self.vector_store = FAISSVectorStore(
            dimension=384,
            index_path=settings.RAG_INDEX_PATH,
            metadata_path=settings.RAG_METADATA_PATH
        )

    def index_document(self, document_id: str, title: str, category: str, content: str) -> int:
        """Chunks, embeds, and indexes a document."""
        chunks = TextChunker.chunk_document(
            document_id=document_id,
            document_title=title,
            category=category,
            text=content,
            chunk_size=500,
            chunk_overlap=100
        )
        if not chunks:
            return 0

        texts = [c.content for c in chunks]
        embeddings = self.embedder.embed_texts(texts)
        self.vector_store.add_chunks(chunks, embeddings)
        return len(chunks)

    def search(
        self,
        query: str,
        top_k: int = settings.RAG_TOP_K,
        threshold: float = settings.RAG_SIMILARITY_THRESHOLD
    ) -> List[SearchResult]:
        query_vector = self.embedder.embed_query(query)
        results = self.vector_store.search(query_vector, top_k=top_k, threshold=threshold)
        return results

    def get_runbook_context(self, query: str, top_k: int = 3) -> str:
        """Constructs a consolidated context string for LLM prompt injection."""
        results = self.search(query, top_k=top_k)
        if not results:
            return "No matching runbooks found in the knowledge base."

        context_blocks = []
        for r in results:
            context_blocks.append(
                f"### [Runbook: {r.document_title}] (Relevance Score: {r.similarity_score:.2f})\n"
                f"{r.chunk_content}"
            )
        return "\n\n---\n\n".join(context_blocks)

    def delete_document(self, document_id: str) -> None:
        self.vector_store.delete_document(document_id)

    def seed_default_runbooks(self, db: Session, runbooks_dir: str = "knowledge_base/runbooks"):
        """Scans the runbooks directory and populates the DB and FAISS index if empty."""
        files = glob.glob(os.path.join(runbooks_dir, "*.md"))
        if not files:
            logger.warning(f"No runbook files found in {runbooks_dir}")
            return

        for filepath in files:
            filename = os.path.basename(filepath)
            title = filename.replace(".md", "").replace("_", " ").title()
            
            existing = db.query(Document).filter(Document.title == title).first()
            if existing:
                continue

            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            doc = Document(
                title=title,
                category="runbook",
                content=content,
                file_path=filepath
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)

            chunk_count = self.index_document(doc.id, doc.title, doc.category, doc.content)
            doc.chunk_count = chunk_count
            db.commit()
            logger.info(f"Seeded runbook '{title}' ({chunk_count} chunks)")

rag_service = RAGService()

