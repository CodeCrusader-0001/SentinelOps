from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class DocumentChunk:
    chunk_id: str
    document_id: str
    document_title: str
    category: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SearchResult:
    document_id: str
    document_title: str
    chunk_content: str
    similarity_score: float
    source_reference: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class BaseVectorStore(ABC):
    @abstractmethod
    def add_chunks(self, chunks: List[DocumentChunk], embeddings: Any) -> None:
        pass

    @abstractmethod
    def search(self, query_embedding: Any, top_k: int = 4, threshold: float = 0.35) -> List[SearchResult]:
        pass

    @abstractmethod
    def delete_document(self, document_id: str) -> None:
        pass

    @abstractmethod
    def save(self) -> None:
        pass

    @abstractmethod
    def load(self) -> bool:
        pass

