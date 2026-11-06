import os
os.environ["USE_TF"] = "0"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"

from typing import List
import numpy as np
from backend.app.core.config import settings
from backend.app.core.logging import logger

class EmbeddingEngine:
    def __init__(self, model_name: str = settings.RAG_EMBEDDING_MODEL):
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded SentenceTransformer embedding model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer: {e}. Fallback dummy embeddings active.")
            self.model = None

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        if self.model is not None:
            embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
            return embeddings.astype(np.float32)
        else:
            # Deterministic pseudo-embedding fallback for test or offline environments (384-dim)
            dim = 384
            res = []
            for t in texts:
                np.random.seed(sum(ord(c) for c in t) % (2**31))
                v = np.random.randn(dim).astype(np.float32)
                norm = np.linalg.norm(v)
                res.append(v / (norm if norm > 0 else 1.0))
            return np.array(res, dtype=np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        return self.embed_texts([query])

