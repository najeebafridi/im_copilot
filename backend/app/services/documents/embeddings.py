"""Local embedding service used for retrieval and Chroma storage."""

from __future__ import annotations

from collections import Counter
import hashlib
import math
import re


class LocalHashEmbeddingService:
    """A deterministic, replaceable embedding service."""

    def __init__(self, model_name: str, dimension: int = 256) -> None:
        self.model_name = model_name
        self.dimension = dimension

    def embed_text(self, text: str) -> list[float]:
        """Embed a single string as a normalized hashed vector."""

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

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple strings."""

        return [self.embed_text(text) for text in texts]

