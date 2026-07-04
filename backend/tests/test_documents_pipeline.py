"""Tests for the Phase 3 document pipeline."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.services.documents.chunking import Chunker
from app.services.documents.loader import DocumentLoader
from app.services.documents.pipeline import DocumentPipelineService
from app.services.documents.retrieval import RetrievalService
from app.services.documents.structure import StructureDetector
from app.services.documents.types import ExtractedPage


def _create_docx(path: Path, text: str) -> None:
    """Create a tiny DOCX document for testing."""

    document = Document()
    for paragraph in text.split("\n"):
        document.add_paragraph(paragraph)
    document.save(path)


def _create_pdf(path: Path, text: str) -> None:
    """Create a tiny PDF document for testing."""

    pdf = canvas.Canvas(str(path), pagesize=letter)
    y = 760
    for line in text.split("\n"):
        pdf.drawString(72, y, line)
        y -= 18
    pdf.save()


@pytest.mark.parametrize("filename", ["sample.txt", "sample.md", "sample.docx", "sample.pdf"])
def test_document_loader_supports_all_formats(tmp_path: Path, filename: str) -> None:
    """The loader should read all supported document formats."""

    sample_text = "CHAPTER 1\n1.1 Attendance Requirement\nStudents must attend 75% of classes."
    path = tmp_path / filename
    if path.suffix == ".docx":
        _create_docx(path, sample_text)
    elif path.suffix == ".pdf":
        _create_pdf(path, sample_text)
    else:
        path.write_text(sample_text, encoding="utf-8")

    loaded = DocumentLoader().load(path)

    assert loaded.document_type == path.suffix.lstrip(".")
    assert loaded.pages
    assert "Attendance Requirement" in loaded.pages[0].text


def test_structure_detection_and_chunk_metadata() -> None:
    """Structure detection and chunking should preserve headings and metadata."""

    pages = [
        ExtractedPage(
            page=1,
            source_file="rules.txt",
            text=(
                "CHAPTER 1\n"
                "1.1 Attendance Policy\n"
                "Students must attend 75 percent of classes.\n"
                "1.1.1 Special Cases\n"
                "Medical leaves must be approved.\n"
            ),
        )
    ]
    sections = StructureDetector().detect(pages, source_file="rules.txt", document_type="txt")
    chunks = Chunker(chunk_size=10, chunk_overlap=2).chunk_sections(sections)

    assert sections
    assert sections[0].chapter == "CHAPTER 1"
    assert chunks
    metadata = chunks[0].to_metadata()
    assert metadata["chunk_id"]
    assert metadata["source_file"] == "rules.txt"
    assert metadata["document_type"] == "txt"
    assert metadata["page_start"] == 1
    assert metadata["page_end"] == 1
    assert metadata["chapter"] == "CHAPTER 1"


def test_ingestion_and_retrieval_pipeline(tmp_path: Path) -> None:
    """Ingestion should create artifacts, store chunks, and support retrieval."""

    documents_dir = tmp_path / "documents"
    processed_dir = tmp_path / "processed"
    chroma_dir = tmp_path / "chroma"
    documents_dir.mkdir()

    (documents_dir / "student_handbook.md").write_text(
        "\n".join(
            [
                "CHAPTER 1",
                "1.1 Attendance Requirement",
                "Students must attend at least 75% of classes to pass.",
                "1.1.1 Medical Leave",
                "Medical leave requires supporting documents.",
            ]
        ),
        encoding="utf-8",
    )

    service = DocumentPipelineService(
        documents_path=str(documents_dir),
        processed_path=str(processed_dir),
        chroma_path=str(chroma_dir),
        embedding_model="test-local-embedding",
        chunk_size=12,
        chunk_overlap=3,
    )
    result = service.ingest_all_documents()

    assert result["documents_processed"] == 1
    assert result["chunks_created"] >= 1
    assert (processed_dir / "extracted_pages.json").exists()
    assert (processed_dir / "structured_sections.json").exists()
    assert (processed_dir / "chunks.json").exists()

    chunks = json.loads((processed_dir / "chunks.json").read_text(encoding="utf-8"))
    assert chunks
    assert chunks[0]["chunk_id"]
    assert chunks[0]["source_file"] == "student_handbook.md"

    retrieval = RetrievalService(chroma_path=str(chroma_dir), embedding_model="test-local-embedding")
    results = retrieval.search(query="attendance requirement", k=3)

    assert results
    assert "metadata" in results[0]
    assert results[0]["metadata"]["source_file"] == "student_handbook.md"
