"""Modular multi-provider LLM router and client abstraction package.

Provides hot-swappable inference and embedding support across local Ollama
(strictly <= 8B parameters), Groq Cloud, OpenAI, and Google Gemini with resilient
exponential backoff, provider fallback, and structured JSON repair.
"""

from __future__ import annotations

from legal_assistant.llm.base import (
    BaseEmbeddingClient,
    BaseLLMClient,
    LLMAllProvidersFailedError,
    LLMAuthenticationError,
    LLMConnectionError,
    LLMError,
    LLMProviderError,
    LLMRateLimitError,
    LLMResponse,
    LLMStructuredOutputError,
    LLMTimeoutError,
    ProviderConfig,
    TokenUsage,
)
from legal_assistant.llm.client import (
    GeminiClient,
    GroqClient,
    OllamaClient,
    OpenAIClient,
    OpenAICompatibleClient,
    OpenAICompatibleEmbeddingClient,
    validate_local_model_size,
)
from legal_assistant.llm.json_repair import (
    clean_markdown_fences,
    extract_outermost_json,
    extract_outermost_json_substring,
    fix_trailing_commas,
    parse_and_validate,
    repair_and_parse_json,
    repair_json_string,
)
from legal_assistant.llm.prompts import (
    CASE_BUILDER_SYSTEM_PROMPT,
    DRAFTER_SYSTEM_PROMPT,
    JSON_REPAIR_SYSTEM_PROMPT,
    LEGAL_ADVISOR_SYSTEM_PROMPT,
    SIMULATOR_SYSTEM_PROMPT,
    STATUTORY_GROUNDING_DIRECTIVE,
    STRUCTURED_JSON_DIRECTIVE,
    SYSTEM_PROMPT_CASE_BUILDER,
    SYSTEM_PROMPT_DOCUMENT_DRAFTER,
    SYSTEM_PROMPT_JSON_REPAIR,
    SYSTEM_PROMPT_LEGAL_STANDING,
    SYSTEM_PROMPT_OPPOSING_COUNSEL,
    format_case_builder_prompt,
    format_json_repair_prompt,
    format_legal_advisor_prompt,
)
from legal_assistant.llm.router import LLMRouter

__all__ = [
    # Base interfaces & exceptions
    "BaseLLMClient",
    "BaseEmbeddingClient",
    "LLMError",
    "LLMConnectionError",
    "LLMTimeoutError",
    "LLMRateLimitError",
    "LLMAuthenticationError",
    "LLMProviderError",
    "LLMStructuredOutputError",
    "LLMAllProvidersFailedError",
    "TokenUsage",
    "LLMResponse",
    "ProviderConfig",
    # Concrete clients
    "OpenAICompatibleClient",
    "GroqClient",
    "OllamaClient",
    "OpenAIClient",
    "GeminiClient",
    "OpenAICompatibleEmbeddingClient",
    "validate_local_model_size",
    # Router
    "LLMRouter",
    # JSON repair utilities
    "clean_markdown_fences",
    "extract_outermost_json",
    "extract_outermost_json_substring",
    "fix_trailing_commas",
    "repair_json_string",
    "repair_and_parse_json",
    "parse_and_validate",
    # Prompts & directives
    "STATUTORY_GROUNDING_DIRECTIVE",
    "STRUCTURED_JSON_DIRECTIVE",
    "SYSTEM_PROMPT_CASE_BUILDER",
    "SYSTEM_PROMPT_LEGAL_STANDING",
    "SYSTEM_PROMPT_DOCUMENT_DRAFTER",
    "SYSTEM_PROMPT_OPPOSING_COUNSEL",
    "SYSTEM_PROMPT_JSON_REPAIR",
    "CASE_BUILDER_SYSTEM_PROMPT",
    "LEGAL_ADVISOR_SYSTEM_PROMPT",
    "DRAFTER_SYSTEM_PROMPT",
    "SIMULATOR_SYSTEM_PROMPT",
    "JSON_REPAIR_SYSTEM_PROMPT",
    "format_case_builder_prompt",
    "format_legal_advisor_prompt",
    "format_json_repair_prompt",
]
