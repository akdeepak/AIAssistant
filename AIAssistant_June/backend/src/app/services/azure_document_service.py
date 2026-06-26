from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict, List

from fastapi import UploadFile

from app.config import settings
from app.ingestion.splitter import RecursiveTextSplitter
from app.models.document import Document
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AzureDocumentService:
    """Azure Blob Storage + Azure AI Search implementation for uploaded files."""

    def __init__(self) -> None:
        self.upload_dir: Path = settings.UPLOAD_DIR
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self._splitter = RecursiveTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )

    async def ingest_file(self, file: UploadFile, safe_name: str) -> Dict[str, Any]:
        self._validate_settings()
        suffix = Path(safe_name).suffix.lower()
        if suffix not in settings.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type {suffix}. Allowed: {', '.join(sorted(settings.SUPPORTED_EXTENSIONS))}"
            )

        document_id = str(uuid.uuid4())
        file_bytes = await file.read()
        if not file_bytes:
            raise ValueError("Uploaded file is empty.")

        local_path = self.upload_dir / f"{document_id}_{safe_name}"
        local_path.write_bytes(file_bytes)

        blob_name = f"{document_id}/{safe_name}"
        blob_url = self._upload_blob(blob_name, file_bytes, file.content_type)

        try:
            source_documents = self._extract_documents(
                local_path,
                document_id,
                safe_name,
                blob_url,
            )
            chunks = self._splitter.split(source_documents) or source_documents
            self._ensure_index()
            indexed = self._index_chunks(document_id, safe_name, blob_url, chunks)
        finally:
            local_path.unlink(missing_ok=True)

        return {
            "document_id": document_id,
            "file_name": safe_name,
            "blob_url": blob_url,
            "chunks": indexed,
            "message": f"Successfully stored and indexed {safe_name}",
        }

    def query_document(
        self,
        document_id: str,
        query: str,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        self._validate_settings()
        self._ensure_index()

        search_client = self._search_client()
        results = search_client.search(
            search_text=query,
            filter=f"document_id eq '{document_id}'",
            top=top_k,
            select=[
                "id",
                "document_id",
                "file_name",
                "blob_url",
                "content",
                "chunk_index",
            ],
        )

        matches: List[Dict[str, Any]] = []
        for result in results:
            matches.append(
                {
                    "chunk_id": result["id"],
                    "document_id": result["document_id"],
                    "file_name": result["file_name"],
                    "blob_url": result["blob_url"],
                    "chunk_index": result["chunk_index"],
                    "content": result["content"],
                    "score": result.get("@search.score"),
                }
            )

        return {
            "document_id": document_id,
            "query": query,
            "results": matches,
            "total_results": len(matches),
        }

    def _validate_settings(self) -> None:
        missing = []
        if not settings.AZURE_BLOB_CONNECTION_STRING:
            missing.append("AZURE_BLOB_CONNECTION_STRING")
        if not settings.AZURE_SEARCH_ENDPOINT:
            missing.append("AZURE_SEARCH_ENDPOINT")
        if not settings.AZURE_SEARCH_API_KEY:
            missing.append("AZURE_SEARCH_API_KEY")
        if missing:
            raise RuntimeError(
                "Missing Azure configuration: " + ", ".join(missing)
            )

    def _blob_service_client(self) -> Any:
        from azure.storage.blob import BlobServiceClient

        return BlobServiceClient.from_connection_string(
            settings.AZURE_BLOB_CONNECTION_STRING
        )

    def _search_client(self) -> Any:
        from azure.core.credentials import AzureKeyCredential
        from azure.search.documents import SearchClient

        return SearchClient(
            endpoint=settings.AZURE_SEARCH_ENDPOINT,
            index_name=settings.AZURE_SEARCH_INDEX_NAME,
            credential=AzureKeyCredential(settings.AZURE_SEARCH_API_KEY),
        )

    def _search_index_client(self) -> Any:
        from azure.core.credentials import AzureKeyCredential
        from azure.search.documents.indexes import SearchIndexClient

        return SearchIndexClient(
            endpoint=settings.AZURE_SEARCH_ENDPOINT,
            credential=AzureKeyCredential(settings.AZURE_SEARCH_API_KEY),
        )

    def _upload_blob(
        self,
        blob_name: str,
        file_bytes: bytes,
        content_type: str | None,
    ) -> str:
        from azure.storage.blob import ContentSettings

        blob_service = self._blob_service_client()
        container_client = blob_service.get_container_client(
            settings.AZURE_BLOB_CONTAINER_NAME
        )
        if not container_client.exists():
            container_client.create_container()

        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(
            file_bytes,
            overwrite=True,
            content_settings=ContentSettings(
                content_type=content_type or "application/octet-stream"
            ),
        )
        return blob_client.url

    def _extract_documents(
        self,
        file_path: Path,
        document_id: str,
        file_name: str,
        blob_url: str,
    ) -> List[Document]:
        suffix = file_path.suffix.lower()
        metadata = {
            "document_id": document_id,
            "file_name": file_name,
            "blob_url": blob_url,
        }

        if suffix == ".pdf":
            from app.pdf_parser import parse_pdf

            parsed_doc = parse_pdf(str(file_path), strategy="auto")
            return [
                Document(
                    content=chunk["text"],
                    metadata={**metadata, **chunk.get("metadata", {})},
                )
                for chunk in parsed_doc.to_chunks(
                    chunk_size=settings.CHUNK_SIZE,
                    chunk_overlap=settings.CHUNK_OVERLAP,
                )
                if chunk.get("text")
            ]

        from langchain_community.document_loaders import Docx2txtLoader

        raw_docs = Docx2txtLoader(str(file_path)).load()
        return [
            Document(
                content=doc.page_content,
                metadata={**metadata, **dict(doc.metadata)},
            )
            for doc in raw_docs
            if doc.page_content
        ]

    def _ensure_index(self) -> None:
        from azure.search.documents.indexes.models import (
            SearchableField,
            SearchFieldDataType,
            SearchIndex,
            SimpleField,
        )

        index_client = self._search_index_client()
        index_names = [name for name in index_client.list_index_names()]
        if settings.AZURE_SEARCH_INDEX_NAME in index_names:
            return

        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SimpleField(
                name="document_id",
                type=SearchFieldDataType.String,
                filterable=True,
                sortable=True,
            ),
            SearchableField(
                name="file_name",
                type=SearchFieldDataType.String,
                filterable=True,
            ),
            SimpleField(name="blob_url", type=SearchFieldDataType.String),
            SearchableField(name="content", type=SearchFieldDataType.String),
            SimpleField(
                name="chunk_index",
                type=SearchFieldDataType.Int32,
                filterable=True,
                sortable=True,
            ),
            SimpleField(
                name="metadata_json",
                type=SearchFieldDataType.String,
            ),
        ]
        index_client.create_index(
            SearchIndex(name=settings.AZURE_SEARCH_INDEX_NAME, fields=fields)
        )

    def _index_chunks(
        self,
        document_id: str,
        file_name: str,
        blob_url: str,
        chunks: List[Document],
    ) -> int:
        if not chunks:
            raise ValueError("No readable content found in upload.")

        search_client = self._search_client()
        search_documents = []
        for index, chunk in enumerate(chunks):
            search_documents.append(
                {
                    "id": f"{document_id}-{index}",
                    "document_id": document_id,
                    "file_name": file_name,
                    "blob_url": blob_url,
                    "content": chunk.content,
                    "chunk_index": index,
                    "metadata_json": json.dumps(chunk.metadata, default=str),
                }
            )

        result = search_client.upload_documents(documents=search_documents)
        failed = [item for item in result if not item.succeeded]
        if failed:
            logger.error("Azure AI Search failed to index %d chunks", len(failed))
            raise RuntimeError("Failed to index one or more document chunks.")
        return len(search_documents)
