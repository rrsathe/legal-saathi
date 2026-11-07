"""Base interfaces, data transfer objects, and error taxonomy for LLM clients.

This module defines the abstract contracts for LLM text generation, structured
output parsing, and text embeddings across all supported inference providers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T", bound=BaseModel)


# ==============================================================================
# Error Taxonomy
# ==============================================================================


class LLMError(Exception):
    """Base exception for all LLM and embedding operations."""


class LLMConnectionError(LLMError):
    """Raised when connection to the inference provider cannot be established."""


class LLMTimeoutError(LLMError):
    """Raised when an inference request exceeds the configured timeout."""


class LLMRateLimitError(LLMError):
    """Raised when rate limits (HTTP 429) are exhausted."""

    def __init__(self, message: str, retry_after: float | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class LLMAuthenticationError(LLMError):
    """Raised on invalid or missing API credentials (HTTP 401/403)."""


class LLMProviderError(LLMError):
    """Raised on provider-side failures (HTTP 500, 502, 503, 504)."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class LLMStructuredOutputError(LLMError):
    """Raised when the LLM fails to produce JSON conforming to the requested schema."""


class LLMAllProvidersFailedError(LLMError):
    """Raised when all providers in a fallback chain fail."""


# ==============================================================================
# Telemetry & Response Schemas
# ==============================================================================


class TokenUsage(BaseModel):
    """Token consumption and latency telemetry for an LLM call."""

    model_config = ConfigDict(frozen=True)

    prompt_tokens: int = Field(default=0, ge=0, description="Tokens in input prompt")
    completion_tokens: int = Field(default=0, ge=0, description="Tokens generated in completion")
    total_tokens: int = Field(default=0, ge=0, description="Total tokens consumed")
    latency_ms: float = Field(
        default=0.0, ge=0.0, description="End-to-end request latency in milliseconds"
    )


class LLMResponse(BaseModel):
    """Standardized response container returned by all LLM clients."""

    model_config = ConfigDict(frozen=True)

    content: str = Field(..., description="Generated text content")
    provider: str = Field(..., description="Provider name that fulfilled the request")
    model: str = Field(..., description="Model identifier used for generation")
    usage: TokenUsage = Field(default_factory=TokenUsage, description="Usage and latency telemetry")
    raw_response: dict[str, Any] = Field(
        default_factory=dict, description="Raw provider response payload"
    )
    finish_reason: str | None = Field(default=None, description="Completion stop reason")


class ProviderConfig(BaseModel):
    """Connection parameters and operational limits for an LLM provider."""

    model_config = ConfigDict(frozen=True)

    provider: str = Field(..., description="Provider name: groq, ollama, openai, gemini")
    model: str = Field(..., description="Target model name")
    base_url: str = Field(..., description="Base REST endpoint URL")
    api_key: str | None = Field(default=None, description="Optional API authentication key")
    timeout: float = Field(default=30.0, gt=0.0, description="HTTP request timeout in seconds")
    max_retries: int = Field(
        default=3, ge=0, description="Maximum retry attempts on transient errors"
    )
    temperature: float = Field(default=0.0, ge=0.0, le=2.0, description="Sampling temperature")
    additional_headers: dict[str, str] = Field(
        default_factory=dict, description="Custom HTTP headers to include with requests"
    )


# ==============================================================================
# Abstract Client Interfaces
# ==============================================================================


class BaseLLMClient(ABC):
    """Abstract interface for LLM text generation and structured extraction."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate text from a prompt.

        Args:
            prompt: User prompt message.
            system_prompt: Optional system instruction prompt.
            temperature: Optional override for generation temperature.
            **kwargs: Additional provider-specific parameters.

        Returns:
            LLMResponse containing text, metadata, and token usage.

        Raises:
            LLMError: On execution failure.
        """

    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        schema: type[T],
        system_prompt: str = "",
        temperature: float | None = None,
        **kwargs: Any,
    ) -> T:
        """Generate structured data conforming to a Pydantic schema.

        Args:
            prompt: User prompt requesting specific data.
            schema: Pydantic model class defining target schema.
            system_prompt: Optional system instruction prompt.
            temperature: Optional override for generation temperature.
            **kwargs: Additional provider-specific parameters.

        Returns:
            Validated instance of the requested Pydantic model schema.

        Raises:
            LLMStructuredOutputError: If schema validation fails after repair.
            LLMError: On network or provider execution failure.
        """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return provider identifier name."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return model identifier name."""


class BaseEmbeddingClient(ABC):
    """Abstract interface for text embedding generation."""

    @abstractmethod
    def embed_query(self, query: str) -> list[float]:
        """Embed a single search query text.

        Args:
            query: Query string to embed.

        Returns:
            Vector embedding as list of floats.
        """

    @abstractmethod
    def embed_documents(self, documents: list[str]) -> list[list[float]]:
        """Embed a batch of document texts.

        Args:
            documents: List of text strings to embed.

        Returns:
            List of vector embeddings.
        """
