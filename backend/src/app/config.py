from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class AppSettings:

    API_KEY: str = field(default_factory=lambda: os.getenv("API_KEY", ""))

    ALLOWED_ORIGINS: List[str] = field(
        default_factory=lambda: [
            x.strip()
            for x in os.getenv(
                "ALLOWED_ORIGINS",
                "http://localhost,http://localhost:3000,http://127.0.0.1:3000",
            ).split(",")
        ]
    )

    AZURE_KEY: str = field(default_factory=lambda: os.getenv("AZURE_KEY", ""))
    AZURE_ENDPOINT: str = field(default_factory=lambda: os.getenv("AZURE_ENDPOINT", ""))
    AZURE_API_VERSION: str = field(
        default_factory=lambda: os.getenv("AZURE_API_VERSION", "2024-12-01-preview")
    )
    AZURE_EMBED_DEPLOYMENT: str = field(
        default_factory=lambda: os.getenv(
            "AZURE_EMBED_DEPLOYMENT", "text-embedding-ada-002"
        )
    )
    AZURE_LLM_DEPLOYMENT: str = field(
        default_factory=lambda: os.getenv("AZURE_LLM_DEPLOYMENT", "gpt-4o")
    )

    EMBED_MODEL_NAME: str = field(
        default_factory=lambda: os.getenv(
            "EMBED_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"
        )
    )
    EMBED_DIMENSION: int = field(
        default_factory=lambda: int(os.getenv("EMBED_DIMENSION", "768"))
    )

    CHUNK_SIZE: int = field(default_factory=lambda: int(os.getenv("CHUNK_SIZE", "800")))
    CHUNK_OVERLAP: int = field(
        default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "100"))
    )

    UPLOAD_DIR: Path = field(
        default_factory=lambda: Path(os.getenv("UPLOAD_DIR", "data/uploads"))
    )
    VECTOR_STORE_DIR: Path = field(
        default_factory=lambda: Path(os.getenv("VECTOR_STORE_DIR", "data/vector_store"))
    )
    ALLOWED_INGEST_DIR: Path = field(
        default_factory=lambda: Path(os.getenv("ALLOWED_INGEST_DIR", "data"))
    )

    DB_TYPE: str = field(default_factory=lambda: os.getenv("DB_TYPE", "qdrant"))

    SUPPORTED_EXTENSIONS: frozenset = field(
        default_factory=lambda: frozenset({".docx", ".pdf"})
    )

    VECTOR_INDEX_STORAGE_MODE: str = field(
        default_factory=lambda: os.getenv("VECTOR_INDEX_STORAGE_MODE", "hybrid").lower()
    )

    QDRANT_URL: str = field(
        default_factory=lambda: os.getenv("QDRANT_URL", "http://localhost:6333")
    )
    QDRANT_API_KEY: str = field(default_factory=lambda: os.getenv("QDRANT_API_KEY", ""))
    QDRANT_COLLECTION_PREFIX: str = field(
        default_factory=lambda: os.getenv("QDRANT_COLLECTION_PREFIX", "kb")
    )


settings = AppSettings()
