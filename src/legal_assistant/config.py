"""Configuration module for Legal Saathi AI Consumer Lawyer.

Loads and validates application settings from environment variables and `.env`
files using `pydantic-settings` v2 with strict UTF-8 support and Windows portability.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from pydantic import AliasChoices, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

LLMProviderType = Literal["ollama", "groq", "openai", "gemini"]


class Settings(BaseSettings):
    """Application settings for Legal Saathi.

    Loads configuration parameters from environment variables and `.env` files.
    Supports local Ollama inference (<=8B params) and cloud API endpoints (Groq,
    OpenAI, Gemini), as well as RAG indexing and hybrid search parameters.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # -------------------------------------------------------------------------
    # LLM Provider & Model Selection
    # -------------------------------------------------------------------------
    llm_provider: LLMProviderType = Field(
        default="groq",
        validation_alias=AliasChoices("llm_provider", "default_llm_provider"),
        description="Active primary LLM inference provider (groq, ollama, openai, gemini)",
    )
    default_model_name: str | None = Field(
        default=None,
        description="Global model name override if set in .env",
    )

    # Local Ollama Inference (strictly <= 8B parameter models for local mode)
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Base HTTP URL for local Ollama server instance",
    )
    ollama_model: str = Field(
        default="llama3.1:8b",
        description="Model identifier for Ollama inference (strictly <=8B limit)",
    )
    ollama_embed_model: str = Field(
        default="nomic-embed-text",
        description="Embedding model identifier for local Ollama embeddings",
    )

    # Groq Cloud API (Ultra-low latency inference)
    groq_api_key: SecretStr = Field(
        default=SecretStr(""),
        description="API key for Groq Cloud inference",
    )
    groq_model: str = Field(
        default="llama-3.1-8b-instant",
        description="Default model identifier for Groq Cloud",
    )

    # OpenAI API
    openai_api_key: SecretStr = Field(
        default=SecretStr(""),
        description="API key for OpenAI inference",
    )
    openai_model: str = Field(
        default="gpt-4o-mini",
        description="Default model identifier for OpenAI",
    )

    # Google Gemini API
    gemini_api_key: SecretStr = Field(
        default=SecretStr(""),
        description="API key for Google Gemini inference",
    )
    gemini_model: str = Field(
        default="gemini-1.5-flash",
        description="Default model identifier for Google Gemini",
    )

    # Fallback Chain & Execution Control
    fallback_providers: list[str] = Field(
        default_factory=lambda: ["ollama", "openai", "gemini"],
        description="Ordered list of fallback providers if primary provider fails",
    )
    llm_timeout_seconds: float = Field(
        default=30.0,
        ge=1.0,
        le=300.0,
        description="HTTP request timeout in seconds for LLM endpoints",
    )
    llm_max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retry attempts on transient network or rate limit errors",
    )
    llm_temperature: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        description="Sampling temperature (0.0 for deterministic legal analysis)",
    )

    # -------------------------------------------------------------------------
    # RAG & Indexing Parameters
    # -------------------------------------------------------------------------
    embedding_provider: str = Field(
        default="ollama",
        description="Embedding provider name (ollama, sentence-transformers, in_memory)",
    )
    embedding_model: str = Field(
        default="nomic-embed-text",
        description="Model name for statutory text embeddings",
    )
    vector_db_path: Path = Field(
        default=Path("data/index/chroma"),
        description="Filesystem path for persistent vector database storage",
    )
    bm25_index_path: Path = Field(
        default=Path("data/index/bm25.pkl"),
        description="Filesystem path for serialized BM25 Okapi index",
    )
    chunk_size: int = Field(
        default=500,
        ge=100,
        le=4000,
        description="Target character size for statutory chunking",
    )
    chunk_overlap: int = Field(
        default=50,
        ge=0,
        le=500,
        description="Character overlap between adjacent statutory chunks",
    )
    top_k_retrieval: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Number of top statutory chunks returned by hybrid search",
    )

    # -------------------------------------------------------------------------
    # Windows & Runtime Portability
    # -------------------------------------------------------------------------
    pythonutf8: int = Field(
        default=1,
        description="Native Windows UTF-8 environment enforcement flag",
    )

    @field_validator("llm_provider", mode="before")
    @classmethod
    def normalize_provider(cls, value: Any) -> Any:
        """Normalize provider string to lowercase stripped value.

        Args:
            value: Input provider name.

        Returns:
            Normalized lowercase provider name.
        """
        if isinstance(value, str):
            return value.strip().lower()
        return value

    @field_validator("fallback_providers", mode="before")
    @classmethod
    def parse_fallback_providers(cls, value: Any) -> list[str]:
        """Parse fallback providers from comma-delimited string, JSON array, or list.

        Args:
            value: Raw input from environment or constructor.

        Returns:
            List of normalized lowercase provider names.
        """
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("[") and value.endswith("]"):
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        return [str(x).strip().lower() for x in parsed if str(x).strip()]
                except json.JSONDecodeError:
                    pass
            return [x.strip().lower() for x in value.split(",") if x.strip()]
        if isinstance(value, list):
            return [str(x).strip().lower() for x in value if str(x).strip()]
        return []

    def get_active_model(self, provider: str | None = None) -> str:
        """Get the model identifier for the specified or active provider.

        Args:
            provider: Target provider name. If None, uses active `llm_provider`.

        Returns:
            The configured model identifier string.
        """
        target = (provider or self.llm_provider).lower()

        # If user explicitly defined a default_model_name and provider matches primary
        if self.default_model_name and (provider is None or target == self.llm_provider):
            return self.default_model_name

        match target:
            case "ollama":
                return self.ollama_model
            case "groq":
                return self.groq_model
            case "openai":
                return self.openai_model
            case "gemini":
                return self.gemini_model
            case _:
                return self.ollama_model

    def get_api_key(self, provider: str) -> str | None:
        """Retrieve plain-text API key for a cloud provider.

        Args:
            provider: Provider name (e.g. 'groq', 'openai', 'gemini').

        Returns:
            API key string if set and non-empty, otherwise None.
        """
        target = provider.lower()
        secret: SecretStr | None = getattr(self, f"{target}_api_key", None)
        if secret is None:
            return None
        val = secret.get_secret_value()
        return val if val.strip() else None

    def is_local_provider(self, provider: str | None = None) -> bool:
        """Check whether the given or active provider runs locally.

        Args:
            provider: Provider name to check. If None, checks active provider.

        Returns:
            True if provider is local (e.g. ollama), False for cloud APIs.
        """
        target = (provider or self.llm_provider).lower()
        return target == "ollama"

    def get_base_url(self, provider: str | None = None) -> str | None:
        """Get the HTTP base URL for the given provider.

        Args:
            provider: Provider name. If None, uses active provider.

        Returns:
            Base URL string or None if default SDK endpoint applies.
        """
        target = (provider or self.llm_provider).lower()
        match target:
            case "ollama":
                return self.ollama_base_url.rstrip("/")
            case "groq":
                return "https://api.groq.com/openai/v1"
            case "gemini":
                return "https://generativelanguage.googleapis.com/v1beta/openai"
            case _:
                return None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached singleton instance of application settings.

    Returns:
        Settings: The validated application configuration instance.
    """
    return Settings()


def clear_settings_cache() -> None:
    """Clear cached settings instance to allow re-reading environment variables."""
    get_settings.cache_clear()
