"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the application."""

    PROJECT_NAME: str = "IM Copilot"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./im_copilot.db"
    JWT_SECRET_KEY: str = "change-this-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DOCUMENTS_PATH: str = "documents"
    CHROMA_PATH: str = "data/chroma"
    EMBEDDING_MODEL: str = "local-hash-embedding"
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 120
    COPILOT_TOP_K: int = 5
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = ""
    LLM_PROVIDER: str = ""
    LLM_MODEL: str = ""
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 256
    MOCK_LLM: bool = True
    ENABLE_CACHE: bool = True
    CACHE_SIZE: int = 100
    ROUTER_DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()
