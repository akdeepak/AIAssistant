from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

from app.config import settings
from app.embeddings.factory import load_embedding_model
from app.ingestion.loader import ingest_documents
from app.ingestion.splitter import RecursiveTextSplitter
from app.models.document import Document
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RAGService:

    def __init__(
        self,
        model_name: str | None = None,
    ) -> None:
        self.model_name = model_name or settings.EMBED_MODEL_NAME
        self._documents: List[Document] = []
        self._document_vectors: List[List[float]] = []
        self._text_splitter = RecursiveTextSplitter(
            chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP
        )
        self._embed_model = load_embedding_model(self.model_name)

    def ingest(self, path: str) -> List[Dict[str, Any]]:
        logger.info("Ingesting documents from %s", path)
        try:
            documents = ingest_documents(path)
        except FileNotFoundError:
            documents = []

        if not documents:
            logger.warning(
                "No documents discovered at %s; returning empty result.", path
            )
            return []

        chunked_documents = self._text_splitter.split(documents) or documents
        vectors = self._embed_model.embed_documents([
            doc.content for doc in chunked_documents
        ])

        self._documents.extend(chunked_documents)
        self._document_vectors.extend(vectors)
        logger.info("Ingested %d FAQ chunks.", len(chunked_documents))

        return [self._serialize_document(doc) for doc in chunked_documents]

    def query(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self._documents:
            logger.warning("Attempted to query FAQs before any ingestion.")
            return []

        bounded_top_k = max(1, min(top_k, len(self._documents)))
        query_vector = self._embed_model.embed_query(query)
        similarities = self._compute_similarities(query_vector)
        if similarities.size == 0:
            return []

        top_indices = np.argsort(similarities)[::-1][:bounded_top_k]
        results: List[Dict[str, Any]] = []
        for idx in top_indices:
            payload = self._serialize_document(self._documents[idx])
            payload["score"] = float(similarities[idx])
            results.append(payload)

        logger.info("Query '%s' processed with %d hits.", query, len(results))
        return results

    @staticmethod
    def _serialize_document(document: Document) -> Dict[str, Any]:
        return {
            "page_content": document.content,
            "metadata": document.metadata,
        }

    def _compute_similarities(self, query_vector: List[float]) -> np.ndarray:
        if not self._document_vectors:
            return np.array([])

        doc_matrix = np.array(self._document_vectors)
        query_vec = np.array(query_vector)

        doc_norms = np.linalg.norm(doc_matrix, axis=1)
        query_norm = np.linalg.norm(query_vec)
        denom = doc_norms * query_norm
        denom[denom == 0] = 1.0

        similarities = (doc_matrix @ query_vec) / denom
        return similarities
