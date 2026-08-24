from app.config import INCIDENTS_DIR
from app.services.embedding import SentenceTransformerEmbeddingService
from app.services.incident_ingestion import IncidentIngestionError, IncidentIngestionService
from app.services.vector_store import VectorStore


class RAGPipeline:

    def __init__(self):

        self.loader = IncidentIngestionService()

        self.embedding_model = SentenceTransformerEmbeddingService()

        self.vector_store = VectorStore()

    def build_vector_database(self):

        records, stats, _source_files = self.loader.load_folder(INCIDENTS_DIR)

        texts = [record.search_text for record in records if record.search_text]

        if not texts:
            raise IncidentIngestionError("No searchable incident text was generated from the uploaded dataset.")

        embeddings = self.embedding_model.embed_documents(texts)

        metadata = [record.model_dump(exclude_none=True, exclude={"search_text"}) for record in records]

        self.vector_store.create_index(embeddings, metadata)
        self.vector_store.save()

        return stats