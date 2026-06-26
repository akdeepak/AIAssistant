from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from typing import List

from app.models.document import Document


def ingest_documents(path: str) -> List[Document]:
    from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader

    pdf_loader = DirectoryLoader(path, glob="**/*.pdf", loader_cls=PyPDFLoader)
    raw_docs = pdf_loader.load()

    try:
        from langchain_community.document_loaders import Docx2txtLoader

        docx_loader = DirectoryLoader(path, glob="**/*.docx", loader_cls=Docx2txtLoader)
        raw_docs.extend(docx_loader.load())
    except ImportError:  # pragma: no cover
        pass

    documents: List[Document] = []
    for doc in raw_docs:
        metadata = dict(doc.metadata)
        metadata["ingested_at"] = datetime.now(timezone.utc).isoformat()
        metadata["source_hash"] = sha256(doc.page_content.encode()).hexdigest()
        documents.append(Document(content=doc.page_content, metadata=metadata))

    return documents
