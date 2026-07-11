"""Document loaders for supported file types."""

from __future__ import annotations

from pathlib import Path

import pdfplumber
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

from app.services.documents.cleaning import clean_page_text
from app.services.documents.types import ExtractedPage, LoadedDocument
from app.services.documents.utils import infer_document_type, is_supported_document


class DocumentLoader:
    """Load text from PDF, DOCX, TXT, and Markdown documents."""

    def load(self, path: Path) -> LoadedDocument:
        """Load a document into page-level text."""

        if not is_supported_document(path):
            raise ValueError(f"Unsupported document type: {path.suffix}")

        document_type = infer_document_type(path)
        if document_type == "pdf":
            pages = self._load_pdf(path)
        elif document_type == "docx":
            pages = self._load_docx(path)
        else:
            pages = self._load_text(path)

        return LoadedDocument(path=path, document_type=document_type, pages=pages)

    def _load_pdf(self, path: Path) -> list[ExtractedPage]:
        """Extract PDF pages with best-effort table preservation."""

        pages: list[ExtractedPage] = []
        with pdfplumber.open(path) as pdf:
            for index, page in enumerate(pdf.pages, start=1):
                fragments: list[str] = []
                text = page.extract_text(layout=True) or ""
                if text.strip():
                    fragments.append(text.strip())

                tables = page.find_tables() or []
                for table in sorted(tables, key=lambda item: item.bbox[1]):
                    rendered = self._render_table(table.extract())
                    if rendered:
                        fragments.append("[TABLE BEGIN]")
                        fragments.append(rendered)
                        fragments.append("[TABLE END]")

                combined = "\n\n".join(fragments).strip()
                pages.append(
                    ExtractedPage(
                        page=index,
                        text=clean_page_text(combined),
                        source_file=path.name,
                    )
                )
        return pages

    def _load_docx(self, path: Path) -> list[ExtractedPage]:
        """Extract all paragraphs and tables from a DOCX file."""

        document = Document(path)
        parts: list[str] = []
        for block in self._iter_block_items(document):
            if isinstance(block, Paragraph):
                text = block.text.strip()
                if text:
                    parts.append(text)
            elif isinstance(block, Table):
                rendered = self._render_table([[cell.text for cell in row.cells] for row in block.rows])
                if rendered:
                    parts.append("[TABLE BEGIN]")
                    parts.append(rendered)
                    parts.append("[TABLE END]")

        text = clean_page_text("\n\n".join(parts))
        return [ExtractedPage(page=1, text=text, source_file=path.name)]

    def _load_text(self, path: Path) -> list[ExtractedPage]:
        """Extract text or markdown as a single page."""

        text = clean_page_text(path.read_text(encoding="utf-8", errors="ignore"))
        return [ExtractedPage(page=1, text=text, source_file=path.name)]

    def _render_table(self, table: list[list[str | None]] | None) -> str:
        """Render a table into a lightweight markdown-like block."""

        if not table:
            return ""

        rows: list[str] = []
        for row in table:
            cells = [cell.strip() if cell else "" for cell in row]
            if any(cells):
                rows.append(" | ".join(cells))
        return "\n".join(rows).strip()

    def _iter_block_items(self, document: Document):
        """Yield paragraphs and tables in document order."""

        for child in document.element.body.iterchildren():
            if child.tag.endswith("}p"):
                yield Paragraph(child, document)
            elif child.tag.endswith("}tbl"):
                yield Table(child, document)
