"""Data models for the smart PDF parser."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ElementType(Enum):
    """Categories of parsed content elements."""

    TITLE = "title"
    NARRATIVE_TEXT = "narrative_text"
    TABLE = "table"
    LIST_ITEM = "list_item"
    HEADER = "header"
    FOOTER = "footer"
    PAGE_BREAK = "page_break"
    UNKNOWN = "unknown"


class DocumentComplexity(Enum):
    """Detected complexity level of a PDF document."""

    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    SCANNED = "scanned"


@dataclass
class DocumentProfile:
    """Profile produced by the smart-detection scan."""

    complexity: DocumentComplexity
    total_pages: int
    has_tables: bool = False
    has_multi_columns: bool = False
    has_images: bool = False
    is_scanned: bool = False
    text_density: float = 0.0
    table_count_estimate: int = 0
    image_count: int = 0
    reasons: list = field(default_factory=list)

    def __repr__(self) -> str:
        return (
            f"DocumentProfile(complexity={self.complexity.value}, "
            f"pages={self.total_pages}, tables={self.has_tables}, "
            f"multi_col={self.has_multi_columns}, scanned={self.is_scanned})"
        )


@dataclass
class ParsedElement:
    """A single parsed element from a PDF document."""

    text: str
    element_type: ElementType = ElementType.UNKNOWN
    page_number: Optional[int] = None
    metadata: dict = field(default_factory=dict)

    def __repr__(self) -> str:
        preview = self.text[:80].replace("\n", " ")
        return (
            f"ParsedElement({self.element_type.value}, "
            f"page={self.page_number}, '{preview}...')"
        )


@dataclass
class ParsedDocument:
    """Complete parsed document with elements and metadata."""

    elements: list  # List[ParsedElement]
    source_path: str
    parser_used: str
    total_pages: Optional[int] = None
    profile: Optional[DocumentProfile] = None
    metadata: dict = field(default_factory=dict)

    @property
    def full_text(self) -> str:
        return "\n\n".join(el.text for el in self.elements if el.text.strip())

    @property
    def tables(self) -> list:
        return [el for el in self.elements if el.element_type == ElementType.TABLE]

    @property
    def narrative_elements(self) -> list:
        return [
            el
            for el in self.elements
            if el.element_type
            in (ElementType.NARRATIVE_TEXT, ElementType.TITLE, ElementType.LIST_ITEM)
        ]

    def get_page(self, page_num: int) -> list:
        return [el for el in self.elements if el.page_number == page_num]

    def to_chunks(self, chunk_size: int = 1000, chunk_overlap: int = 200) -> list:
        chunks: list = []
        complexity_label = self.profile.complexity.value if self.profile else "unknown"

        for el in self.tables:
            text = el.text.strip()
            if text:
                chunks.append({
                    "text": text,
                    "metadata": {
                        "source": self.source_path,
                        "page": el.page_number,
                        "type": "table",
                        "parser": self.parser_used,
                        "complexity": complexity_label,
                        **el.metadata,
                    },
                })

        current_chunk = ""
        current_page = None
        for el in self.narrative_elements:
            text = el.text.strip()
            if not text:
                continue

            if len(current_chunk) + len(text) + 2 > chunk_size and current_chunk:
                chunks.append({
                    "text": current_chunk.strip(),
                    "metadata": {
                        "source": self.source_path,
                        "page": current_page,
                        "type": "text",
                        "parser": self.parser_used,
                        "complexity": complexity_label,
                    },
                })
                if chunk_overlap > 0:
                    current_chunk = current_chunk[-chunk_overlap:] + "\n\n" + text
                else:
                    current_chunk = text
            else:
                current_chunk = current_chunk + "\n\n" + text if current_chunk else text
            current_page = el.page_number

        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "metadata": {
                    "source": self.source_path,
                    "page": current_page,
                    "type": "text",
                    "parser": self.parser_used,
                    "complexity": complexity_label,
                },
            })

        return chunks
