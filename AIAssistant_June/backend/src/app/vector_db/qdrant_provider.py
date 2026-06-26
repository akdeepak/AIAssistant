from __future__ import annotations

from functools import lru_cache

from qdrant_client import QdrantClient

from app.config import settings


@lru_cache(maxsize=1)
def get_qdrant_client() -> QdrantClient:
    api_key = settings.QDRANT_API_KEY or None
    return QdrantClient(url=settings.QDRANT_URL, api_key=api_key)
