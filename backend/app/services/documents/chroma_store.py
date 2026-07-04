"""Persistent Chroma storage for document chunks."""

from __future__ import annotations

from pathlib import Path

import chromadb

from app.services.documents.embeddings import LocalHashEmbeddingService
from app.services.documents.types import ChunkRecord


class ChromaStore:
    """Persist and query chunks in ChromaDB."""

    def __init__(self, chroma_path: str, embedding_service: LocalHashEmbeddingService) -> None:
        self.path = Path(chroma_path)
        self.path.mkdir(parents=True, exist_ok=True)
        self.embedding_service = embedding_service
        self.client = chromadb.PersistentClient(path=str(self.path))
        self.collection = self.client.get_or_create_collection(
            name="im_copilot_documents",
            metadata={"hnsw:space": "cosine"},
        )

    def upsert_chunks(self, chunks: list[ChunkRecord]) -> None:
        """Insert or update chunk records in Chroma."""

        if not chunks:
            return

        ids = [chunk.chunk_id for chunk in chunks]
        documents = [chunk.text for chunk in chunks]
        metadatas = [chunk.to_metadata() for chunk in chunks]
        embeddings = self.embedding_service.embed_texts(documents)
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    def query(self, query: str, k: int) -> list[dict[str, object]]:
        """Search the collection and return result dictionaries."""

        query_embedding = self.embedding_service.embed_text(query)
        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )

        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        items: list[dict[str, object]] = []
        for document, metadata, distance in zip(documents, metadatas, distances, strict=False):
            items.append(
                {
                    "text": document,
                    "metadata": metadata,
                    "distance": distance,
                }
            )
        return items

