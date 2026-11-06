import uuid
from typing import List
from backend.app.rag.base import DocumentChunk

class TextChunker:
    @staticmethod
    def chunk_document(
        document_id: str,
        document_title: str,
        category: str,
        text: str,
        chunk_size: int = 500,
        chunk_overlap: int = 100
    ) -> List[DocumentChunk]:
        """
        Splits markdown / text documents with sliding window overlap,
        preserving line boundaries where possible.
        """
        lines = text.split("\n")
        chunks: List[DocumentChunk] = []
        current_chunk = []
        current_length = 0

        for line in lines:
            line_len = len(line) + 1
            if current_length + line_len > chunk_size and current_chunk:
                content = "\n".join(current_chunk).strip()
                if content:
                    chunk = DocumentChunk(
                        chunk_id=str(uuid.uuid4()),
                        document_id=document_id,
                        document_title=document_title,
                        category=category,
                        content=content,
                        metadata={"title": document_title, "category": category}
                    )
                    chunks.append(chunk)

                # Keep overlap from the end of the current chunk
                overlap_chars = 0
                new_start = []
                for prev_line in reversed(current_chunk):
                    if overlap_chars + len(prev_line) <= chunk_overlap:
                        new_start.insert(0, prev_line)
                        overlap_chars += len(prev_line) + 1
                    else:
                        break
                current_chunk = new_start
                current_length = overlap_chars

            current_chunk.append(line)
            current_length += line_len

        # Remaining content
        if current_chunk:
            content = "\n".join(current_chunk).strip()
            if content:
                chunk = DocumentChunk(
                    chunk_id=str(uuid.uuid4()),
                    document_id=document_id,
                    document_title=document_title,
                    category=category,
                    content=content,
                    metadata={"title": document_title, "category": category}
                )
                chunks.append(chunk)

        return chunks

