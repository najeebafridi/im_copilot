"""Local embedding service used for retrieval and Chroma storage."""

from __future__ import annotations

from collections import Counter
import hashlib
import math
import re
import threading
from typing import ClassVar, Sequence

try:  # pragma: no cover - optional dependency is resolved at runtime
    from sentence_transformers import SentenceTransformer
except ImportError:  # pragma: no cover - fallback keeps the backend usable
    SentenceTransformer = None  # type: ignore[assignment]


class LocalHashEmbeddingService:
    """A deterministic local embedding service with a reusable sentence model."""

    DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    LEGACY_MODEL_ALIASES = {
        "": DEFAULT_MODEL_NAME,
        "local-hash-embedding": DEFAULT_MODEL_NAME,
        "test-local-embedding": DEFAULT_MODEL_NAME,
    }

    _model_cache: ClassVar[dict[str, SentenceTransformer]] = {}
    _model_lock: ClassVar[threading.Lock] = threading.Lock()

    def __init__(self, model_name: str, dimension: int = 256) -> None:
        self.model_name = self._resolve_model_name(model_name)
        self.dimension = dimension
        self._model = self._load_model(self.model_name)

    def embed_text(self, text: str) -> list[float]:
        """Embed a single string as a normalized vector."""

        if self._model is not None:
            return self._encode([text])[0]
        return self._hash_embed(text)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple strings in a single batch when possible."""

        if not texts:
            return []

        if self._model is not None:
            return self._encode(texts)
        return [self._hash_embed(text) for text in texts]

    @classmethod
    def _resolve_model_name(cls, model_name: str) -> str:
        """Resolve legacy aliases to the production sentence-transformer model."""

        normalized = model_name.strip()
        return cls.LEGACY_MODEL_ALIASES.get(normalized.lower(), normalized or cls.DEFAULT_MODEL_NAME)

    @classmethod
    def _load_model(cls, model_name: str) -> SentenceTransformer | None:
        """Load the singleton sentence-transformer model if available."""

        if SentenceTransformer is None:
            return None

        with cls._model_lock:
            cached = cls._model_cache.get(model_name)
            if cached is not None:
                return cached

            try:
                model = SentenceTransformer(model_name, device="cpu")
                model.eval()
            except Exception:  # pragma: no cover - fallback path protects local runs
                return None

            cls._model_cache[model_name] = model
            return model

    def _encode(self, texts: Sequence[str]) -> list[list[float]]:
        """Encode one or many texts with normalized embeddings."""

        assert self._model is not None
        batch_size = max(1, min(32, len(texts)))
        embeddings = self._model.encode(
            list(texts),
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return [embedding.tolist() for embedding in embeddings]

    def _hash_embed(self, text: str) -> list[float]:
        """Fallback deterministic embedding for environments without the model."""

        vector = [0.0] * self.dimension
        tokens = re.findall(r"[a-z0-9]+", text.lower())
        counts = Counter(tokens)
        for token, count in counts.items():
            index = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16) % self.dimension
            vector[index] += float(count)

        norm = math.sqrt(sum(value * value for value in vector))
        if norm:
            vector = [value / norm for value in vector]
        return vector
