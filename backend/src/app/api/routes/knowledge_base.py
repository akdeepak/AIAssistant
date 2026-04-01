from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    get_kb_ingestion_service,
    get_kb_retrieval_service,
    validate_ingest_path,
    validate_knowledge_base_id,
)
from app.knowledge_base.services import (
    KnowledgeBaseIngestionService,
    KnowledgeBaseRetrievalService,
)
from app.models.schemas import IngestPathRequest, KBIngestResponse, KBQueryRequest
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/knowledge-bases", tags=["Knowledge Base"])


@router.post(
    "/ingest",
    response_model=KBIngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new knowledge base from a directory",
)
def ingest_knowledge_base(
    payload: IngestPathRequest,
    ingestion_service: KnowledgeBaseIngestionService = Depends(
        get_kb_ingestion_service
    ),
) -> KBIngestResponse:
    validated_path = validate_ingest_path(payload.path)
    try:
        result = ingestion_service.ingest_directory(str(validated_path))
        return KBIngestResponse(**result)
    except Exception as exc:  # pragma: no cover
        logger.exception("Knowledge base ingestion failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to ingest knowledge base",
        )


@router.post(
    "/{knowledge_base_id}/query",
    response_model=List[Dict[str, Any]],
    summary="Query an existing knowledge base",
)
def query_knowledge_base(
    knowledge_base_id: str,
    payload: KBQueryRequest,
    retrieval_service: KnowledgeBaseRetrievalService = Depends(
        get_kb_retrieval_service
    ),
) -> List[Dict[str, Any]]:
    kb_id = validate_knowledge_base_id(knowledge_base_id)
    try:
        return retrieval_service.query(kb_id, payload.query, payload.top_k)
    except Exception as exc:  # pragma: no cover
        logger.exception("Knowledge base query failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to query knowledge base",
        )
