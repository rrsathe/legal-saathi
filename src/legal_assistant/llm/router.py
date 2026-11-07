"""Hot-swappable Multi-Provider LLM Router with automatic fallback chain.

Enables zero-lock-in switching between Local Ollama, Groq Cloud, OpenAI,
and Gemini, providing resilient fallback on transient errors and exhaustion.
"""

from __future__ import annotations

import logging
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel

from legal_assistant.config import Settings, get_settings
from legal_assistant.llm.base import (
    BaseEmbeddingClient,
    BaseLLMClient,
    LLMAllProvidersFailedError,
    LLMError,
    LLMResponse,
)
from legal_assistant.llm.client import (
    GeminiClient,
    GroqClient,
    OllamaClient,
    OpenAIClient,
    OpenAICompatibleEmbeddingClient,
)

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class LLMRouter:
    """Central router managing LLM clients and resilient multi-provider fallback."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize router with application settings.

        Args:
            settings: Optional explicit settings instance. Defaults to get_settings().
        """
        self.settings = settings or get_settings()
        self._clients: dict[str, BaseLLMClient] = {}
        self._embedding_clients: dict[str, BaseEmbeddingClient] = {}
        self._transports: dict[str, httpx.BaseTransport] = {}

    def register_transport(self, provider: str, transport: httpx.BaseTransport) -> None:
        """Register a custom HTTP transport (e.g. MockTransport) for a provider.

        Args:
            provider: Provider name (e.g. 'groq', 'ollama').
            transport: Custom httpx.BaseTransport instance.
        """
        p = provider.lower()
        self._transports[p] = transport
        # Invalidate any cached client for this provider to ensure transport is bound
        self._clients.pop(p, None)

    def register_client(self, provider: str, client: BaseLLMClient) -> None:
        """Register a pre-constructed or mocked LLM client for a provider.

        Args:
            provider: Provider name.
            client: BaseLLMClient instance.
        """
        self._clients[provider.lower()] = client

    def get_client(self, provider: str | None = None) -> BaseLLMClient:
        """Get cached or new client instance for requested provider.

        Args:
            provider: Provider name ('groq', 'ollama', 'openai', 'gemini').
                If None, uses settings.llm_provider.

        Returns:
            BaseLLMClient instance.

        Raises:
            ValueError: If provider is unknown.
        """
        target = (provider or self.settings.llm_provider).lower()
        if target in self._clients:
            return self._clients[target]

        transport = self._transports.get(target)

        client: BaseLLMClient
        if target == "groq":
            client = GroqClient(
                api_key=self.settings.get_api_key("groq") or "",
                model=self.settings.get_active_model("groq"),
                timeout=self.settings.llm_timeout_seconds,
                max_retries=self.settings.llm_max_retries,
                transport=transport,
            )
        elif target == "ollama":
            client = OllamaClient(
                base_url=self.settings.ollama_base_url,
                model=self.settings.get_active_model("ollama"),
                timeout=self.settings.llm_timeout_seconds,
                max_retries=self.settings.llm_max_retries,
                transport=transport,
            )
        elif target == "openai":
            client = OpenAIClient(
                api_key=self.settings.get_api_key("openai") or "",
                model=self.settings.get_active_model("openai"),
                timeout=self.settings.llm_timeout_seconds,
                max_retries=self.settings.llm_max_retries,
                transport=transport,
            )
        elif target == "gemini":
            client = GeminiClient(
                api_key=self.settings.get_api_key("gemini") or "",
                model=self.settings.get_active_model("gemini"),
                timeout=self.settings.llm_timeout_seconds,
                max_retries=self.settings.llm_max_retries,
                transport=transport,
            )
        else:
            raise ValueError(
                f"Unsupported LLM provider: '{target}'. Supported: groq, ollama, openai, gemini"
            )

        self._clients[target] = client
        return client

    def get_embedding_client(self, provider: str | None = None) -> BaseEmbeddingClient:
        """Get cached or new embedding client for requested provider.

        Args:
            provider: Provider name ('ollama', 'openai', 'gemini').

        Returns:
            BaseEmbeddingClient instance.

        Raises:
            ValueError: If provider is unknown.
        """
        target = (provider or self.settings.embedding_provider).lower()
        if target in self._embedding_clients:
            return self._embedding_clients[target]

        transport = self._transports.get(target)
        emb_client: BaseEmbeddingClient

        if target == "ollama":
            emb_client = OpenAICompatibleEmbeddingClient(
                base_url=self.settings.ollama_base_url,
                model=self.settings.embedding_model,
                api_key=None,
                transport=transport,
            )
        elif target == "openai":
            emb_client = OpenAICompatibleEmbeddingClient(
                base_url="https://api.openai.com/v1",
                model="text-embedding-3-small",
                api_key=self.settings.get_api_key("openai"),
                transport=transport,
            )
        elif target == "gemini":
            emb_client = OpenAICompatibleEmbeddingClient(
                base_url="https://generativelanguage.googleapis.com/v1beta/openai",
                model="text-embedding-004",
                api_key=self.settings.get_api_key("gemini"),
                transport=transport,
            )
        else:
            raise ValueError(f"Unsupported embedding provider: '{target}'")

        self._embedding_clients[target] = emb_client
        return emb_client

    def is_provider_configured(self, provider: str) -> bool:
        """Check if provider has necessary configuration/credentials.

        Args:
            provider: Provider name.

        Returns:
            True if provider can be invoked, False if credentials missing.
        """
        p = provider.lower()
        # If a mock transport was explicitly registered for testing, treat as configured
        if p in self._transports or p in self._clients:
            return True
        if p == "groq":
            return bool(self.settings.get_api_key("groq"))
        if p == "ollama":
            return True  # Local daemon does not require an API key
        if p == "openai":
            return bool(self.settings.get_api_key("openai"))
        if p == "gemini":
            return bool(self.settings.get_api_key("gemini"))
        return False

    def generate(
        self,
        prompt: str,
        provider: str | None = None,
        system_prompt: str = "",
        temperature: float | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate text using specified or default provider without fallback."""
        client = self.get_client(provider)
        return client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            **kwargs,
        )

    def generate_structured(
        self,
        prompt: str,
        schema: type[T],
        provider: str | None = None,
        system_prompt: str = "",
        temperature: float | None = None,
        **kwargs: Any,
    ) -> T:
        """Generate structured data using specified or default provider without fallback."""
        client = self.get_client(provider)
        return client.generate_structured(
            prompt=prompt,
            schema=schema,
            system_prompt=system_prompt,
            temperature=temperature,
            **kwargs,
        )

    def generate_with_fallback(
        self,
        prompt: str,
        system_prompt: str = "",
        provider_order: list[str] | None = None,
        temperature: float | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Execute generation with automatic multi-provider fallback.

        Args:
            prompt: User prompt.
            system_prompt: System prompt.
            provider_order: Optional sequence of providers to try.
                Defaults to settings.fallback_providers.
            temperature: Generation temperature.
            **kwargs: Extra parameters passed to clients.

        Returns:
            LLMResponse from the first provider that succeeds.

        Raises:
            LLMAllProvidersFailedError: If all providers in fallback chain fail.
        """
        chain = provider_order or [
            self.settings.llm_provider,
            *self.settings.fallback_providers,
        ]
        # Remove duplicates while preserving order
        seen: set[str] = set()
        deduped_chain: list[str] = []
        for prov in chain:
            p = prov.lower()
            if p not in seen:
                seen.add(p)
                deduped_chain.append(p)

        errors: dict[str, str] = {}

        for prov in deduped_chain:
            if not self.is_provider_configured(prov):
                logger.debug("Skipping unconfigured provider: %s", prov)
                continue

            try:
                client = self.get_client(prov)
                response = client.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    **kwargs,
                )
                logger.info(
                    "Generation succeeded using provider '%s' (model '%s')", prov, client.model_name
                )
                return response
            except (LLMError, ValueError) as exc:
                logger.warning("Provider '%s' failed: %s. Advancing fallback...", prov, exc)
                errors[prov] = str(exc)

        raise LLMAllProvidersFailedError(f"All configured providers failed: {errors}")

    def generate_structured_with_fallback(
        self,
        prompt: str,
        schema: type[T],
        system_prompt: str = "",
        provider_order: list[str] | None = None,
        temperature: float | None = None,
        **kwargs: Any,
    ) -> T:
        """Execute structured generation with automatic multi-provider fallback."""
        chain = provider_order or [
            self.settings.llm_provider,
            *self.settings.fallback_providers,
        ]
        seen: set[str] = set()
        deduped_chain: list[str] = []
        for prov in chain:
            p = prov.lower()
            if p not in seen:
                seen.add(p)
                deduped_chain.append(p)

        errors: dict[str, str] = {}

        for prov in deduped_chain:
            if not self.is_provider_configured(prov):
                logger.debug("Skipping unconfigured provider: %s", prov)
                continue

            try:
                client = self.get_client(prov)
                result = client.generate_structured(
                    prompt=prompt,
                    schema=schema,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    **kwargs,
                )
                logger.info("Structured generation succeeded using provider '%s'", prov)
                return result
            except (LLMError, ValueError) as exc:
                logger.warning(
                    "Structured generation failed on '%s': %s. Advancing fallback...", prov, exc
                )
                errors[prov] = str(exc)

        raise LLMAllProvidersFailedError(
            f"All configured providers failed structured generation: {errors}"
        )
