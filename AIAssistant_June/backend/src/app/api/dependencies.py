from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config import settings
from app.utils.logger import get_logger
from app.utils.validators import UUID_RE

logger = get_logger(__name__)

_API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(
    api_key: str | None = Security(_API_KEY_HEADER),
) -> None:
    if not settings.API_KEY:
        return
    if not api_key or api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )



def validate_knowledge_base_id(knowledge_base_id: str) -> str:
    if not UUID_RE.match(knowledge_base_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid knowledge_base_id — must be a valid UUID.",
        )
    return knowledge_base_id


def validate_ingest_path(path: str) -> Path:
    resolved = Path(path).resolve()
    allowed = settings.ALLOWED_INGEST_DIR.resolve()
    if not resolved.is_relative_to(allowed):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied — path must be within {allowed}",
        )
    if not resolved.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Path does not exist: {path}",
        )
    return resolved


def sanitize_filename(filename: str | None) -> str:
    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Upload filename is missing.",
        )
    safe_name = Path(filename).name
    if not safe_name or safe_name.startswith("."):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename.",
        )
    return safe_name



@lru_cache(maxsize=1)
def get_rag_service():
    from app.services.rag_service import RAGService

    return RAGService()


@lru_cache(maxsize=1)
def get_faq_vector_service():
    from app.knowledge_base.vector_index_backend import VectorIndexKnowledgeBaseBackend

    return VectorIndexKnowledgeBaseBackend()


@lru_cache(maxsize=1)
def get_azure_document_service():
    from app.services.azure_document_service import AzureDocumentService

    return AzureDocumentService()


@lru_cache(maxsize=1)
def get_kb_ingestion_service():
    from app.knowledge_base.services import KnowledgeBaseIngestionService

    return KnowledgeBaseIngestionService(settings.DB_TYPE, {})


@lru_cache(maxsize=1)
def get_kb_retrieval_service():
    from app.knowledge_base.services import KnowledgeBaseRetrievalService

    return KnowledgeBaseRetrievalService(settings.DB_TYPE, {})
