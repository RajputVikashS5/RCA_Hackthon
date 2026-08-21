from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    """
    Generates embeddings for document chunks.
    """

    def __init__(self):

        self.model = None

    def _ensure_model(self):

        if self.model is None:

            # Lightweight and accurate model
            self.model = SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2"
            )

    def embed_documents(self, texts):

        self._ensure_model()

        return self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=True
        )

    def embed_query(self, query):

        self._ensure_model()

        return self.model.encode(
            query,
            convert_to_numpy=True
        )