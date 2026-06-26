from fastapi import APIRouter, Depends

from app.api.dependencies import verify_api_key

from .faq import router as faq_router
from .assistant import router as assistant_bot_router
from .azure_documents import router as azure_documents_router
from .knowledge_base import router as knowledge_base_router

router = APIRouter(dependencies=[Depends(verify_api_key)])

router.include_router(faq_router)
router.include_router(assistant_bot_router)
router.include_router(azure_documents_router)
router.include_router(knowledge_base_router)


@router.get("/health", tags=["Health"], summary="Service health check")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
