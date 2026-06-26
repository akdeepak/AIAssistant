from __future__ import annotations

from typing import List, Protocol, runtime_checkable


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Abstraction over embedding backends.

    Implementations wrap framework-specific classes (LangChain, LlamaIndex,
    sentence-transformers, etc.) so that the service layer never imports
    those frameworks directly.
    """

    def embed_documents(self, texts: List[str]) -> List[List[float]]: ...

    def embed_query(self, text: str) -> List[float]: ...
