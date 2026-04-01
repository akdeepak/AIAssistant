from __future__ import annotations

import uuid
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Dict, List

from app.config import settings
from app.embeddings.factory import load_embedding_model
from app.ingestion.loader import ingest_documents
from app.ingestion.splitter import RecursiveTextSplitter
from app.utils.logger import get_logger
from app.vector_db.connector import VectorDBConnector

logger = get_logger(__name__)


class KnowledgeBaseIngestionService:

    def __init__(self, db_type: str, db_config: Dict[str, Any]) -> None:
        self._connector = VectorDBConnector(db_type, db_config)
        self._text_splitter = RecursiveTextSplitter(
            chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP
        )
        self._embed_model = load_embedding_model(settings.EMBED_MODEL_NAME)

    def ingest_directory(self, path: str) -> Dict[str, Any]:
        knowledge_base_id = str(uuid.uuid4())
        logger.info("Creating knowledge base %s from path %s", knowledge_base_id, path)

        try:
            documents = ingest_documents(path)
        except FileNotFoundError:
            documents = []

        if not documents:
            logger.warning(
                "No documents discovered at %s; creating empty knowledge base %s",
                path,
                knowledge_base_id,
            )
            return {
                "knowledge_base_id": knowledge_base_id,
                "chunks": 0,
                "message": "No documents found to ingest.",
            }

        chunked_documents = self._text_splitter.split(documents) or documents
        contents = [doc.content for doc in chunked_documents]
        vectors = self._embed_model.embed_documents(contents)

        for doc, vector in zip(chunked_documents, vectors):
            metadata = dict(doc.metadata)
            metadata.setdefault("ingested_at", datetime.now(timezone.utc).isoformat())
            metadata.setdefault(
                "source_hash", sha256(doc.content.encode()).hexdigest()
            )
            metadata["knowledge_base_id"] = knowledge_base_id
            self._connector.insert(vector, metadata)

        logger.info(
            "Knowledge base %s ingested with %d chunks",
            knowledge_base_id,
            len(chunked_documents),
        )

        return {
            "knowledge_base_id": knowledge_base_id,
            "chunks": len(chunked_documents),
            "message": "Knowledge base created successfully.",
        }


class KnowledgeBaseRetrievalService:

    def __init__(self, db_type: str, db_config: Dict[str, Any]) -> None:
        self._connector = VectorDBConnector(db_type, db_config)
        self._embed_model = load_embedding_model(settings.EMBED_MODEL_NAME)

    def query(
        self, knowledge_base_id: str, query: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        if not query:
            return []

        logger.info(
            "Querying knowledge base %s with top_k=%d", knowledge_base_id, top_k
        )
        query_vector = self._embed_model.embed_query(query)

        results = self._connector.query(
            query_vector,
            top_k,
            metadata_filter={"knowledge_base_id": knowledge_base_id},
        )

        return results
