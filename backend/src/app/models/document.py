from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Document:
    """Framework-agnostic document representation.

    All service-layer code should use this instead of
    langchain_core.documents.Document or llama_index.core.Document.
    Conversion helpers live in the adapter modules
    (ingestion.loader, pdf_parser.converters).
    """

    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
