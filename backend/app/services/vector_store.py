from __future__ import annotations

import json
import os
from typing import Any, Dict, List

import faiss
import numpy as np

from app.config import INCIDENT_VECTOR_DB_DIR


class VectorStore:

    def __init__(self):

        self.index = None
        self.metadata = []
        self.index_path = os.path.join(INCIDENT_VECTOR_DB_DIR, "faiss.index")
        self.metadata_path = os.path.join(INCIDENT_VECTOR_DB_DIR, "metadata.json")

    def create_index(self, embeddings, metadata):

        if embeddings is None or len(embeddings) == 0:
            raise ValueError("Cannot create a FAISS index without embeddings.")

        normalized_embeddings = np.array(embeddings, dtype="float32")
        faiss.normalize_L2(normalized_embeddings)

        dimension = normalized_embeddings.shape[1]

        self.index = faiss.IndexFlatL2(dimension)

        self.index.add(normalized_embeddings)

        self.metadata = metadata

    def save(self):

        if self.index is None:
            raise RuntimeError("FAISS index is not initialized.")

        faiss.write_index(self.index, self.index_path)

        with open(self.metadata_path, "w", encoding="utf-8") as file_handle:
            json.dump(self.metadata, file_handle, ensure_ascii=False, indent=2)

    def exists(self):

        return os.path.exists(self.index_path) and os.path.exists(self.metadata_path)

    def load(self):

        if not self.exists():
            raise FileNotFoundError("FAISS index is not initialized.")

        self.index = faiss.read_index(self.index_path)

        with open(self.metadata_path, "r", encoding="utf-8") as file_handle:
            self.metadata = json.load(file_handle)

    def search(self, query_embedding, top_k=5):

        if self.index is None:
            raise RuntimeError("FAISS index is not initialized.")

        query_vector = np.array([query_embedding], dtype="float32")
        faiss.normalize_L2(query_vector)

        distances, indices = self.index.search(query_vector, top_k)

        results = []

        for distance, index in zip(distances[0], indices[0]):

            if index == -1:
                continue

            metadata = dict(self.metadata[index])
            similarity_score = max(-1.0, min(1.0, 1.0 - (float(distance) / 2.0)))

            results.append({
                "incident_id": metadata.get("incident_id", ""),
                "title": metadata.get("title", ""),
                "description": metadata.get("description", ""),
                "root_cause": metadata.get("root_cause", ""),
                "resolution": metadata.get("resolution", ""),
                "similarity_score": round(similarity_score, 4),
                "metadata": metadata,
            })

        return results   