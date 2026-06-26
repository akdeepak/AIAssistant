from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import Any, Dict

from llama_index.core import (
    Settings as LlamaSettings,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

from app.config import settings
from app.knowledge_base.base import KnowledgeBaseBackend
from app.knowledge_base.index_builder import (
    DefaultIndexBuilder,
    IndexBuilder,
    SemanticIndexBuilder,
)
from app.llm.provider import get_embed_model, get_llm
from app.utils.validators import UUID_RE

logger = logging.getLogger(__name__)


class VectorIndexKnowledgeBaseBackend(KnowledgeBaseBackend):

    def __init__(self, use_semantic_splitter: bool = True) -> None:
        self.upload_dir: Path = settings.UPLOAD_DIR
        self.vector_store_dir: Path = settings.VECTOR_STORE_DIR
        self.use_semantic_splitter = use_semantic_splitter

        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.vector_store_dir.mkdir(parents=True, exist_ok=True)

        embed_model = get_embed_model()
        llm = get_llm()

        LlamaSettings.llm = llm
        LlamaSettings.embed_model = embed_model

        self._index_builder: IndexBuilder = (
            SemanticIndexBuilder(embed_model)
            if use_semantic_splitter
            else DefaultIndexBuilder(embed_model)
        )

    def ingest_file(self, file_path: Path) -> Dict[str, Any]:
        suffix = file_path.suffix.lower()
        if suffix not in settings.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type {suffix}. Allowed: {', '.join(sorted(settings.SUPPORTED_EXTENSIONS))}"
            )

        logger.info("Starting ingestion for file=%s", file_path.name)
        documents = []
        if suffix == ".pdf":
            from app.pdf_parser import parse_pdf
            from app.pdf_parser.converters import to_llamaindex_documents

            parsed_doc = parse_pdf(str(file_path), strategy="auto")
            documents = to_llamaindex_documents(
                parsed_doc,
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
            )
            logger.info(
                "PDF smart-parse complete: complexity=%s parser=%s elements=%d",
                parsed_doc.profile.complexity.value if parsed_doc.profile else "forced",
                parsed_doc.parser_used,
                len(parsed_doc.elements),
            )
        else:
            reader = SimpleDirectoryReader(input_files=[str(file_path)])
            documents = reader.load_data()
        if not documents:
            logger.warning("No readable content found for file=%s", file_path.name)
            raise ValueError("No readable content found in upload")

        if suffix == ".pdf":
            builder = DefaultIndexBuilder(get_embed_model())
        else:
            builder = self._index_builder
        index = builder.build(documents)

        knowledge_base_id = str(uuid.uuid4())
        kb_dir = self.vector_store_dir / knowledge_base_id
        kb_dir.mkdir(parents=True, exist_ok=True)
        index.storage_context.persist(persist_dir=str(kb_dir))
        logger.info(
            "Persisted vector index for KB %s to %s with %d source documents",
            knowledge_base_id,
            kb_dir,
            len(documents),
        )
        return {
            "knowledge_base_id": knowledge_base_id,
            "message": f"Successfully ingested {file_path.name}",
            "documents": len(documents),
        }

    def query(
        self, knowledge_base_id: str, query: str, top_k: int = 3
    ) -> Dict[str, Any]:
        if not UUID_RE.match(knowledge_base_id):
            raise ValueError(
                f"Invalid knowledge_base_id '{knowledge_base_id}' — must be a UUID."
            )

        kb_dir = self.vector_store_dir / knowledge_base_id
        docstore_file = kb_dir / "docstore.json"
        if not docstore_file.exists():
            logger.warning(
                "Query attempted before ingestion. docstore missing at %s",
                docstore_file,
            )
            raise LookupError(
                "No ingested data found for this knowledge base. Run ingestion first."
            )

        storage_context = StorageContext.from_defaults(persist_dir=str(kb_dir))
        index = load_index_from_storage(storage_context)
        query_engine = index.as_query_engine(similarity_top_k=top_k)
        logger.info("Processing query '%s'", query)
        response = query_engine.query(query)
        return {"response": str(response)}
