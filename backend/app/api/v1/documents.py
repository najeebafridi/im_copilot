"""Document ingestion endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.documents import IngestResponse
from app.services.documents.pipeline import DocumentPipelineService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/ingest", response_model=IngestResponse)
def ingest_documents() -> IngestResponse:
    """Process every supported document in the configured documents directory."""

    service = DocumentPipelineService()
    result = service.ingest_all_documents()
    return IngestResponse(**result)

