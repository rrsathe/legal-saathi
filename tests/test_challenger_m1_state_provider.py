"""Empirical Stress Tests: Session State Robustness, Retriever Caching & Provider Switching.

Challenger 2 (State & Provider Stress Challenger) verification suite for Milestone 1.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from pydantic import SecretStr
from streamlit.testing.v1 import AppTest

from legal_assistant.config import Settings
from legal_assistant.llm.base import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMRateLimitError,
    LLMResponse,
)
from legal_assistant.llm.router import LLMRouter
from legal_assistant.rag.hybrid_retriever import StatutoryHybridRetriever
from legal_assistant.schemas import CaseFile, LegalStanding
from legal_assistant.ui.app import (
    apply_runtime_provider,
    get_cached_retriever,
    ping_provider,
)
from legal_assistant.workflows.simulator import DefenseTacticType
from tests.test_ui import MockLLMClient

APP_FILE = str(
    Path(__file__).resolve().parent.parent / "src" / "legal_assistant" / "ui" / "app.py"
)


class FailingMockLLMClient(MockLLMClient):
    """Mock client engineered to raise specific LLM exceptions on demand."""

    def __init__(self, failure_mode: str, provider_name: str = "groq") -> None:
        super().__init__(provider_name=provider_name, model_name="mock-model")
        self.failure_mode = failure_mode

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        if self.failure_mode == "auth":
            raise LLMAuthenticationError(
                f"Invalid credentials for {self.provider_name} (HTTP 401)"
            )
        if self.failure_mode == "connection":
            raise LLMConnectionError(
                f"Connection failed for {self.provider_name} (HTTP 503)"
            )
        if self.failure_mode == "ratelimit":
            raise LLMRateLimitError(
                f"Rate limit exceeded for {self.provider_name} (HTTP 429)"
            )
        if self.failure_mode == "unexpected":
            raise RuntimeError("Fatal socket transport drop")
        return LLMResponse(
            content="PONG",
            model=self.model_name,
            provider=self.provider_name,
        )


@pytest.fixture
def mock_router() -> LLMRouter:
    settings = Settings(
        llm_provider="groq",
        groq_api_key=SecretStr("mock-groq-key"),
        groq_model="llama-3.1-8b-instant",
    )
    router = LLMRouter(settings=settings)
    router.register_client(
        "groq", MockLLMClient(provider_name="groq", model_name="llama-3.1-8b-instant")
    )
    router.register_client(
        "ollama", MockLLMClient(provider_name="ollama", model_name="llama3.2:3b")
    )
    router.register_client(
        "openai", MockLLMClient(provider_name="openai", model_name="gpt-4o-mini")
    )
    router.register_client(
        "gemini", MockLLMClient(provider_name="gemini", model_name="gemini-1.5-flash")
    )
    return router


# ==============================================================================
# 1. EMPIRICAL TEST: Retriever Caching & Avoidance of Redundant Re-Indexing
# ==============================================================================
def test_retriever_caching_singleton_and_no_redundant_disk_reads() -> None:
    """Verify that get_cached_retriever caches instance and avoids re-reading corpus."""
    retriever_1 = get_cached_retriever()
    assert isinstance(retriever_1, StatutoryHybridRetriever)
    assert len(retriever_1.indexed_chunks) > 0

    retriever_2 = get_cached_retriever()
    assert retriever_1 is retriever_2, "get_cached_retriever failed to return cached singleton!"

    # Verify subsequent calls do not invoke Path.read_text
    with patch.object(Path, "read_text", side_effect=RuntimeError("Corpus re-read attempted!")):
        retriever_3 = get_cached_retriever()
        assert retriever_3 is retriever_1


def test_retriever_caching_across_independent_apptest_sessions(mock_router: LLMRouter) -> None:
    """Verify that multiple independent Streamlit sessions share the cached retriever."""
    at1 = AppTest.from_file(APP_FILE)
    at1.session_state["router"] = mock_router
    at1.run(timeout=30)
    assert len(at1.exception) == 0
    retriever_session_1 = at1.session_state.get("retriever")

    at2 = AppTest.from_file(APP_FILE)
    at2.session_state["router"] = mock_router
    at2.run(timeout=30)
    assert len(at2.exception) == 0
    retriever_session_2 = at2.session_state.get("retriever")

    assert retriever_session_1 is not None
    assert retriever_session_2 is not None
    assert retriever_session_1 is retriever_session_2, (
        "Independent AppTest sessions created distinct retriever instances!"
    )


# ==============================================================================
# 2. EMPIRICAL TEST: ping_provider Error Handling & Robustness
# ==============================================================================
def test_ping_provider_operational_success(mock_router: LLMRouter) -> None:
    """Verify ping_provider returns success badge and latency when provider responds."""
    res = ping_provider("groq", mock_router)
    assert "✅" in res
    assert "operational" in res
    assert "Latency:" in res
    assert "ms" in res


def test_ping_provider_authentication_error() -> None:
    """Verify ping_provider cleanly reports authentication failure without uncaught exception."""
    router = LLMRouter()
    client = FailingMockLLMClient(failure_mode="auth", provider_name="groq")
    router.register_client("groq", client)
    res = ping_provider("groq", router)
    assert "❌" in res
    assert "Connection failed" in res
    assert "401" in res or "Invalid credentials" in res


def test_ping_provider_connection_error() -> None:
    """Verify ping_provider cleanly reports network connection drop without crash."""
    router = LLMRouter()
    client = FailingMockLLMClient(failure_mode="connection", provider_name="ollama")
    router.register_client("ollama", client)
    res = ping_provider("ollama", router)
    assert "❌" in res
    assert "Connection failed" in res
    assert "Connection failed" in res


def test_ping_provider_rate_limit_error() -> None:
    """Verify ping_provider cleanly reports 429 rate limit errors without crash."""
    router = LLMRouter()
    client = FailingMockLLMClient(failure_mode="ratelimit", provider_name="openai")
    router.register_client("openai", client)
    res = ping_provider("openai", router)
    assert "❌" in res
    assert "Connection failed" in res
    assert "Rate limit exceeded" in res


def test_ping_provider_unexpected_runtime_error() -> None:
    """Verify ping_provider cleanly catches arbitrary unexpected exceptions."""
    router = LLMRouter()
    client = FailingMockLLMClient(failure_mode="unexpected", provider_name="gemini")
    router.register_client("gemini", client)
    res = ping_provider("gemini", router)
    assert "❌" in res
    assert "Unexpected error" in res
    assert "Fatal socket transport drop" in res


def test_ping_provider_unknown_provider_string() -> None:
    """Verify ping_provider handles unconfigured/unknown provider strings safely."""
    router = LLMRouter()
    res = ping_provider("nonexistent_cloud_llm", router)
    assert "❌" in res
    assert "nonexistent_cloud_llm" in res


# ==============================================================================
# 3. EMPIRICAL TEST: apply_runtime_provider Robustness & Edge Cases
# ==============================================================================
def test_apply_runtime_provider_valid_switch_and_cache_eviction() -> None:
    """Verify switching to supported provider clears router client cache and updates settings."""
    settings = Settings(llm_provider="groq")
    router = LLMRouter(settings=settings)
    mock_client = MockLLMClient(provider_name="ollama", model_name="llama3.2:3b")
    router.register_client("ollama", mock_client)
    assert "ollama" in router._clients

    msg = apply_runtime_provider(
        provider="ollama",
        model_name="llama3.2:1b",
        base_url="http://localhost:11434",
        settings=settings,
        router=router,
    )
    assert "Active provider successfully switched to: ollama" in msg
    assert settings.llm_provider == "ollama"
    assert settings.ollama_model == "llama3.2:1b"
    assert settings.ollama_base_url == "http://localhost:11434"
    assert "ollama" not in router._clients


def test_apply_runtime_provider_case_insensitivity_and_whitespace() -> None:
    """Verify apply_runtime_provider trims whitespace and handles mixed case."""
    settings = Settings()
    msg = apply_runtime_provider(
        provider="  OPENAI  ",
        model_name="  gpt-4o  ",
        api_key="  sk-test-12345  ",
        settings=settings,
    )
    assert "Active provider successfully switched to: openai" in msg
    assert settings.llm_provider == "openai"
    assert settings.openai_model == "gpt-4o"
    assert settings.openai_api_key is not None
    assert settings.openai_api_key.get_secret_value() == "sk-test-12345"


def test_apply_runtime_provider_unknown_provider_raises_uncaught_value_error() -> None:
    """Empirical reproduction of BUG: apply_runtime_provider crashes with uncaught ValueError.

    Expected: Clean error string or safe fallback.
    Actual: ValueError('"Settings" object has no field "anthropic_model"') because clean_provider
    is not restricted to supported providers before calling setattr(cfg, f"{clean_provider}_model").
    """
    settings = Settings()
    with pytest.raises(ValueError, match=r'"Settings" object has no field "anthropic_model"'):
        apply_runtime_provider(
            provider="anthropic",
            model_name="claude-3-5-sonnet",
            settings=settings,
        )


def test_apply_runtime_provider_unknown_provider_api_key_raises_uncaught_value_error() -> None:
    """Empirical reproduction of BUG: apply_runtime_provider crashes when given unknown api_key.

    Expected: Clean error string or safe fallback.
    Actual: ValueError('"Settings" object has no field "anthropic_api_key"').
    """
    settings = Settings()
    with pytest.raises(ValueError, match=r'"Settings" object has no field "anthropic_api_key"'):
        apply_runtime_provider(
            provider="anthropic",
            api_key="sk-ant-test-key",
            settings=settings,
        )


def test_apply_runtime_provider_empty_and_whitespace_only() -> None:
    """Verify apply_runtime_provider behavior on empty or whitespace-only provider string."""
    settings = Settings()
    msg = apply_runtime_provider(
        provider="   ",
        settings=settings,
    )
    assert "Active provider successfully switched to:" in msg
    assert settings.llm_provider == "groq"


# ==============================================================================
# 4. EMPIRICAL TEST: Tab 4 Defense Tactic Collapse Bug Reproduction
# ==============================================================================
def test_streamlit_simulator_defense_tactic_collapse_bug() -> None:
    """Empirical reproduction of BUG: Tab 4 collapses 4 valid tactics into terms_and_conditions.

    In src/legal_assistant/ui/app.py:
        chosen_tactic = (
            DefenseTacticType.UNBOXING_VIDEO_ABSENCE
            if "unboxing" in str(sim_tactic).lower()
            else DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND
        )
    This ignores:
    - 'IT Act Section 79 Intermediary Safe Harbor'
    - 'Courier / 3PL Transit Damage Disclaimer'
    - 'Delivery OTP Verification Defense'
    - 'Auto'
    """
    ui_options_and_expected = {
        "Terms & Conditions No Refund Waiver": (
            DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND
        ),
        "Absence of Unboxing Video": DefenseTacticType.UNBOXING_VIDEO_ABSENCE,
        "IT Act Section 79 Intermediary Safe Harbor": (
            DefenseTacticType.IT_ACT_SECTION_79_SAFE_HARBOR
        ),
        "Courier / 3PL Transit Damage Disclaimer": (
            DefenseTacticType.THIRD_PARTY_LOGISTICS_MANUFACTURER
        ),
        "Delivery OTP Verification Defense": (
            DefenseTacticType.OTP_VERIFICATION_ACCEPTANCE
        ),
    }

    for option_str, expected_tactic in ui_options_and_expected.items():
        actual_mapped = (
            DefenseTacticType.UNBOXING_VIDEO_ABSENCE
            if "unboxing" in str(option_str).lower()
            else DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND
        )
        if expected_tactic not in (
            DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND,
            DefenseTacticType.UNBOXING_VIDEO_ABSENCE,
        ):
            assert actual_mapped != expected_tactic
            assert actual_mapped == DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND


# ==============================================================================
# 5. EMPIRICAL TEST: Session State Multi-Step Persistence Across Reruns
# ==============================================================================
def test_streamlit_session_state_end_to_end_rerun_lifecycle(mock_router: LLMRouter) -> None:
    """Empirically stress-test session state persistence across full multi-tab workflow reruns."""
    at = AppTest.from_file(APP_FILE)
    at.session_state["router"] = mock_router
    at.run(timeout=30)
    assert len(at.exception) == 0

    # Step 1: Tab 1 — Click Load Sample Dispute
    load_btn = at.button(key="btn_load_sample")
    assert load_btn is not None
    load_btn.click().run(timeout=30)
    assert len(at.exception) == 0
    sample_text = at.session_state.get("ta_case_narrative", "")
    assert len(sample_text) > 50

    # Step 2: Tab 1 — Click Analyze Facts & Build Case
    analyze_btn = at.button(key="btn_analyze_case")
    assert analyze_btn is not None
    analyze_btn.click().run(timeout=30)
    assert len(at.exception) == 0

    case_obj = at.session_state.get("case_file")
    assert isinstance(case_obj, CaseFile)
    case_id = case_obj.case_id

    # Step 3: Sidebar Hot-Swap — Change provider to Ollama and apply
    at.sidebar.selectbox(key="sb_provider_select").select("ollama")
    at.sidebar.button(key="sb_btn_apply").click().run(timeout=30)
    assert len(at.exception) == 0
    assert at.session_state.get("active_provider") == "ollama"

    # STRESS ASSERTION: case_file must SURVIVE sidebar hot-swap rerun
    surviving_case = at.session_state.get("case_file")
    assert surviving_case is not None, "case_file was wiped after sidebar provider switch!"
    assert surviving_case.case_id == case_id

    # Step 4: Tab 2 — Assess Legal Standing
    assess_btn = at.button(key="btn_assess_standing")
    assert assess_btn is not None
    assess_btn.click().run(timeout=30)
    assert len(at.exception) == 0

    standing_obj = at.session_state.get("standing")
    assert isinstance(standing_obj, LegalStanding)
    assert standing_obj.is_consumer is True

    # STRESS ASSERTION: case_file and standing must co-exist in state
    assert at.session_state.get("case_file") is not None
    assert at.session_state.get("standing") is not None

    # Step 5: Tab 3 — Document Drafting & User Manual Edit
    draft_btn = at.button(key="btn_draft_single")
    assert draft_btn is not None
    draft_btn.click().run(timeout=30)
    assert len(at.exception) == 0

    assert at.session_state.get("drafted_doc") is not None
    initial_draft = at.session_state.get("draft_raw_text", "")
    assert len(initial_draft) > 50

    # Simulate user manually editing the markdown draft in the text area
    edited_text = initial_draft + "\n\n### Additional Complainant Clause: Statutory Damages."
    at.text_area(key="ta_raw_markdown_editor").set_value(edited_text).run(timeout=30)
    assert len(at.exception) == 0

    # STRESS ASSERTION: User manual edits must be preserved in draft_raw_text
    assert at.session_state.get("draft_raw_text") == edited_text
    dl_md = at.download_button(key="btn_dl_md")
    assert dl_md is not None
    assert at.session_state.get("draft_raw_text") == edited_text

    # Step 6: Tab 4 — Opposing Counsel Simulator & Chat Input Turn
    init_sim_btn = at.button(key="btn_init_sim")
    assert init_sim_btn is not None
    init_sim_btn.click().run(timeout=30)
    assert len(at.exception) == 0

    assert at.session_state.get("sim_state") is not None
    assert len(at.session_state.get("chat_history", [])) == 1

    # Take a simulator turn via chat_input
    chat_inp = at.chat_input(key="ci_consumer_rebuttal")
    assert chat_inp is not None
    chat_inp.set_value(
        "Under Section 2(47) of CPA 2019, arbitrary cancellation of warranty is unfair."
    ).run(timeout=30)
    assert len(at.exception) == 0

    # STRESS ASSERTIONS:
    chat_hist = at.session_state.get("chat_history", [])
    assert len(chat_hist) >= 2, f"Chat history did not advance: {chat_hist}"
    assert chat_hist[-1]["role"] == "user" or any(m["role"] == "user" for m in chat_hist)

    sim_scores = at.session_state.get("sim_scores", {})
    assert "turn_score" in sim_scores
    assert "cumulative_score" in sim_scores

    assert at.session_state.get("case_file") is not None, "case_file was lost during simulator!"
    assert at.session_state.get("standing") is not None, "standing was lost during simulator!"
    assert at.session_state.get("drafted_doc") is not None, "drafted_doc was lost during simulator!"
    assert at.session_state.get("draft_raw_text") == edited_text, "draft_raw_text was lost!"


# ==============================================================================
# 6. EMPIRICAL TEST: Out-of-Order Interactions & Boundary Guards
# ==============================================================================
def test_streamlit_out_of_order_interactions_fail_gracefully(mock_router: LLMRouter) -> None:
    """Verify Tab 2 assess or Tab 3 draft without Tab 1 intake warns cleanly without crashing."""
    at = AppTest.from_file(APP_FILE)
    at.session_state["router"] = mock_router
    at.run(timeout=30)
    assert len(at.exception) == 0

    # Click Assess Standing with NO case_file in session_state
    assess_btn = at.button(key="btn_assess_standing")
    assess_btn.click().run(timeout=30)
    assert len(at.exception) == 0
    assert at.session_state.get("standing") is None
    warning_texts = [w.value for w in at.warning]
    assert any("Tab 1" in w for w in warning_texts)

    # Click Draft Selected Document with NO case_file in session_state
    draft_btn = at.button(key="btn_draft_single")
    draft_btn.click().run(timeout=30)
    assert len(at.exception) == 0
    assert at.session_state.get("drafted_doc") is None
    warning_texts = [w.value for w in at.warning]
    assert any("Tab 1" in w for w in warning_texts)

    # Click Draft All 3 with NO case_file in session_state
    draft_all_btn = at.button(key="btn_draft_all")
    draft_all_btn.click().run(timeout=30)
    assert len(at.exception) == 0
    warning_texts = [w.value for w in at.warning]
    assert any("Tab 1" in w for w in warning_texts)
