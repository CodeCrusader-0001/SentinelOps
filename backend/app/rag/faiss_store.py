import os
import pickle
from typing import List, Dict, Any, Optional
import numpy as np
import faiss

from backend.app.rag.base import BaseVectorStore, DocumentChunk, SearchResult
from backend.app.core.config import settings
from backend.app.core.logging import logger

class FAISSVectorStore(BaseVectorStore):
    def __init__(
        self,
        dimension: int = 384,
        index_path: str = settings.RAG_INDEX_PATH,
        metadata_path: str = settings.RAG_METADATA_PATH
    ):
        self.dimension = dimension
        self.index_path = index_path
        self.metadata_path = metadata_path
        
        # Use Inner Product (cosine similarity on normalized vectors)
        self.index = faiss.IndexFlatIP(self.dimension)
        self.chunks: List[DocumentChunk] = []
        
        # Create storage directory if needed
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        self.load()

    def add_chunks(self, chunks: List[DocumentChunk], embeddings: np.ndarray) -> None:
        if len(chunks) == 0:
            return
            
        if embeddings.shape[1] != self.dimension:
            raise ValueError(f"Embedding dimension {embeddings.shape[1]} does not match index {self.dimension}")

        # Normalize to ensure inner product equals cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
        self.chunks.extend(chunks)
        self.save()
        logger.info(f"Indexed {len(chunks)} chunks into FAISS vector store. Total index size: {self.index.ntotal}")

    def search(self, query_embedding: np.ndarray, top_k: int = 4, threshold: float = 0.35) -> List[SearchResult]:
        if self.index.ntotal == 0 or len(self.chunks) == 0:
            return []

        # Normalize query vector
        faiss.normalize_L2(query_embedding)
        k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(query_embedding, k)

        results: List[SearchResult] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1 or idx >= len(self.chunks):
                continue
            if score < threshold:
                continue

            chunk = self.chunks[idx]
            results.append(
                SearchResult(
                    document_id=chunk.document_id,
                    document_title=chunk.document_title,
                    chunk_content=chunk.content,
                    similarity_score=round(float(score), 4),
                    source_reference=f"{chunk.document_title} (Category: {chunk.category})",
                    metadata=chunk.metadata
                )
            )

        return results

    def delete_document(self, document_id: str) -> None:
        """Deletes all chunks associated with a document_id and rebuilds the FAISS index."""
        remaining_chunks = [c for c in self.chunks if c.document_id != document_id]
        if len(remaining_chunks) == len(self.chunks):
            return # Nothing to delete

        logger.info(f"Deleting document {document_id} from FAISS. Remaining chunks: {len(remaining_chunks)}")
        
        # Re-index remaining chunks
        self.index = faiss.IndexFlatIP(self.dimension)
        self.chunks = []
        
        if remaining_chunks:
            from backend.app.rag.embedding import EmbeddingEngine
            embedder = EmbeddingEngine()
            texts = [c.content for c in remaining_chunks]
            embeddings = embedder.embed_texts(texts)
            self.add_chunks(remaining_chunks, embeddings)
        else:
            self.save()

    def save(self) -> None:
        try:
            faiss.write_index(self.index, self.index_path)
            with open(self.metadata_path, "wb") as f:
                pickle.dump(self.chunks, f)
            logger.info("FAISS index and metadata successfully saved to disk.")
        except Exception as e:
            logger.error(f"Failed to persist FAISS index: {e}", exc_info=True)

    def load(self) -> bool:
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.metadata_path, "rb") as f:
                    self.chunks = pickle.load(f)
                logger.info(f"Loaded existing FAISS index from disk. Items: {self.index.ntotal}")
                return True
            except Exception as e:
                logger.warning(f"Error reading existing FAISS index files: {e}. Initializing fresh index.")
                self.index = faiss.IndexFlatIP(self.dimension)
                self.chunks = []
                return False
        return False

