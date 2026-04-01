"""Document-structure detection for PDF files."""

from __future__ import annotations

import logging
import re
from typing import List

from app.pdf_parser.models import DocumentComplexity, DocumentProfile

logger = logging.getLogger(__name__)


def detect_document_profile(file_path: str, sample_pages: int = 5) -> DocumentProfile:

    try:
        import fitz  # PyMuPDF
    except ImportError:
        logger.warning(
            "PyMuPDF not installed — cannot detect profile. Assuming MODERATE."
        )
        return DocumentProfile(
            complexity=DocumentComplexity.MODERATE,
            total_pages=0,
            reasons=["PyMuPDF not available for detection"],
        )

    doc = fitz.open(file_path)
    total_pages = len(doc)
    pages_to_scan = min(sample_pages, total_pages)

    reasons: list[str] = []
    total_text_chars = 0
    total_images = 0
    total_tables_est = 0
    multi_column_pages = 0
    low_text_pages = 0

    for page_idx in range(pages_to_scan):
        page = doc[page_idx]
        page_width = page.rect.width


        text = page.get_text("text")
        char_count = len(text.strip())
        total_text_chars += char_count
        if char_count < 50:
            low_text_pages += 1

        total_images += len(page.get_images(full=True))

        total_tables_est += _count_tables_on_page(page, text)


        if _page_is_multi_column(page, page_width):
            multi_column_pages += 1

    doc.close()


    avg_text_density = total_text_chars / pages_to_scan if pages_to_scan else 0
    has_tables = total_tables_est > 0
    has_multi_columns = multi_column_pages >= 1
    has_images = total_images > 0
    is_scanned = low_text_pages > pages_to_scan * 0.5 and has_images

    complexity, reasons = _classify(
        is_scanned=is_scanned,
        has_multi_columns=has_multi_columns,
        has_tables=has_tables,
        total_tables_est=total_tables_est,
        avg_text_density=avg_text_density,
        low_text_pages=low_text_pages,
        pages_to_scan=pages_to_scan,
        total_images=total_images,
        multi_column_pages=multi_column_pages,
    )

    profile = DocumentProfile(
        complexity=complexity,
        total_pages=total_pages,
        has_tables=has_tables,
        has_multi_columns=has_multi_columns,
        has_images=has_images,
        is_scanned=is_scanned,
        text_density=avg_text_density,
        table_count_estimate=total_tables_est,
        image_count=total_images,
        reasons=reasons,
    )
    logger.info("Document profile: %s | Reasons: %s", profile, "; ".join(reasons))
    return profile


def select_parsers_for_profile(profile: DocumentProfile) -> List[str]:
    mapping = {
        DocumentComplexity.SCANNED: ["hires", "fast", "pymupdf", "pypdf"],
        DocumentComplexity.COMPLEX: ["hires", "pymupdf", "fast", "pypdf"],
        DocumentComplexity.MODERATE: ["pymupdf", "hires", "fast", "pypdf"],
        DocumentComplexity.SIMPLE: ["pymupdf", "pypdf", "fast", "hires"],
    }
    return mapping[profile.complexity]


def _count_tables_on_page(page, text: str) -> int:
    try:
        found = page.find_tables()
        if found and len(found.tables) > 0:
            return len(found.tables)
    except (AttributeError, Exception):
        pass

    # Heuristic: look for aligned numbers, pipes, tabs, percentages
    lines = text.split("\n")
    table_like = sum(
        1
        for line in lines
        if re.search(r"\d+\s*%", line)
        or line.count("\t") >= 2
        or line.count("  ") >= 3
        or "|" in line
    )
    return 1 if table_like > 5 else 0


def _page_is_multi_column(page, page_width: float) -> bool:
    blocks = page.get_text("dict", sort=True).get("blocks", [])
    text_blocks = [b for b in blocks if b.get("type") == 0]
    if len(text_blocks) < 4:
        return False

    mid = page_width / 2
    x_positions = [b["bbox"][0] for b in text_blocks]
    left = sum(1 for x in x_positions if x < mid * 0.4)
    right = sum(1 for x in x_positions if x > mid * 0.6)
    return left >= 2 and right >= 2


def _classify(
    *,
    is_scanned: bool,
    has_multi_columns: bool,
    has_tables: bool,
    total_tables_est: int,
    avg_text_density: float,
    low_text_pages: int,
    pages_to_scan: int,
    total_images: int,
    multi_column_pages: int,
) -> tuple[DocumentComplexity, list[str]]:
    """Return (complexity, reasons) based on detected features."""
    reasons: list[str] = []

    if is_scanned:
        reasons.append(
            f"Low text on {low_text_pages}/{pages_to_scan} pages "
            f"with {total_images} images"
        )
        return DocumentComplexity.SCANNED, reasons

    if has_multi_columns and has_tables:
        reasons.append(
            f"Multi-column on {multi_column_pages} pages + ~{total_tables_est} tables"
        )
        return DocumentComplexity.COMPLEX, reasons

    if has_multi_columns:
        reasons.append(f"Multi-column layout on {multi_column_pages} pages")
        return DocumentComplexity.COMPLEX, reasons

    if has_tables and total_tables_est >= 3:
        reasons.append(f"~{total_tables_est} tables detected (heavy table content)")
        return DocumentComplexity.COMPLEX, reasons

    if has_tables:
        reasons.append(f"~{total_tables_est} tables detected")
        return DocumentComplexity.MODERATE, reasons

    if avg_text_density > 500:
        reasons.append(f"Dense text (avg {avg_text_density:.0f} chars/page)")
        return DocumentComplexity.MODERATE, reasons

    reasons.append(f"Simple text (avg {avg_text_density:.0f} chars/page)")
    return DocumentComplexity.SIMPLE, reasons
