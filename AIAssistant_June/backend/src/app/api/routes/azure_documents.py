from typing import Any, Dict

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.dependencies import (
    get_azure_document_service,
    sanitize_filename,
    validate_knowledge_base_id,
)
from app.models.schemas import AzureDocumentQueryRequest
from app.services.azure_document_service import AzureDocumentService
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/azure-documents", tags=["Azure Documents"])


@router.post(
    "/ingest",
    status_code=status.HTTP_201_CREATED,
    summary="Store an uploaded PDF/DOCX in Azure Blob Storage and index it in Azure AI Search",
)
async def ingest_azure_document(
    file: UploadFile = File(...),
    service: AzureDocumentService = Depends(get_azure_document_service),
) -> Dict[str, Any]:
    safe_name = sanitize_filename(file.filename)
    try:
        return await service.ingest_file(file, safe_name)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except RuntimeError as exc:
        logger.exception("Azure document ingestion configuration/runtime error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )
    except Exception as exc:  # pragma: no cover
        logger.exception("Azure document ingestion failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to ingest document into Azure services",
        )


@router.post(
    "/{document_id}/query",
    summary="Query indexed document chunks by document id",
)
def query_azure_document(
    document_id: str,
    payload: AzureDocumentQueryRequest,
    service: AzureDocumentService = Depends(get_azure_document_service),
) -> Dict[str, Any]:
    validated_document_id = validate_knowledge_base_id(document_id)
    try:
        return service.query_document(
            validated_document_id,
            payload.query,
            payload.top_k,
        )
    except RuntimeError as exc:
        logger.exception("Azure document query configuration/runtime error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )
    except Exception as exc:  # pragma: no cover
        logger.exception("Azure document query failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to query Azure AI Search index",
        )
