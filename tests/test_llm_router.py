"""Comprehensive offline unit tests for hot-swappable LLM Router and client suite.

Executes 100% offline with zero external API key requirements using httpx.MockTransport
and unittest.mock. Validates provider switching, exponential backoff, retry-after headers,
provider fallback, structured Pydantic extraction (including CaseFile), JSON repair,
statutory calculations, and token telemetry.
"""

from __future__ import annotations

import json
from datetime import date
from typing import Any
from unittest.mock import MagicMock, patch

import httpx
import pytest
from pydantic import BaseModel, Field, SecretStr

from legal_assistant.config import Settings, clear_settings_cache, get_settings
from legal_assistant.llm.base import (
    LLMAllProvidersFailedError,
    LLMAuthenticationError,
    LLMProviderError,
    LLMStructuredOutputError,
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
    fix_trailing_commas,
    parse_and_unwrap_dict,
    repair_and_parse_json,
    repair_json_string,
)
from legal_assistant.llm.router import LLMRouter
from legal_assistant.schemas import (
    CaseFile,
    PecuniaryForum,
    calculate_edaakhil_fee,
    check_limitation_status,
    determine_pecuniary_forum,
)

# ==============================================================================
# Test Data Models & Mock Helpers
# ==============================================================================


class SampleCitation(BaseModel):
    """Test schema for structured generation testing."""

    statute: str = Field(description="Name of statute")
    section: str = Field(description="Section identifier")
    title: str = Field(description="Statutory title")


def make_chat_response_json(
    content: str,
    prompt_tokens: int = 20,
    completion_tokens: int = 15,
    model: str = "test-model",
) -> dict[str, Any]:
    """Helper creating standard OpenAI-compatible chat completion JSON payload."""
    return {
        "id": "chatcmpl-mock-1",
        "object": "chat.completion",
        "created": 1700000000,
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content,
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
    }


def make_embedding_response_json(embeddings: list[list[float]]) -> dict[str, Any]:
    """Helper creating standard OpenAI-compatible embeddings JSON payload."""
    return {
        "object": "list",
        "data": [
            {"object": "embedding", "embedding": emb, "index": i}
            for i, emb in enumerate(embeddings)
        ],
        "model": "text-embedding-test",
        "usage": {"prompt_tokens": 10, "total_tokens": 10},
    }


# ==============================================================================
# Unit Tests: Configuration & Model Selection
# ==============================================================================


def test_settings_initialization_and_cache() -> None:
    """Verify Settings loads defaults and get_settings is cached singleton."""
    clear_settings_cache()
    settings = get_settings()
    assert settings.ollama_model == "llama3.1:8b"
    assert settings.groq_model == "llama-3.1-8b-instant"
    assert settings.llm_timeout_seconds == 30.0

    # Test cache singleton
    settings_2 = get_settings()
    assert settings is settings_2

    clear_settings_cache()


def test_settings_fallback_providers_parsing() -> None:
    """Verify fallback_providers parses comma-delimited string, JSON array, and list."""
    s1 = Settings(fallback_providers=["ollama", "groq"])
    assert s1.fallback_providers == ["ollama", "groq"]

    # String format
    s2 = Settings.model_validate({"fallback_providers": "ollama,openai,gemini"})
    assert s2.fallback_providers == ["ollama", "openai", "gemini"]

    # JSON array string format
    s3 = Settings.model_validate({"fallback_providers": '["groq", "ollama"]'})
    assert s3.fallback_providers == ["groq", "ollama"]


def test_settings_get_active_model_and_api_key() -> None:
    """Verify get_active_model and get_api_key resolution."""
    settings = Settings(
        groq_api_key=SecretStr("gsk_test_12345"),
        default_model_name="custom-override-model",
    )
    assert settings.get_api_key("groq") == "gsk_test_12345"
    assert settings.get_api_key("openai") is None
    assert settings.get_active_model("ollama") == "llama3.1:8b"
    assert settings.get_active_model() == "custom-override-model"


# ==============================================================================
# Unit Tests: Provider Selection & Model Guards
# ==============================================================================


def test_router_instantiation_default_provider() -> None:
    """Verify router instantiates configured default provider."""
    settings = Settings(llm_provider="groq")
    router = LLMRouter(settings=settings)
    client = router.get_client()
    assert isinstance(client, GroqClient)
    assert client.provider_name == "groq"


def test_router_explicit_provider_switching() -> None:
    """Verify hot-swapping across providers via explicit function arguments."""
    settings = Settings(llm_provider="groq")
    router = LLMRouter(settings=settings)

    ollama_client = router.get_client("ollama")
    assert isinstance(ollama_client, OllamaClient)
    assert ollama_client.provider_name == "ollama"

    openai_client = router.get_client("openai")
    assert isinstance(openai_client, OpenAIClient)
    assert openai_client.provider_name == "openai"

    gemini_client = router.get_client("gemini")
    assert isinstance(gemini_client, GeminiClient)
    assert gemini_client.provider_name == "gemini"

    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        router.get_client("non_existent_provider")


def test_ollama_local_model_size_guard() -> None:
    """Verify Ollama client strictly rejects models exceeding 8B parameters."""
    # Valid <= 8B models
    validate_local_model_size("llama3.1:8b")
    validate_local_model_size("qwen2.5:7b")
    validate_local_model_size("mistral:7b")

    client = OllamaClient(model="llama3.1:8b")
    assert client.model == "llama3.1:8b"

    # Models > 8B must raise ValueError
    with pytest.raises(ValueError, match="exceeds strictly enforced 8.0B parameter limit"):
        validate_local_model_size("llama3.1:70b")

    with pytest.raises(ValueError, match="exceeds strictly enforced 8.0B parameter limit"):
        OllamaClient(model="llama3.1:70b")

    with pytest.raises(ValueError, match="exceeds strictly enforced 8.0B parameter limit"):
        OllamaClient(model="mixtral:8x7b")


# ==============================================================================
# Unit Tests: Generation & Token Telemetry (Offline Mocks)
# ==============================================================================


def test_openai_compatible_generation_success() -> None:
    """Verify text generation and telemetry extraction using MockTransport."""
    expected_content = "Under Section 2(7) of CPA 2019, you are a verified consumer."

    def mock_handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/openai/v1/chat/completions"
        return httpx.Response(200, json=make_chat_response_json(expected_content, 50, 25))

    client = OpenAICompatibleClient(
        provider="groq",
        model="llama-3.1-8b-instant",
        base_url="https://api.groq.com/openai/v1",
        transport=httpx.MockTransport(mock_handler),
    )

    response = client.generate(
        prompt="Check my standing",
        system_prompt="You are a legal assistant.",
    )
    assert response.content == expected_content
    assert response.provider == "groq"
    assert response.usage.prompt_tokens == 50
    assert response.usage.completion_tokens == 25
    assert response.usage.total_tokens == 75
    assert response.usage.latency_ms >= 0.0


def test_authentication_error_no_retry() -> None:
    """Verify HTTP 401 raises LLMAuthenticationError immediately without retrying."""
    call_count = 0

    def mock_handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(401, json={"error": "Invalid API key"})

    client = OpenAICompatibleClient(
        provider="groq",
        model="llama-3.1-8b-instant",
        base_url="https://api.groq.com/openai/v1",
        max_retries=3,
        transport=httpx.MockTransport(mock_handler),
    )

    with pytest.raises(LLMAuthenticationError):
        client.generate(prompt="Hello")

    assert call_count == 1  # Proves no wasteful retries on auth failure


# ==============================================================================
# Unit Tests: Exponential Backoff & Retry
# ==============================================================================


@patch("time.sleep")
def test_retry_on_http_429_rate_limit(mock_sleep: MagicMock) -> None:
    """Verify exponential backoff retries transient 429 errors and succeeds."""
    call_count = 0

    def mock_handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            return httpx.Response(
                429,
                json={"error": {"message": "Rate limit reached"}},
                headers={"Retry-After": "2"},
            )
        return httpx.Response(200, json=make_chat_response_json("Success after retry"))

    client = OpenAICompatibleClient(
        provider="groq",
        model="llama-3.1-8b-instant",
        base_url="https://api.groq.com/openai/v1",
        max_retries=3,
        transport=httpx.MockTransport(mock_handler),
    )

    response = client.generate(prompt="Test retry")
    assert response.content == "Success after retry"
    assert call_count == 3
    assert mock_sleep.call_count == 2
    # First sleep should respect Retry-After header (2.0 seconds)
    assert mock_sleep.call_args_list[0][0][0] >= 2.0


@patch("time.sleep")
def test_retry_on_http_503_service_unavailable(mock_sleep: MagicMock) -> None:
    """Verify exponential backoff retries 503 errors."""
    call_count = 0

    def mock_handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return httpx.Response(503, json={"error": "Service Unavailable"})
        return httpx.Response(200, json=make_chat_response_json("Recovered from 503"))

    client = OpenAICompatibleClient(
        provider="groq",
        model="llama-3.1-8b-instant",
        base_url="https://api.groq.com/openai/v1",
        max_retries=2,
        transport=httpx.MockTransport(mock_handler),
    )

    response = client.generate(prompt="Test 503")
    assert response.content == "Recovered from 503"
    assert call_count == 2
    assert mock_sleep.call_count == 1


@patch("time.sleep")
def test_retry_exhaustion_raises_llm_error(mock_sleep: MagicMock) -> None:
    """Verify exceeding max_retries raises appropriate LLMProviderError."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "Permanent Internal Error"})

    client = OpenAICompatibleClient(
        provider="groq",
        model="llama-3.1-8b-instant",
        base_url="https://api.groq.com/openai/v1",
        max_retries=2,
        transport=httpx.MockTransport(mock_handler),
    )

    with pytest.raises(LLMProviderError) as exc_info:
        client.generate(prompt="Will fail")
    assert exc_info.value.status_code == 500


# ==============================================================================
# Unit Tests: Fallback Chain
# ==============================================================================


@patch("time.sleep")
def test_fallback_chain_primary_to_secondary_success(mock_sleep: MagicMock) -> None:
    """Verify router cascades to secondary provider when primary fails permanently."""
    settings = Settings(
        llm_provider="groq",
        fallback_providers=["ollama", "openai"],
    )

    groq_transport = httpx.MockTransport(lambda req: httpx.Response(500, json={"error": "Down"}))
    ollama_transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json=make_chat_response_json("Ollama fallback output"))
    )

    router = LLMRouter(settings=settings)
    router.register_transport("groq", groq_transport)
    router.register_transport("ollama", ollama_transport)

    response = router.generate_with_fallback(prompt="Analyze case")
    assert response.content == "Ollama fallback output"
    assert response.provider == "ollama"


@patch("time.sleep")
def test_fallback_chain_all_exhausted_raises_error(mock_sleep: MagicMock) -> None:
    """Verify router raises LLMAllProvidersFailedError when all providers fail."""
    settings = Settings(
        llm_provider="groq",
        fallback_providers=["ollama"],
    )

    failing_transport = httpx.MockTransport(lambda req: httpx.Response(500, json={"error": "Fail"}))

    router = LLMRouter(settings=settings)
    router.register_transport("groq", failing_transport)
    router.register_transport("ollama", failing_transport)

    with pytest.raises(LLMAllProvidersFailedError):
        router.generate_with_fallback(prompt="Analyze case")


# ==============================================================================
# Unit Tests: Structured Output & JSON Repair
# ==============================================================================


def test_structured_generation_clean_json() -> None:
    """Verify generate_structured parses clean conforming JSON."""
    raw_payload = json.dumps(
        {
            "statute": "Consumer Protection Act, 2019",
            "section": "Section 2(47)",
            "title": "Unfair Trade Practice",
        }
    )

    client = OpenAICompatibleClient(
        provider="groq",
        model="llama-3.1-8b-instant",
        base_url="https://api.groq.com/openai/v1",
        transport=httpx.MockTransport(
            lambda req: httpx.Response(200, json=make_chat_response_json(raw_payload))
        ),
    )

    result = client.generate_structured(prompt="Get citation", schema=SampleCitation)
    assert isinstance(result, SampleCitation)
    assert result.section == "Section 2(47)"
    assert result.title == "Unfair Trade Practice"


def test_structured_generation_fences_and_trailing_commas() -> None:
    """Verify JSON repair strips markdown fences and repairs trailing commas."""
    malformed_raw = """Here is the extracted citation in JSON format:
```json
{
  "statute": "Consumer Protection Act, 2019",
  "section": "Section 35",
  "title": "Manner of making complaint",
}
```
Let me know if you need anything else!"""

    client = OpenAICompatibleClient(
        provider="ollama",
        model="llama3.1:8b",
        base_url="http://localhost:11434/v1",
        transport=httpx.MockTransport(
            lambda req: httpx.Response(200, json=make_chat_response_json(malformed_raw))
        ),
    )

    result = client.generate_structured(prompt="Get citation", schema=SampleCitation)
    assert isinstance(result, SampleCitation)
    assert result.section == "Section 35"
    assert result.title == "Manner of making complaint"


def test_structured_generation_unwraps_envelope_key() -> None:
    """Verify parser unwraps single-key class envelope wrapper."""
    envelope_raw = json.dumps(
        {
            "SampleCitation": {
                "statute": "Consumer Protection (E-Commerce) Rules, 2020",
                "section": "Rule 4(5)",
                "title": "Grievance Redressal Mechanism",
            }
        }
    )

    client = OpenAICompatibleClient(
        provider="groq",
        model="llama-3.1-8b-instant",
        base_url="https://api.groq.com/openai/v1",
        transport=httpx.MockTransport(
            lambda req: httpx.Response(200, json=make_chat_response_json(envelope_raw))
        ),
    )

    result = client.generate_structured(prompt="Get rule", schema=SampleCitation)
    assert isinstance(result, SampleCitation)
    assert result.section == "Rule 4(5)"


def test_structured_generation_automated_repair_flow() -> None:
    """Verify generate_structured triggers repair prompt on initial failure and succeeds."""
    call_count = 0
    valid_citation_json = json.dumps(
        {
            "statute": "Consumer Protection Act, 2019",
            "section": "Section 2(7)",
            "title": "Definition of Consumer",
        }
    )

    def mock_handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            # First call returns invalid schema (missing required fields)
            return httpx.Response(
                200, json=make_chat_response_json('{"invalid_key": "some value"}')
            )
        # Second call (repair prompt) returns conforming JSON
        return httpx.Response(200, json=make_chat_response_json(valid_citation_json))

    client = OpenAICompatibleClient(
        provider="groq",
        model="llama-3.1-8b-instant",
        base_url="https://api.groq.com/openai/v1",
        transport=httpx.MockTransport(mock_handler),
    )

    result = client.generate_structured(prompt="Get consumer citation", schema=SampleCitation)
    assert isinstance(result, SampleCitation)
    assert result.section == "Section 2(7)"
    assert call_count == 2  # Proves repair prompt was dispatched


def test_structured_generation_case_file_schema() -> None:
    """Verify structured generation works end-to-end with CaseFile domain schema."""
    case_payload = {
        "title": "Flipkart Defective TV Dispute",
        "complainant": {
            "name": "Amit Patel",
            "email": "amit@example.com",
            "city": "Ahmedabad",
            "state": "Gujarat",
        },
        "opposite_parties": [
            {
                "name": "Flipkart Internet Pvt Ltd",
                "role": "E-Commerce Marketplace",
                "entity_type": "marketplace",
            }
        ],
        "transaction_date": "2024-03-10",
        "cause_of_action_date": "2024-03-20",
        "disputed_amount_inr": "₹ 42,999.00",
        "compensation_claimed_inr": "₹10,000",
        "facts_summary": "Delivered TV has shattered screen. Platform refused replacement.",
        "timeline": [
            {
                "date": "2024-03-10",
                "description": "Order delivered and unboxed",
                "significance": "Date of delivery",
            }
        ],
        "evidence_checklist": [
            {
                "item_name": "Tax Invoice",
                "category": "documentary",
                "is_available": True,
                "description": "Invoice showing payment of 42999",
            }
        ],
        "tags": ["e-commerce", "defective_goods"],
    }

    client = OpenAICompatibleClient(
        provider="groq",
        model="llama-3.1-8b-instant",
        base_url="https://api.groq.com/openai/v1",
        transport=httpx.MockTransport(
            lambda req: httpx.Response(200, json=make_chat_response_json(json.dumps(case_payload)))
        ),
    )

    case = client.generate_structured(prompt="Parse intake", schema=CaseFile)
    assert isinstance(case, CaseFile)
    assert case.complainant.name == "Amit Patel"
    assert case.disputed_amount_inr == 42999.0
    assert case.compensation_claimed_inr == 10000.0
    assert len(case.opposite_parties) == 1
    assert case.opposite_parties[0].name == "Flipkart Internet Pvt Ltd"


def test_structured_generation_unrecoverable_failure_raises() -> None:
    """Verify unrecoverable JSON failure raises LLMStructuredOutputError."""
    client = OpenAICompatibleClient(
        provider="groq",
        model="llama-3.1-8b-instant",
        base_url="https://api.groq.com/openai/v1",
        transport=httpx.MockTransport(
            lambda req: httpx.Response(
                200, json=make_chat_response_json("Not a JSON document at all.")
            )
        ),
    )

    with pytest.raises(LLMStructuredOutputError):
        client.generate_structured(prompt="Get citation", schema=SampleCitation)


# ==============================================================================
# Unit Tests: JSON Repair Utility Functions
# ==============================================================================


def test_json_repair_helpers() -> None:
    """Verify string repair utilities handle diverse malformations."""
    # Fences
    assert clean_markdown_fences("```json\n{'a': 1}\n```") == "{'a': 1}"
    assert clean_markdown_fences("```\n{'a': 1}\n```") == "{'a': 1}"
    assert clean_markdown_fences("Plain text") == "Plain text"

    # Outermost JSON
    assert extract_outermost_json('Note: {"k": "v"} done') == '{"k": "v"}'
    assert extract_outermost_json("List: [1, 2] done") == "[1, 2]"

    # Trailing commas
    assert fix_trailing_commas('{"a": 1,}') == '{"a": 1}'
    assert fix_trailing_commas('{"a": [1, 2,],}') == '{"a": [1, 2]}'

    # Full repair string
    malformed = 'Here is JSON:\n```json\n{"statute": "CPA", "section": "Sec 2",}\n```\nThanks'
    repaired = repair_json_string(malformed)
    assert repaired == '{"statute": "CPA", "section": "Sec 2"}'

    # Repair and parse
    parsed = repair_and_parse_json(malformed)
    assert parsed["statute"] == "CPA"
    assert parsed["section"] == "Sec 2"


# ==============================================================================
# Unit Tests: Embedding Client
# ==============================================================================


def test_openai_compatible_embedding_client() -> None:
    """Verify embedding client batches document embeddings and embeds queries."""
    sample_vectors = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]

    def mock_embed_handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/embeddings"
        return httpx.Response(200, json=make_embedding_response_json(sample_vectors))

    client = OpenAICompatibleEmbeddingClient(
        base_url="http://localhost:11434/v1",
        model="nomic-embed-text",
        transport=httpx.MockTransport(mock_embed_handler),
    )

    docs = ["First document", "Second document"]
    embeddings = client.embed_documents(docs)
    assert len(embeddings) == 2
    assert embeddings[0] == [0.1, 0.2, 0.3]
    assert embeddings[1] == [0.4, 0.5, 0.6]

    single_emb = client.embed_query("Search query")
    assert single_emb == [0.1, 0.2, 0.3]

    assert client.embed_documents([]) == []


# ==============================================================================
# Unit Tests: Statutory Calculations (Pecuniary, Court Fees, Limitation)
# ==============================================================================


def test_pecuniary_forum_determination_2021_rules() -> None:
    """Verify 2021 Pecuniary Rules strictly enforced on consideration paid."""
    # District Commission: <= 50 Lakhs (5,000,000)
    forum_d1, rationale_d1 = determine_pecuniary_forum(84_990.0)
    assert forum_d1 == PecuniaryForum.DISTRICT_COMMISSION.value
    assert "District Consumer Disputes Redressal Commission" in rationale_d1
    assert "Rule 3" in rationale_d1

    forum_d2, _ = determine_pecuniary_forum(5_000_000.0)
    assert forum_d2 == PecuniaryForum.DISTRICT_COMMISSION.value

    # State Commission: > 50 Lakhs and <= 2 Crores (20,000,000)
    forum_s1, rationale_s1 = determine_pecuniary_forum(5_000_001.0)
    assert forum_s1 == PecuniaryForum.STATE_COMMISSION.value
    assert "Rule 4" in rationale_s1

    forum_s2, _ = determine_pecuniary_forum(20_000_000.0)
    assert forum_s2 == PecuniaryForum.STATE_COMMISSION.value

    # National Commission: > 2 Crores
    forum_n, rationale_n = determine_pecuniary_forum(25_000_000.0)
    assert forum_n == PecuniaryForum.NATIONAL_COMMISSION.value
    assert "Rule 5" in rationale_n


def test_edaakhil_court_fee_slabs() -> None:
    """Verify e-Daakhil official fee slabs from ₹0 up to ₹7,500."""
    assert calculate_edaakhil_fee(10_000.0) == 0
    assert calculate_edaakhil_fee(500_000.0) == 0
    assert calculate_edaakhil_fee(750_000.0) == 200
    assert calculate_edaakhil_fee(1_500_000.0) == 400
    assert calculate_edaakhil_fee(3_500_000.0) == 1000
    assert calculate_edaakhil_fee(7_500_000.0) == 2000
    assert calculate_edaakhil_fee(15_000_000.0) == 2500
    assert calculate_edaakhil_fee(30_000_000.0) == 3000
    assert calculate_edaakhil_fee(50_000_000.0) == 4000
    assert calculate_edaakhil_fee(70_000_000.0) == 5000
    assert calculate_edaakhil_fee(90_000_000.0) == 6000
    assert calculate_edaakhil_fee(150_000_000.0) == 7500


def test_section_69_limitation_status() -> None:
    """Verify Section 69 CPA 2019 2-year (730 days) limitation period calculations."""
    # Case 1: Elapsed days passed as integer (well within limitation)
    is_within_1, remaining_1, rationale_1 = check_limitation_status(120)
    assert is_within_1 is True
    assert remaining_1 == 610
    assert "well within" in rationale_1

    # Case 2: Approaching deadline (650 days)
    is_within_2, remaining_2, rationale_2 = check_limitation_status(650)
    assert is_within_2 is True
    assert remaining_2 == 80
    assert "URGENT" in rationale_2

    # Case 3: Barred by limitation (> 730 days)
    is_within_3, remaining_3, rationale_3 = check_limitation_status(800)
    assert is_within_3 is False
    assert remaining_3 == -70
    assert "condonation" in rationale_3

    # Case 4: Dates passed as ISO string
    is_within_4, remaining_4, _ = check_limitation_status(
        cause_of_action_date="2024-01-01",
        filing_date="2024-04-10",
    )
    assert is_within_4 is True
    assert remaining_4 == 730 - 100

    # Case 5: Dates passed as date objects
    is_within_5, remaining_5, _ = check_limitation_status(
        cause_of_action_date=date(2021, 1, 1),
        filing_date=date(2024, 1, 1),
    )
    assert is_within_5 is False
    assert remaining_5 < 0


def test_parse_and_unwrap_dict_non_dict_raises_value_error() -> None:
    """Verify parse_and_unwrap_dict raises ValueError when payload is not a JSON dict."""
    with pytest.raises(ValueError, match="Expected JSON object"):
        parse_and_unwrap_dict("[1, 2, 3]", SampleCitation)

    with pytest.raises(ValueError, match="Expected JSON object"):
        parse_and_unwrap_dict('"raw string"', SampleCitation)

    with pytest.raises(ValueError, match="Expected JSON object"):
        parse_and_unwrap_dict("123", SampleCitation)


def test_extract_outermost_json_strict_delimiter_pairing() -> None:
    """Verify extract_outermost_json strictly pairs matching delimiters without cross-trapping."""
    assert extract_outermost_json('Here is { "a": 1 } and a closing bracket ]') == '{ "a": 1 }'
    assert extract_outermost_json('Here is { "a": 1 } [Note: filed in 2024]') == '{ "a": 1 }'
    assert extract_outermost_json("Result: [1, 2, 3] {end note}") == "[1, 2, 3]"
    assert extract_outermost_json('[ {"a": 1}, {"b": 2} ]') == '[ {"a": 1}, {"b": 2} ]'
    assert extract_outermost_json('{ "items": [1, 2, 3] }') == '{ "items": [1, 2, 3] }'


def test_case_file_inr_amount_sanitization() -> None:
    """Verify CaseFile sanitizes diverse Indian currency formats cleanly."""
    valid_data: dict[str, Any] = {
        "title": "INR Sanitization Test",
        "complainant": {"name": "Test User", "city": "Delhi"},
        "opposite_parties": [{"name": "Merchant", "role": "Seller"}],
        "transaction_date": "2024-01-15",
        "facts_summary": "Dispute details",
    }

    # Test INR prefix, commas, and trailing /-
    payload1: dict[str, Any] = {
        **valid_data,
        "disputed_amount_inr": "INR 45,000",
        "compensation_claimed_inr": "45,000/-",
    }
    case1 = CaseFile.model_validate(payload1)
    assert case1.disputed_amount_inr == 45000.0
    assert case1.compensation_claimed_inr == 45000.0

    # Test lowercase inr, Rs. prefix, and /- suffix
    payload2: dict[str, Any] = {
        **valid_data,
        "disputed_amount_inr": "inr 1,25,000/-",
        "compensation_claimed_inr": "Rs. 25,000",
    }
    case2 = CaseFile.model_validate(payload2)
    assert case2.disputed_amount_inr == 125000.0
    assert case2.compensation_claimed_inr == 25000.0

    # Test rupee symbol and invalid non-numeric string fallback
    payload3: dict[str, Any] = {
        **valid_data,
        "disputed_amount_inr": "₹ 84,990.50",
        "compensation_claimed_inr": "N/A - Free Gift",
    }
    case3 = CaseFile.model_validate(payload3)
    assert case3.disputed_amount_inr == 84990.50
    assert case3.compensation_claimed_inr == 0.0
