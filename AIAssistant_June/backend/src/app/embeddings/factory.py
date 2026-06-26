from __future__ import annotations

from typing import List

from app.config import settings
from app.embeddings.base import EmbeddingProvider
from app.utils.logger import get_logger

logger = get_logger(__name__)


class _SentenceTransformerEmbedding:
    """Adapter wrapping LangChain SentenceTransformerEmbeddings."""

    def __init__(self, model_name: str) -> None:
        from langchain_community.embeddings import SentenceTransformerEmbeddings

        self._model = SentenceTransformerEmbeddings(model_name=model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._model.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._model.embed_query(text)


class _FakeEmbedding:
    """Adapter wrapping LangChain FakeEmbeddings (test/fallback only)."""

    def __init__(self, dimension: int) -> None:
        from langchain_community.embeddings import FakeEmbeddings

        self._model = FakeEmbeddings(size=dimension)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._model.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._model.embed_query(text)


def load_embedding_model(
    model_name: str | None = None,
    dimension: int | None = None,
) -> EmbeddingProvider:
    model_name = model_name or settings.EMBED_MODEL_NAME
    dimension = dimension or settings.EMBED_DIMENSION

    try:
        return _SentenceTransformerEmbedding(model_name)
    except Exception as exc:  # pragma: no cover
        logger.warning("Falling back to FakeEmbeddings: %s", exc)
        return _FakeEmbedding(dimension)
