from __future__ import annotations

from typing import Any, Dict, List, Protocol, runtime_checkable

from app.knowledge_base.vector_index_backend import VectorIndexKnowledgeBaseBackend
from app.models.document import Document
from app.utils.logger import get_logger

logger = get_logger(__name__)


@runtime_checkable
class Retriever(Protocol):
    def retrieve(self, query: str) -> List[Document]: ...


class KnowledgeBaseRetriever:

    def __init__(
        self,
        backend: VectorIndexKnowledgeBaseBackend,
        knowledge_base_id: str,
        top_k: int = 3,
    ) -> None:
        self._backend = backend
        self._knowledge_base_id = knowledge_base_id
        self._top_k = top_k

    def retrieve(self, query: str) -> List[Document]:
        logger.info(
            "KnowledgeBaseRetriever querying KB %s with top_k=%d",
            self._knowledge_base_id,
            self._top_k,
        )
        result = self._backend.query(self._knowledge_base_id, query, self._top_k)
        content = str(result.get("response", ""))
        return [
            Document(
                content=content,
                metadata={"knowledge_base_id": self._knowledge_base_id},
            )
        ]
