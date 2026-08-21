from sentence_transformers import SentenceTransformer
import numpy as np

from app.config import EMBEDDING_DIMENSION, EMBEDDING_MODEL_NAME


class EmbeddingModel:
    """
    Generates embeddings for document chunks.
    """

    def __init__(self):

        self.model = None

    def _ensure_model(self):

        if self.model is None:

            # Lightweight and accurate model
            self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    def _normalize(self, embeddings):
        array = np.asarray(embeddings, dtype=np.float32)
        if array.shape[-1] != EMBEDDING_DIMENSION:
            raise ValueError(
                f"Embedding dimension {array.shape[-1]} does not match configured dimension {EMBEDDING_DIMENSION}."
            )
        if array.ndim == 1:
            norm = np.linalg.norm(array)
            return array / norm if norm else array
        norms = np.linalg.norm(array, axis=1, keepdims=True)
        return np.divide(array, norms, out=np.zeros_like(array), where=norms != 0)

    def embed_documents(self, texts):

        self._ensure_model()

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=True
        )
        return self._normalize(embeddings)

    def embed_query(self, query):

        self._ensure_model()

        embeddings = self.model.encode(
            query,
            convert_to_numpy=True
        )
        return self._normalize(embeddings)