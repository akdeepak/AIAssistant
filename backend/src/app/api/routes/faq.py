from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_rag_service, validate_ingest_path
from app.models.schemas import FAQDocumentResponse, FAQQueryRequest, IngestPathRequest
from app.services.rag_service import RAGService
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/faqs", tags=["FAQs"])


@router.post(
    "/ingest",
    response_model=List[FAQDocumentResponse],
    summary="Ingest FAQ documents with LangChain",
)
def ingest_faqs(
    payload: IngestPathRequest,
    faq_service: RAGService = Depends(get_rag_service),
) -> List[FAQDocumentResponse]:
    validated_path = validate_ingest_path(payload.path)
    try:
        return faq_service.ingest(str(validated_path))
    except Exception as exc:  # pragma: no cover
        logger.exception("FAQ ingestion failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to ingest FAQ documents",
        )


@router.post(
    "/query",
    response_model=List[FAQDocumentResponse],
    summary="Query ingested FAQs with LangChain retrieval",
)
def query_faqs(
    payload: FAQQueryRequest,
    faq_service: RAGService = Depends(get_rag_service),
) -> List[FAQDocumentResponse]:
    try:
        return faq_service.query(payload.query, payload.top_k)
    except Exception as exc:  # pragma: no cover
        logger.exception("FAQ query failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to query FAQs",
        )
