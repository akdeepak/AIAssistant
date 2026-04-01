from __future__ import annotations

from typing import List, Protocol, runtime_checkable

from app.models.document import Document


@runtime_checkable
class TextSplitter(Protocol):
    """Abstraction over text/document splitting strategies."""

    def split(self, documents: List[Document]) -> List[Document]: ...


class RecursiveTextSplitter:
    """TextSplitter backed by LangChain's RecursiveCharacterTextSplitter.

    All LangChain usage is confined to this adapter class.
    """

    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        self._impl = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

    def split(self, documents: List[Document]) -> List[Document]:
        from langchain_core.documents import Document as LCDocument

        lc_docs = [
            LCDocument(page_content=d.content, metadata=d.metadata)
            for d in documents
        ]
        lc_chunks = self._impl.split_documents(lc_docs)
        return [
            Document(content=c.page_content, metadata=c.metadata)
            for c in lc_chunks
        ]
