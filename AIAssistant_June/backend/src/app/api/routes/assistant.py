from typing import Any, Dict

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.dependencies import (
    get_faq_vector_service,
    sanitize_filename,
    validate_knowledge_base_id,
)
from app.knowledge_base.vector_index_backend import VectorIndexKnowledgeBaseBackend
from app.models.schemas import FAQVectorQueryRequest
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/ai-assistant", tags=["FAQ Vector Index"])


@router.post(
    "/catalyze",
    status_code=status.HTTP_201_CREATED,
    summary="Ingest a single FAQ file",
)
async def ingest_faq_vector(
    file: UploadFile = File(...),
    service: VectorIndexKnowledgeBaseBackend = Depends(get_faq_vector_service),
) -> Dict[str, Any]:
    safe_name = sanitize_filename(file.filename)
    upload_path = service.upload_dir / safe_name
    try:
        with upload_path.open("wb") as buffer:
            buffer.write(await file.read())
        result = service.ingest_file(upload_path)
        return result
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:  # pragma: no cover
        logger.exception("FAQ vector ingestion failed: %s", exc)
        if upload_path.exists():
            upload_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to ingest FAQ document",
        )


@router.post(
    "/query",
    summary="Query ingested FAQs using the vector index store",
)
async def query_faq_vector(
    payload: FAQVectorQueryRequest,
    service: VectorIndexKnowledgeBaseBackend = Depends(get_faq_vector_service),
) -> Dict[str, Any]:
    kb_id = validate_knowledge_base_id(payload.knowledge_base_id)
    try:
        return service.query(kb_id, payload.query)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except Exception as exc:  # pragma: no cover
        logger.exception("FAQ vector query failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to query FAQ vector index",
        )
