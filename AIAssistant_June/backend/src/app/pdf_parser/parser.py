"""PDF parser back-ends and the unified ``parse_pdf`` entry point."""

from __future__ import annotations

import logging
from typing import Callable, Dict, Optional

from app.pdf_parser.models import (
    DocumentProfile,
    ElementType,
    ParsedDocument,
    ParsedElement,
)

logger = logging.getLogger(__name__)


def _parse_with_unstructured_hires(file_path: str) -> Optional[ParsedDocument]:
    try:
        from unstructured.partition.pdf import partition_pdf

        logger.info("Parser: unstructured (hi_res) for %s", file_path)
        elements = partition_pdf(
            filename=file_path,
            strategy="hi_res",
            infer_table_structure=True,
            include_page_breaks=True,
            languages=["eng"],
        )
        return _convert_unstructured(elements, file_path, "unstructured_hires")
    except ImportError:
        logger.debug("unstructured[pdf] not installed.")
        return None
    except Exception as e:
        logger.warning("unstructured (hi_res) failed: %s", e)
        return None


def _parse_with_unstructured_fast(file_path: str) -> Optional[ParsedDocument]:
    try:
        from unstructured.partition.pdf import partition_pdf

        logger.info("Parser: unstructured (fast) for %s", file_path)
        elements = partition_pdf(
            filename=file_path,
            strategy="fast",
            include_page_breaks=True,
        )
        return _convert_unstructured(elements, file_path, "unstructured_fast")
    except ImportError:
        logger.debug("unstructured not installed.")
        return None
    except Exception as e:
        logger.warning("unstructured (fast) failed: %s", e)
        return None


def _parse_with_pymupdf(file_path: str) -> Optional[ParsedDocument]:
    try:
        import fitz

        logger.info("Parser: PyMuPDF for %s", file_path)
        doc = fitz.open(file_path)
        parsed_elements: list[ParsedElement] = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict", sort=True)["blocks"]

            for block in blocks:
                if block["type"] == 0:  # text block
                    text = ""
                    for line in block.get("lines", []):
                        line_text = " ".join(
                            span["text"] for span in line.get("spans", [])
                        )
                        text += line_text + "\n"
                    text = text.strip()
                    if not text:
                        continue
                    parsed_elements.append(
                        ParsedElement(
                            text=text,
                            element_type=(
                                ElementType.TABLE
                                if _heuristic_is_table(text)
                                else ElementType.NARRATIVE_TEXT
                            ),
                            page_number=page_num + 1,
                            metadata={"bbox": block.get("bbox", [])},
                        )
                    )
                elif block["type"] == 1:  # image block
                    parsed_elements.append(
                        ParsedElement(
                            text="[Image]",
                            element_type=ElementType.UNKNOWN,
                            page_number=page_num + 1,
                            metadata={"is_image": True},
                        )
                    )

            # PyMuPDF built-in table finder (v1.23+)
            try:
                tables = page.find_tables()
                for table in tables:
                    table_data = table.extract()
                    if table_data:
                        table_text = _format_table_data(table_data)
                        if table_text.strip():
                            parsed_elements.append(
                                ParsedElement(
                                    text=table_text,
                                    element_type=ElementType.TABLE,
                                    page_number=page_num + 1,
                                    metadata={
                                        "extraction_method": "pymupdf_table_finder"
                                    },
                                )
                            )
            except AttributeError:
                pass

        total = len(doc)
        doc.close()
        return ParsedDocument(
            elements=parsed_elements,
            source_path=file_path,
            parser_used="pymupdf",
            total_pages=total,
        )
    except ImportError:
        logger.debug("PyMuPDF not installed.")
        return None
    except Exception as e:
        logger.warning("PyMuPDF failed: %s", e)
        return None


def _parse_with_pypdf(file_path: str) -> Optional[ParsedDocument]:
    try:
        from pypdf import PdfReader

        logger.info("Parser: pypdf for %s", file_path)
        reader = PdfReader(file_path)
        parsed_elements: list[ParsedElement] = []
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                parsed_elements.append(
                    ParsedElement(
                        text=text.strip(),
                        element_type=ElementType.NARRATIVE_TEXT,
                        page_number=page_num + 1,
                    )
                )
        return ParsedDocument(
            elements=parsed_elements,
            source_path=file_path,
            parser_used="pypdf",
            total_pages=len(reader.pages),
        )
    except ImportError:
        logger.debug("pypdf not installed.")
        return None
    except Exception as e:
        logger.error("pypdf failed: %s", e)
        return None


def _convert_unstructured(elements, file_path: str, parser_name: str) -> ParsedDocument:
    from unstructured.documents.elements import (
        Footer,
        Header,
        ListItem,
        NarrativeText,
        PageBreak,
        Table,
        Title,
    )

    type_map = {
        Title: ElementType.TITLE,
        NarrativeText: ElementType.NARRATIVE_TEXT,
        Table: ElementType.TABLE,
        ListItem: ElementType.LIST_ITEM,
        Header: ElementType.HEADER,
        Footer: ElementType.FOOTER,
        PageBreak: ElementType.PAGE_BREAK,
    }

    parsed: list[ParsedElement] = []
    max_page = 0
    for el in elements:
        el_type = type_map.get(type(el), ElementType.UNKNOWN)
        page_num = (
            getattr(el.metadata, "page_number", None)
            if hasattr(el, "metadata")
            else None
        )
        if page_num and page_num > max_page:
            max_page = page_num

        extra: dict = {}
        if hasattr(el, "metadata"):
            html = getattr(el.metadata, "text_as_html", None)
            if html:
                extra["html"] = html

        parsed.append(
            ParsedElement(
                text=el.text if hasattr(el, "text") else str(el),
                element_type=el_type,
                page_number=page_num,
                metadata=extra,
            )
        )

    return ParsedDocument(
        elements=parsed,
        source_path=file_path,
        parser_used=parser_name,
        total_pages=max_page if max_page > 0 else None,
    )


def _heuristic_is_table(text: str) -> bool:
    lines = text.strip().split("\n")
    if len(lines) < 2:
        return False
    tab_lines = sum(1 for ln in lines if "\t" in ln or "  " in ln)
    pipe_lines = sum(1 for ln in lines if "|" in ln)
    pct_lines = sum(1 for ln in lines if "%" in ln)
    if tab_lines > len(lines) * 0.5:
        return True
    if pipe_lines > len(lines) * 0.5:
        return True
    if pct_lines > len(lines) * 0.4 and len(lines) >= 3:
        return True
    return False


def _format_table_data(table_data: list) -> str:
    if not table_data:
        return ""
    return "\n".join(
        " | ".join(str(cell).strip() if cell else "" for cell in row)
        for row in table_data
    )

_PARSER_REGISTRY: Dict[str, Callable[[str], Optional[ParsedDocument]]] = {
    "hires": _parse_with_unstructured_hires,
    "fast": _parse_with_unstructured_fast,
    "pymupdf": _parse_with_pymupdf,
    "pypdf": _parse_with_pypdf,
}


def parse_pdf(
    file_path: str,
    strategy: str = "auto",
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    return_chunks: bool = False,
) -> ParsedDocument:
    import os

    file_path = str(file_path)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF not found: {file_path}")
    if not file_path.lower().endswith(".pdf"):
        raise ValueError(f"Not a PDF file: {file_path}")

    profile: Optional[DocumentProfile] = None

    if strategy == "auto":
        from app.pdf_parser.detector import (
            detect_document_profile,
            select_parsers_for_profile,
        )

        logger.info("Strategy=auto → detecting document profile …")
        profile = detect_document_profile(file_path)
        parser_order = select_parsers_for_profile(profile)
        logger.info(
            "Detected: %s → parser order: %s",
            profile.complexity.value,
            " → ".join(parser_order),
        )
    else:
        if strategy not in _PARSER_REGISTRY:
            raise ValueError(
                f"Unknown strategy '{strategy}'. "
                f"Choose from: auto, {', '.join(_PARSER_REGISTRY)}"
            )
        parser_order = [strategy]

    result: Optional[ParsedDocument] = None
    for parser_name in parser_order:
        parse_func = _PARSER_REGISTRY[parser_name]
        result = parse_func(file_path)
        if result and result.elements:
            break

    if not result or not result.elements:
        raise RuntimeError(
            f"All parsers failed for {file_path}. "
            "Install at least one: pip install PyMuPDF  OR  pip install pypdf"
        )

    result.elements = [el for el in result.elements if el.text.strip()]
    result.profile = profile

    if return_chunks:
        result.metadata["chunks"] = result.to_chunks(chunk_size, chunk_overlap)

    logger.info(
        "Parsed: file=%s complexity=%s parser=%s elements=%d pages=%s",
        os.path.basename(file_path),
        profile.complexity.value if profile else "forced",
        result.parser_used,
        len(result.elements),
        result.total_pages,
    )
    return result
