"""In-memory cache for repeated LLM requests."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from threading import Lock
from typing import Tuple

from app.schemas.llm import ChatResponse

CacheKey = tuple[str, str, str]


@dataclass(slots=True)
class CachedChatResponse:
    """Cached response payload."""

    response: str
    model: str
    provider: str

    def to_schema(self) -> ChatResponse:
        """Convert the cached value to the public response schema."""

        return ChatResponse(response=self.response, model=self.model, provider=self.provider)


class LLMResponseCache:
    """Small thread-safe LRU cache."""

    def __init__(self, enabled: bool = True, max_size: int = 100) -> None:
        """Create a cache with a fixed maximum size."""

        self.enabled = enabled
        self.max_size = max_size
        self._store: OrderedDict[CacheKey, CachedChatResponse] = OrderedDict()
        self._lock = Lock()

    def get(self, key: CacheKey) -> CachedChatResponse | None:
        """Fetch a cached response, if present."""

        if not self.enabled:
            return None

        with self._lock:
            value = self._store.get(key)
            if value is None:
                return None
            self._store.move_to_end(key)
            return value

    def set(self, key: CacheKey, value: CachedChatResponse) -> None:
        """Store a response and evict the least recently used item if needed."""

        if not self.enabled:
            return

        with self._lock:
            self._store[key] = value
            self._store.move_to_end(key)
            while len(self._store) > self.max_size:
                self._store.popitem(last=False)

    def clear(self) -> None:
        """Remove all cached items."""

        with self._lock:
            self._store.clear()


_GLOBAL_CACHE: LLMResponseCache | None = None
_GLOBAL_CONFIG: tuple[bool, int] | None = None


def get_response_cache(enabled: bool, max_size: int) -> LLMResponseCache:
    """Return a shared cache instance configured from settings."""

    global _GLOBAL_CACHE, _GLOBAL_CONFIG
    config = (enabled, max_size)
    if _GLOBAL_CACHE is None or _GLOBAL_CONFIG != config:
        _GLOBAL_CACHE = LLMResponseCache(enabled=enabled, max_size=max_size)
        _GLOBAL_CONFIG = config
    return _GLOBAL_CACHE
