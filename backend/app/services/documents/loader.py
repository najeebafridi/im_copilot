"""Document loaders for supported file types."""

from __future__ import annotations

from pathlib import Path

import pdfplumber
from docx import Document

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
                text = page.extract_text(layout=True) or ""
                tables = page.extract_tables() or []
                table_text: list[str] = []
                for table in tables:
                    rows = []
                    for row in table:
                        cells = [cell.strip() if cell else "" for cell in row]
                        rows.append(" | ".join(cells))
                    if rows:
                        table_text.append("\n".join(rows))

                combined = "\n".join(part for part in [text, *table_text] if part).strip()
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
        for paragraph in document.paragraphs:
            if paragraph.text.strip():
                parts.append(paragraph.text)

        for table in document.tables:
            for row in table.rows:
                cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if cells:
                    parts.append(" | ".join(cells))

        text = clean_page_text("\n".join(parts))
        return [ExtractedPage(page=1, text=text, source_file=path.name)]

    def _load_text(self, path: Path) -> list[ExtractedPage]:
        """Extract text or markdown as a single page."""

        text = clean_page_text(path.read_text(encoding="utf-8", errors="ignore"))
        return [ExtractedPage(page=1, text=text, source_file=path.name)]

