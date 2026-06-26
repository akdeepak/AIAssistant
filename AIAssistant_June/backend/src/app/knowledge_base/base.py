from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict


class KnowledgeBaseBackend(ABC):

    @abstractmethod
    def ingest_file(self, file_path: Path) -> Dict[str, Any]: ...

    @abstractmethod
    def query(
        self, knowledge_base_id: str, query: str, top_k: int = 3
    ) -> Dict[str, Any]: ...
