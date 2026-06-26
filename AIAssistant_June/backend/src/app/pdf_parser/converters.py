"""Converters from ParsedDocument to framework-specific document objects."""

from __future__ import annotations

from typing import List

from app.models.document import Document
from app.pdf_parser.models import ParsedDocument


def to_documents(
    parsed_doc: ParsedDocument,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> List[Document]:
    chunks = parsed_doc.to_chunks(chunk_size, chunk_overlap)
    return [Document(content=c["text"], metadata=c["metadata"]) for c in chunks]


def to_langchain_documents(
    parsed_doc: ParsedDocument,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
):
    try:
        from langchain_core.documents import Document as LCDocument
    except ImportError:
        from langchain.schema import Document as LCDocument  # type: ignore[no-redef]

    chunks = parsed_doc.to_chunks(chunk_size, chunk_overlap)
    return [LCDocument(page_content=c["text"], metadata=c["metadata"]) for c in chunks]


def to_llamaindex_documents(
    parsed_doc: ParsedDocument,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
):
    from llama_index.core import Document as LIDocument

    chunks = parsed_doc.to_chunks(chunk_size, chunk_overlap)
    return [LIDocument(text=c["text"], metadata=c["metadata"]) for c in chunks]
