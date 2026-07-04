"""Reusable document ingestion pipeline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.services.documents.chunking import Chunker
from app.services.documents.chroma_store import ChromaStore
from app.services.documents.cleaning import clean_page_text
from app.services.documents.embeddings import LocalHashEmbeddingService
from app.services.documents.loader import DocumentLoader
from app.services.documents.structure import StructureDetector
from app.services.documents.types import ChunkRecord, ExtractedPage, StructuredSection
from app.services.documents.utils import is_supported_document


class DocumentPipelineService:
    """Load, clean, structure, chunk, embed, and store documents."""

    def __init__(
        self,
        documents_path: str | None = None,
        processed_path: str | None = None,
        chroma_path: str | None = None,
        embedding_model: str | None = None,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> None:
        settings = get_settings()
        self.documents_dir = Path(documents_path or settings.DOCUMENTS_PATH)
        self.processed_dir = Path(processed_path or "processed")
        self.documents_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        self.loader = DocumentLoader()
        self.detector = StructureDetector()
        self.chunker = Chunker(chunk_size or settings.CHUNK_SIZE, chunk_overlap or settings.CHUNK_OVERLAP)
        self.embedding_service = LocalHashEmbeddingService(embedding_model or settings.EMBEDDING_MODEL)
        self.store = ChromaStore(chroma_path or settings.CHROMA_PATH, self.embedding_service)

    def ingest_all_documents(self) -> dict[str, int]:
        """Process every supported document in the configured directory."""

        documents = sorted(
            path for path in self.documents_dir.rglob("*") if path.is_file() and is_supported_document(path)
        )
        print(f"[INGEST] Found {len(documents)} document(s) in {self.documents_dir}")

        extracted_pages: list[dict[str, Any]] = []
        structured_sections: list[dict[str, Any]] = []
        chunks: list[dict[str, Any]] = []

        documents_processed = 0
        chunks_created = 0

        for document_path in documents:
            print(f"[INGEST] Processing {document_path.name}")
            loaded_document = self.loader.load(document_path)
            cleaned_pages = [
                ExtractedPage(page=page.page, text=clean_page_text(page.text), source_file=page.source_file)
                for page in loaded_document.pages
            ]
            documents_processed += 1
            extracted_pages.extend(page.to_dict() for page in cleaned_pages)

            sections = self.detector.detect(
                cleaned_pages,
                source_file=document_path.name,
                document_type=loaded_document.document_type,
            )
            structured_sections.extend(section.to_dict() for section in sections)
            print(f"[INGEST] Detected {len(sections)} section(s) in {document_path.name}")

            section_chunks = self.chunker.chunk_sections(sections)
            chunks.extend(chunk.to_dict() for chunk in section_chunks)
            chunks_created += len(section_chunks)
            print(f"[INGEST] Created {len(section_chunks)} chunk(s) for {document_path.name}")

            self.store.upsert_chunks(section_chunks)
            print(f"[INGEST] Stored {len(section_chunks)} chunk(s) in Chroma")

        self._write_json("extracted_pages.json", extracted_pages)
        self._write_json("structured_sections.json", structured_sections)
        self._write_json("chunks.json", chunks)

        print(
            f"[INGEST] Completed: documents_processed={documents_processed}, chunks_created={chunks_created}"
        )
        return {
            "documents_processed": documents_processed,
            "chunks_created": chunks_created,
        }

    def _write_json(self, filename: str, data: list[dict[str, Any]]) -> None:
        """Write debug output to the processed directory."""

        output_path = self.processed_dir / filename
        output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[INGEST] Wrote {output_path}")

