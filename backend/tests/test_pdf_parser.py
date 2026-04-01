import pytest

from app.pdf_parser.models import (
    DocumentComplexity,
    DocumentProfile,
    ElementType,
    ParsedDocument,
    ParsedElement,
)
from app.pdf_parser.detector import select_parsers_for_profile, _classify
from app.pdf_parser.parser import _heuristic_is_table, parse_pdf


class TestDocumentProfile:
    def test_repr(self):
        p = DocumentProfile(
            complexity=DocumentComplexity.COMPLEX,
            total_pages=12,
            has_tables=True,
            has_multi_columns=True,
        )
        assert "COMPLEX" not in repr(p)  # enum .value is lowercase
        assert "complex" in repr(p)
        assert "pages=12" in repr(p)

    def test_defaults(self):
        p = DocumentProfile(complexity=DocumentComplexity.SIMPLE, total_pages=1)
        assert p.has_tables is False
        assert p.is_scanned is False
        assert p.reasons == []


class TestParsedDocument:
    @staticmethod
    def _make_doc() -> ParsedDocument:
        return ParsedDocument(
            elements=[
                ParsedElement("Title", ElementType.TITLE, 1),
                ParsedElement("Some narrative text.", ElementType.NARRATIVE_TEXT, 1),
                ParsedElement("Col1 | Col2\nA | B", ElementType.TABLE, 2),
                ParsedElement("Another paragraph.", ElementType.NARRATIVE_TEXT, 2),
            ],
            source_path="test.pdf",
            parser_used="test",
            total_pages=2,
            profile=DocumentProfile(
                complexity=DocumentComplexity.MODERATE, total_pages=2
            ),
        )

    def test_full_text(self):
        doc = self._make_doc()
        assert "Title" in doc.full_text
        assert "narrative" in doc.full_text

    def test_tables_property(self):
        doc = self._make_doc()
        assert len(doc.tables) == 1

    def test_narrative_elements(self):
        doc = self._make_doc()
        types = {e.element_type for e in doc.narrative_elements}
        assert ElementType.TABLE not in types

    def test_get_page(self):
        doc = self._make_doc()
        assert len(doc.get_page(1)) == 2
        assert len(doc.get_page(2)) == 2
        assert len(doc.get_page(99)) == 0

    def test_to_chunks_basic(self):
        doc = self._make_doc()
        chunks = doc.to_chunks(chunk_size=5000)
        assert len(chunks) >= 2  # at least 1 table + 1 text
        types = {c["metadata"]["type"] for c in chunks}
        assert "table" in types
        assert "text" in types
        for c in chunks:
            assert c["metadata"]["parser"] == "test"

    def test_to_chunks_splits_large_text(self):
        big_text = "word " * 600  # ~3000 chars
        doc = ParsedDocument(
            elements=[
                ParsedElement(big_text, ElementType.NARRATIVE_TEXT, 1),
                ParsedElement(big_text, ElementType.NARRATIVE_TEXT, 2),
            ],
            source_path="big.pdf",
            parser_used="test",
        )
        chunks = doc.to_chunks(chunk_size=1000, chunk_overlap=100)
        assert len(chunks) >= 2



class TestClassify:
    def test_scanned(self):
        c, r = _classify(
            is_scanned=True,
            has_multi_columns=False,
            has_tables=False,
            total_tables_est=0,
            avg_text_density=10,
            low_text_pages=4,
            pages_to_scan=5,
            total_images=10,
            multi_column_pages=0,
        )
        assert c == DocumentComplexity.SCANNED

    def test_complex_multi_col_and_tables(self):
        c, _ = _classify(
            is_scanned=False,
            has_multi_columns=True,
            has_tables=True,
            total_tables_est=5,
            avg_text_density=800,
            low_text_pages=0,
            pages_to_scan=5,
            total_images=0,
            multi_column_pages=3,
        )
        assert c == DocumentComplexity.COMPLEX

    def test_complex_multi_col_only(self):
        c, _ = _classify(
            is_scanned=False,
            has_multi_columns=True,
            has_tables=False,
            total_tables_est=0,
            avg_text_density=800,
            low_text_pages=0,
            pages_to_scan=5,
            total_images=0,
            multi_column_pages=2,
        )
        assert c == DocumentComplexity.COMPLEX

    def test_complex_many_tables(self):
        c, _ = _classify(
            is_scanned=False,
            has_multi_columns=False,
            has_tables=True,
            total_tables_est=5,
            avg_text_density=800,
            low_text_pages=0,
            pages_to_scan=5,
            total_images=0,
            multi_column_pages=0,
        )
        assert c == DocumentComplexity.COMPLEX

    def test_moderate_few_tables(self):
        c, _ = _classify(
            is_scanned=False,
            has_multi_columns=False,
            has_tables=True,
            total_tables_est=2,
            avg_text_density=400,
            low_text_pages=0,
            pages_to_scan=5,
            total_images=0,
            multi_column_pages=0,
        )
        assert c == DocumentComplexity.MODERATE

    def test_moderate_dense_text(self):
        c, _ = _classify(
            is_scanned=False,
            has_multi_columns=False,
            has_tables=False,
            total_tables_est=0,
            avg_text_density=800,
            low_text_pages=0,
            pages_to_scan=5,
            total_images=0,
            multi_column_pages=0,
        )
        assert c == DocumentComplexity.MODERATE

    def test_simple(self):
        c, _ = _classify(
            is_scanned=False,
            has_multi_columns=False,
            has_tables=False,
            total_tables_est=0,
            avg_text_density=200,
            low_text_pages=0,
            pages_to_scan=5,
            total_images=0,
            multi_column_pages=0,
        )
        assert c == DocumentComplexity.SIMPLE


class TestSelectParsers:
    def test_scanned_order(self):
        p = DocumentProfile(complexity=DocumentComplexity.SCANNED, total_pages=5)
        order = select_parsers_for_profile(p)
        assert order[0] == "hires"

    def test_complex_order(self):
        p = DocumentProfile(complexity=DocumentComplexity.COMPLEX, total_pages=5)
        order = select_parsers_for_profile(p)
        assert order[0] == "hires"
        assert order[1] == "pymupdf"

    def test_moderate_order(self):
        p = DocumentProfile(complexity=DocumentComplexity.MODERATE, total_pages=5)
        order = select_parsers_for_profile(p)
        assert order[0] == "pymupdf"

    def test_simple_order(self):
        p = DocumentProfile(complexity=DocumentComplexity.SIMPLE, total_pages=5)
        order = select_parsers_for_profile(p)
        assert order[0] == "pymupdf"
        assert order[1] == "pypdf"


class TestHeuristicIsTable:
    def test_pipe_table(self):
        text = "A | B | C\n1 | 2 | 3\n4 | 5 | 6"
        assert _heuristic_is_table(text) is True

    def test_percentage_table(self):
        text = "Item 10%\nItem 20%\nItem 30%\nItem 40%"
        assert _heuristic_is_table(text) is True

    def test_plain_paragraph(self):
        text = "This is a normal paragraph of text."
        assert _heuristic_is_table(text) is False

    def test_single_line(self):
        assert _heuristic_is_table("single") is False



class TestParsePdfValidation:
    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            parse_pdf("/nonexistent/path/file.pdf")

    def test_not_a_pdf(self, tmp_path):
        txt = tmp_path / "file.txt"
        txt.write_text("hello")
        with pytest.raises(ValueError, match="Not a PDF"):
            parse_pdf(str(txt))

    def test_unknown_strategy(self, tmp_path):
        pdf = tmp_path / "dummy.pdf"
        pdf.write_bytes(b"%PDF-1.4 fake")
        with pytest.raises(ValueError, match="Unknown strategy"):
            parse_pdf(str(pdf), strategy="banana")
