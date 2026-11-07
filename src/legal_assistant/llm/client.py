"""Unified HTTPX-based OpenAI-compatible LLM and Embedding clients.

Provides zero-lock-in hot-swappable client implementations for Groq Cloud,
Local Ollama (<=8B parameters), Universal OpenAI, and Gemini.
"""

from __future__ import annotations

import json
import logging
import random
import re
import time
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from legal_assistant.llm.base import (
    BaseEmbeddingClient,
    BaseLLMClient,
    LLMAuthenticationError,
    LLMConnectionError,
    LLMProviderError,
    LLMRateLimitError,
    LLMResponse,
    LLMStructuredOutputError,
    LLMTimeoutError,
    ProviderConfig,
    TokenUsage,
)
from legal_assistant.llm.json_repair import parse_and_validate
from legal_assistant.llm.prompts import (
    SYSTEM_PROMPT_JSON_REPAIR,
    format_json_repair_prompt,
)

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)

RETRYABLE_STATUS_CODES: frozenset[int] = frozenset({429, 500, 502, 503, 504})


def validate_local_model_size(model_name: str, max_billions: float = 8.0) -> None:
    """Validate that a local model does not exceed the strictly enforced parameter limit.

    Args:
        model_name: Ollama model tag (e.g. 'llama3.1:8b', 'mistral:7b', 'llama3.1:70b').
        max_billions: Maximum allowed parameters in billions (default: 8.0).

    Raises:
        ValueError: If model parameter size strictly exceeds max_billions.
    """
    lower = model_name.lower()

    # Check MoE pattern first, e.g. 8x7b -> 56B
    moe_match = re.search(r"(\d+)x(\d+(?:\.\d+)?)b\b", lower)
    if moe_match:
        total_size = float(moe_match.group(1)) * float(moe_match.group(2))
        if total_size > max_billions:
            raise ValueError(
                f"Local Ollama model '{model_name}' exceeds strictly enforced {max_billions}B "
                f"parameter limit ({total_size}B > {max_billions}B). "
                f"For models > 8B, use cloud providers like Groq or OpenAI."
            )
        return

    # Standard pattern e.g. 8b, 70b
    match = re.search(r"(\d+(?:\.\d+)?)b\b", lower)
    if match:
        size = float(match.group(1))
        if size > max_billions:
            raise ValueError(
                f"Local Ollama model '{model_name}' exceeds strictly enforced {max_billions}B "
                f"parameter limit ({size}B > {max_billions}B). "
                f"For models > 8B, use cloud providers like Groq or OpenAI."
            )


class OpenAICompatibleClient(BaseLLMClient):
    """High-performance OpenAI-compatible REST client using httpx."""

    def __init__(
        self,
        config: ProviderConfig | None = None,
        *,
        provider: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        temperature: float = 0.0,
        additional_headers: dict[str, str] | None = None,
        http_client: httpx.Client | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        """Initialize client with provider configuration or explicit parameters.

        Args:
            config: Provider configuration parameters.
            provider: Provider name (groq, ollama, openai, gemini).
            model: Target model name.
            base_url: Base REST endpoint URL.
            api_key: Optional API key.
            timeout: HTTP timeout in seconds.
            max_retries: Maximum retry attempts on transient errors.
            temperature: Sampling temperature.
            additional_headers: Extra headers dictionary.
            http_client: Optional pre-configured httpx.Client.
            transport: Optional httpx.BaseTransport (e.g. MockTransport for testing).
        """
        if config is not None:
            self.config = config
        else:
            self.config = ProviderConfig(
                provider=provider or "openai",
                model=model or "default",
                base_url=base_url or "http://localhost:11434/v1",
                api_key=api_key,
                timeout=timeout,
                max_retries=max_retries,
                temperature=temperature,
                additional_headers=additional_headers or {},
            )

        self._transport = transport
        self._custom_client: httpx.Client | None
        if http_client is not None:
            self._custom_client = http_client
        elif transport is not None:
            self._custom_client = httpx.Client(transport=transport, timeout=self.config.timeout)
        else:
            self._custom_client = None

    @property
    def provider_name(self) -> str:
        """Return provider identifier name."""
        return self.config.provider

    @property
    def model_name(self) -> str:
        """Return model identifier name."""
        return self.config.model

    @property
    def model(self) -> str:
        """Convenience alias for model identifier name."""
        return self.config.model

    @property
    def base_url(self) -> str:
        """Convenience alias for base endpoint URL."""
        return self.config.base_url

    def _get_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            **self.config.additional_headers,
        }
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return headers

    def _calculate_backoff(self, attempt: int, retry_after: float | None = None) -> float:
        """Calculate exponential backoff with full jitter.

        Args:
            attempt: Current retry attempt number (0-indexed).
            retry_after: Optional explicit delay from Retry-After header.

        Returns:
            Backoff delay in seconds.
        """
        if retry_after is not None and retry_after > 0:
            return retry_after + random.uniform(0.1, 0.5)

        base_backoff = 1.0
        max_backoff = 16.0
        calculated = min(max_backoff, base_backoff * (2.0**attempt))
        return random.uniform(0.1, calculated)

    def _execute_with_retry(
        self,
        url: str,
        payload: dict[str, Any],
    ) -> tuple[dict[str, Any], float]:
        """Execute HTTP request with full jitter exponential backoff.

        Args:
            url: Target endpoint URL.
            payload: JSON request body.

        Returns:
            Tuple of (parsed_json_response, latency_ms).

        Raises:
            LLMError: If request fails after exhausting retries.
        """
        headers = self._get_headers()
        timeout = httpx.Timeout(
            connect=10.0,
            read=self.config.timeout,
            write=10.0,
            pool=10.0,
        )

        client = (
            self._custom_client
            if self._custom_client is not None
            else httpx.Client(timeout=timeout)
        )
        should_close = self._custom_client is None

        attempt = 0
        max_retries = self.config.max_retries

        try:
            while True:
                start_time = time.perf_counter()
                try:
                    response = client.post(url, headers=headers, json=payload)
                    latency_ms = (time.perf_counter() - start_time) * 1000.0

                    if response.status_code == 200:
                        return response.json(), latency_ms

                    status = response.status_code
                    if status in (401, 403):
                        raise LLMAuthenticationError(
                            f"Authentication failed for {self.config.provider} "
                            f"(HTTP {status}): {response.text}"
                        )
                    if status in (400, 404, 422):
                        raise LLMProviderError(
                            f"Client error from {self.config.provider} "
                            f"(HTTP {status}): {response.text}",
                            status_code=status,
                        )

                    if status in RETRYABLE_STATUS_CODES:
                        retry_after_header = response.headers.get("retry-after")
                        retry_after = (
                            float(retry_after_header)
                            if retry_after_header and retry_after_header.isdigit()
                            else None
                        )

                        if attempt >= max_retries:
                            if status == 429:
                                raise LLMRateLimitError(
                                    f"Rate limit exceeded on {self.config.provider} "
                                    f"after {max_retries} retries",
                                    retry_after=retry_after,
                                )
                            raise LLMProviderError(
                                f"Provider {self.config.provider} failed with "
                                f"HTTP {status}: {response.text}",
                                status_code=status,
                            )

                        sleep_time = self._calculate_backoff(attempt, retry_after)
                        logger.warning(
                            "Transient HTTP %s from %s. Retrying in %.2fs (attempt %s/%s)...",
                            status,
                            self.config.provider,
                            sleep_time,
                            attempt + 1,
                            max_retries,
                        )
                        time.sleep(sleep_time)
                        attempt += 1
                        continue

                    response.raise_for_status()

                except httpx.TimeoutException as exc:
                    if attempt >= max_retries:
                        raise LLMTimeoutError(
                            f"Request to {self.config.provider} timed out after "
                            f"{self.config.timeout}s (attempt {attempt + 1}/{max_retries + 1})"
                        ) from exc
                    sleep_time = self._calculate_backoff(attempt)
                    logger.warning(
                        "Timeout from %s. Retrying in %.2fs...", self.config.provider, sleep_time
                    )
                    time.sleep(sleep_time)
                    attempt += 1

                except httpx.RequestError as exc:
                    if attempt >= max_retries:
                        raise LLMConnectionError(
                            f"Network error connecting to {self.config.provider}: {exc}"
                        ) from exc
                    sleep_time = self._calculate_backoff(attempt)
                    logger.warning(
                        "Connection error from %s. Retrying in %.2fs...",
                        self.config.provider,
                        sleep_time,
                    )
                    time.sleep(sleep_time)
                    attempt += 1

        finally:
            if should_close:
                client.close()

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate text completion from OpenAI-compatible endpoint.

        Args:
            prompt: User prompt message.
            system_prompt: Optional system instruction prompt.
            temperature: Optional override for generation temperature.
            **kwargs: Additional provider-specific parameters.

        Returns:
            LLMResponse containing text, metadata, and token usage.
        """
        url = f"{self.config.base_url.rstrip('/')}/chat/completions"
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature if temperature is None else temperature,
            **kwargs,
        }

        data, latency_ms = self._execute_with_retry(url, payload)

        choices = data.get("choices", [])
        if not choices:
            raise LLMProviderError(f"Provider {self.config.provider} returned empty choices array")

        message = choices[0].get("message", {})
        content = message.get("content", "")
        finish_reason = choices[0].get("finish_reason")

        usage_data = data.get("usage", {})
        prompt_tokens = usage_data.get("prompt_tokens", 0)
        completion_tokens = usage_data.get("completion_tokens", 0)
        total_tokens = usage_data.get("total_tokens", prompt_tokens + completion_tokens)

        usage = TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
        )

        return LLMResponse(
            content=content,
            provider=self.config.provider,
            model=self.config.model,
            usage=usage,
            raw_response=data,
            finish_reason=finish_reason,
        )

    def generate_structured(
        self,
        prompt: str,
        schema: type[T],
        system_prompt: str = "",
        temperature: float | None = None,
        **kwargs: Any,
    ) -> T:
        """Generate and validate structured JSON output matching a Pydantic schema.

        Includes automatic 1-attempt repair loop on malformed JSON or validation failure.

        Args:
            prompt: User prompt requesting specific data.
            schema: Pydantic model class defining target schema.
            system_prompt: Optional system instruction prompt.
            temperature: Optional override for generation temperature.
            **kwargs: Additional provider-specific parameters.

        Returns:
            Validated instance of model schema T.

        Raises:
            LLMStructuredOutputError: If model fails to produce conforming JSON after repair.
        """
        schema_json = json.dumps(schema.model_json_schema(), indent=2)
        format_instruction = (
            "\n\nCRITICAL INSTRUCTION: You MUST output ONLY a valid JSON object "
            "matching this schema:\n"
            f"```json\n{schema_json}\n```\n"
            "Do not include any prose, markdown text, or explanations outside the JSON object."
        )

        effective_system = (
            (system_prompt + format_instruction) if system_prompt else format_instruction
        )

        response = self.generate(
            prompt=prompt,
            system_prompt=effective_system,
            temperature=temperature,
            response_format={"type": "json_object"},
            **kwargs,
        )

        raw_output = response.content

        try:
            return parse_and_validate(raw_output, schema)
        except (ValidationError, json.JSONDecodeError, ValueError) as initial_error:
            logger.warning(
                "Initial structured parse failed on %s: %s. Initiating repair prompt...",
                self.config.provider,
                initial_error,
            )

            # Automated 1-turn repair prompt
            repair_user_prompt = format_json_repair_prompt(
                raw_output=raw_output,
                error_message=str(initial_error),
                schema=schema,
            )

            try:
                repair_response = self.generate(
                    prompt=repair_user_prompt,
                    system_prompt=SYSTEM_PROMPT_JSON_REPAIR,
                    temperature=0.0,
                    response_format={"type": "json_object"},
                )
                return parse_and_validate(repair_response.content, schema)
            except Exception as repair_error:
                raise LLMStructuredOutputError(
                    f"Failed to produce structured output conforming to {schema.__name__} "
                    f"on provider '{self.config.provider}' after automated repair.\n"
                    f"Initial error: {initial_error}\n"
                    f"Repair error: {repair_error}\n"
                    f"Raw response was:\n{raw_output}"
                ) from repair_error


class GroqClient(OpenAICompatibleClient):
    """Client for Groq Cloud ultra-low-latency LPU inference."""

    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.1-8b-instant",
        timeout: float = 30.0,
        max_retries: int = 3,
        http_client: httpx.Client | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        config = ProviderConfig(
            provider="groq",
            model=model,
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
        )
        super().__init__(config=config, http_client=http_client, transport=transport)


class OllamaClient(OpenAICompatibleClient):
    """Client for Local Ollama inference (strictly <= 8B parameters)."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3.1:8b",
        timeout: float = 30.0,
        max_retries: int = 3,
        http_client: httpx.Client | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        validate_local_model_size(model)
        clean_base = base_url.rstrip("/")
        endpoint_base = clean_base if clean_base.endswith("/v1") else f"{clean_base}/v1"
        config = ProviderConfig(
            provider="ollama",
            model=model,
            base_url=endpoint_base,
            api_key=None,
            timeout=timeout,
            max_retries=max_retries,
        )
        super().__init__(config=config, http_client=http_client, transport=transport)


class OpenAIClient(OpenAICompatibleClient):
    """Client for OpenAI Cloud inference."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        timeout: float = 30.0,
        max_retries: int = 3,
        http_client: httpx.Client | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        config = ProviderConfig(
            provider="openai",
            model=model,
            base_url="https://api.openai.com/v1",
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
        )
        super().__init__(config=config, http_client=http_client, transport=transport)


class GeminiClient(OpenAICompatibleClient):
    """Client for Google Gemini via OpenAI-compatible endpoint."""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-1.5-flash",
        timeout: float = 30.0,
        max_retries: int = 3,
        http_client: httpx.Client | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        config = ProviderConfig(
            provider="gemini",
            model=model,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai",
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
        )
        super().__init__(config=config, http_client=http_client, transport=transport)


class OpenAICompatibleEmbeddingClient(BaseEmbeddingClient):
    """Universal embedding client supporting Ollama (/v1/embeddings), OpenAI, and Gemini."""

    def __init__(
        self,
        base_url: str,
        model: str = "nomic-embed-text",
        api_key: str | None = None,
        timeout: float = 30.0,
        http_client: httpx.Client | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        clean_base = base_url.rstrip("/")
        self.base_url = clean_base if clean_base.endswith("/v1") else f"{clean_base}/v1"
        self.model = model
        self.api_key = api_key
        self.timeout = timeout
        self._custom_client: httpx.Client | None
        if http_client is not None:
            self._custom_client = http_client
        elif transport is not None:
            self._custom_client = httpx.Client(transport=transport, timeout=timeout)
        else:
            self._custom_client = None

    def embed_documents(self, documents: list[str]) -> list[list[float]]:
        """Embed a batch of document texts."""
        if not documents:
            return []

        url = f"{self.base_url}/embeddings"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        client = (
            self._custom_client
            if self._custom_client is not None
            else httpx.Client(timeout=self.timeout)
        )
        should_close = self._custom_client is None

        try:
            response = client.post(
                url,
                headers=headers,
                json={"model": self.model, "input": documents},
            )
            response.raise_for_status()
            data = response.json()
            items = data.get("data", [])
            items_sorted = sorted(items, key=lambda x: x.get("index", 0))
            return [item["embedding"] for item in items_sorted]
        finally:
            if should_close:
                client.close()

    def embed_query(self, query: str) -> list[float]:
        """Embed a single search query text."""
        results = self.embed_documents([query])
        return results[0] if results else []
