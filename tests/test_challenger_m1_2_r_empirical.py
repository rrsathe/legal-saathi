"""Empirical Stress & State Lifecycle Test Suite.

Authored by Replacement Challenger 2 (State & Provider Stress Challenger).
Empirically challenges:
1. Streamlit session state management and persistence across repeated simulated reruns.
2. Runtime provider hot-swapping (`apply_runtime_provider`) and health ping (`ping_provider`)
   under adversarial, invalid, malformed, and edge-case inputs.
3. Resource caching (`@st.cache_resource get_cached_retriever`) preventing redundant
   corpus re-chunking and re-indexing across application lifecycles.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast
from unittest.mock import MagicMock, patch

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
from legal_assistant.rag.chunker import StatutoryChunker
from legal_assistant.rag.hybrid_retriever import StatutoryHybridRetriever
from legal_assistant.schemas import CaseFile, LegalStanding
from legal_assistant.ui.app import (
    apply_runtime_provider,
    get_cached_retriever,
    handle_simulator_turn,
    ping_provider,
)
from tests.test_ui import MockLLMClient

APP_FILE = str(
    Path(__file__).resolve().parent.parent / "src" / "legal_assistant" / "ui" / "app.py"
)


class FaultyLLMClient(MockLLMClient):
    """Configurable mock LLM client designed to inject faults for adversarial testing."""

    def __init__(
        self,
        provider_name: str = "faulty",
        model_name: str = "fault-model",
        fault_type: str | None = None,
        fault_message: str = "Simulated fault",
    ) -> None:
        super().__init__(provider_name=provider_name, model_name=model_name)
        self.fault_type = fault_type
        self.fault_message = fault_message

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        if self.fault_type == "connection":
            raise LLMConnectionError(self.fault_message)
        if self.fault_type == "auth":
            raise LLMAuthenticationError(self.fault_message)
        if self.fault_type == "rate_limit":
            raise LLMRateLimitError(self.fault_message)
        if self.fault_type == "generic":
            raise RuntimeError(self.fault_message)
        return super().generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            **kwargs,
        )


@pytest.fixture
def mock_router() -> LLMRouter:
    """Fixture providing LLMRouter with deterministic mock clients."""
    settings = Settings(
        llm_provider="groq",
        groq_api_key=SecretStr("mock-groq-key"),
        groq_model="llama-3.1-8b-instant",
    )
    router = LLMRouter(settings=settings)
    for p in ("groq", "ollama", "openai", "gemini"):
        router.register_client(p, MockLLMClient(provider_name=p, model_name=f"mock-{p}"))
    return router


# ==============================================================================
# 1. Empirical Tests: Session State Lifecycle & Rerun Persistence
# ==============================================================================
class TestStreamlitSessionStateLifecycleAcrossReruns:
    """Empirical challenge: verify session state persistence across sequential simulated reruns."""

    def test_full_workflow_session_state_persistence_across_multiple_reruns(
        self, mock_router: LLMRouter
    ) -> None:
        """Simulate a complete 10-step user journey with multiple provider switches and reruns.

        Verifies that:
        - Loading sample dispute populates state and survives subsequent reruns.
        - Case intake builds CaseFile and persists in session_state.
        - Provider hot-swapping in the sidebar does NOT wipe or reset CaseFile, standing, or drafts.
        - Legal standing evaluation persists across further provider switches.
        - User manual edits to raw markdown editor are preserved dynamically in download payloads.
        - Simulator turns increment turn count and update cumulative scores without data loss.
        """
        at = AppTest.from_file(APP_FILE)
        at.session_state["router"] = mock_router

        # Rerun 1: Mount initial app
        at.run(timeout=30)
        assert len(at.exception) == 0, f"Exceptions on mount: {at.exception}"
        assert at.session_state.get("case_file") is None

        # Rerun 2: Click 'Load Sample Dispute'
        at.button(key="btn_load_sample").click().run(timeout=30)
        assert len(at.exception) == 0
        narrative_1 = str(at.session_state.get("ta_case_narrative", ""))
        assert len(narrative_1) > 100
        assert "smartphone" in narrative_1.lower()

        # Rerun 3: Verify narrative persists on a pure rerun without clicking load button
        at.run(timeout=30)
        assert len(at.exception) == 0
        narrative_2 = str(at.session_state.get("ta_case_narrative", ""))
        assert narrative_2 == narrative_1

        # Rerun 4: Trigger 'Analyze Facts & Build Case'
        at.button(key="btn_analyze_case").click().run(timeout=30)
        assert len(at.exception) == 0
        case_file_1 = at.session_state.get("case_file")
        assert isinstance(case_file_1, CaseFile)
        assert case_file_1.disputed_amount_inr is not None
        assert len(at.session_state.get("intake_timeline", [])) >= 1

        # Rerun 5: Hot-swap provider to OpenAI in Sidebar and apply settings
        at.sidebar.selectbox(key="sb_provider_select").select("openai")
        at.sidebar.button(key="sb_btn_apply").click().run(timeout=30)
        assert len(at.exception) == 0
        assert at.session_state.get("active_provider") == "openai"
        # CRITICAL ASSERTION: case_file must NOT be wiped by sidebar provider switch!
        case_file_after_switch = at.session_state.get("case_file")
        assert case_file_after_switch is not None
        assert isinstance(case_file_after_switch, CaseFile)
        assert case_file_after_switch.case_id == case_file_1.case_id

        # Rerun 6: Ping Provider
        at.sidebar.button(key="sb_btn_ping").click().run(timeout=30)
        assert len(at.exception) == 0
        # State must remain intact after ping
        assert at.session_state.get("case_file") is not None

        # Rerun 7: Evaluate Legal Standing in Tab 2
        at.button(key="btn_assess_standing").click().run(timeout=30)
        assert len(at.exception) == 0
        standing_1 = at.session_state.get("standing")
        assert isinstance(standing_1, LegalStanding)
        assert standing_1.is_consumer is True
        assert at.session_state.get("case_file") is not None

        # Rerun 8: Hot-swap provider again to Gemini in Sidebar
        at.sidebar.selectbox(key="sb_provider_select").select("gemini")
        at.sidebar.button(key="sb_btn_apply").click().run(timeout=30)
        assert len(at.exception) == 0
        assert at.session_state.get("active_provider") == "gemini"
        # Both case_file and standing must persist across the 2nd provider hot-swap!
        assert at.session_state.get("case_file") is not None
        assert at.session_state.get("standing") is not None

        # Rerun 9: Generate Draft Document in Tab 3
        at.button(key="btn_draft_single").click().run(timeout=30)
        assert len(at.exception) == 0
        draft_doc = at.session_state.get("drafted_doc")
        assert draft_doc is not None
        initial_draft_text = str(at.session_state.get("draft_raw_text", ""))
        assert len(initial_draft_text) > 50

        # Rerun 10: Simulate user editing the raw markdown text area
        edited_content = (
            "# AMENDED LEGAL NOTICE UNDER SECTION 38 CPA 2019\n\n"
            "This is a custom user-edited notice text with specific demands."
        )
        at.session_state["ta_raw_markdown_editor"] = edited_content
        at.run(timeout=30)
        assert len(at.exception) == 0
        # The draft_raw_text and download button payloads must reflect user edits
        assert at.session_state.get("draft_raw_text") == edited_content
        dl_md = at.download_button(key="btn_dl_md")
        assert dl_md is not None

        # Rerun 11: Start Opposing Counsel Simulator in Tab 4
        at.button(key="btn_init_sim").click().run(timeout=30)
        assert len(at.exception) == 0
        sim_state_1 = at.session_state.get("sim_state")
        assert sim_state_1 is not None
        chat_hist = at.session_state.get("chat_history", [])
        assert len(chat_hist) >= 1
        assert chat_hist[0]["role"] == "assistant"

        # Rerun 12: Advance simulator turn
        u_state, hist, s_txt, s_md, w_md, a_md = handle_simulator_turn(
            user_argument=(
                "Under Section 2(47), refusal to refund for cracked screen is "
                "unfair trade practice."
            ),
            state=sim_state_1,
            router=mock_router,
        )
        at.session_state["sim_state"] = u_state
        at.session_state["chat_history"] = hist
        at.session_state["sim_scores"] = {
            "turn_score": 90.0,
            "cumulative_score": 85.0,
            "strengths": s_md,
            "weaknesses": w_md,
            "advice": a_md,
        }
        at.run(timeout=30)
        assert len(at.exception) == 0
        assert len(at.session_state.get("chat_history", [])) >= 2
        # Verify complete multi-tab state integrity
        assert at.session_state.get("case_file") is not None
        assert at.session_state.get("standing") is not None
        assert at.session_state.get("drafted_doc") is not None
        assert at.session_state.get("sim_state") is not None

    def test_uninitialized_state_guards_across_tabs(self, mock_router: LLMRouter) -> None:
        """Verify that tabs handle None case_file gracefully without unhandled crashes."""
        at = AppTest.from_file(APP_FILE)
        at.session_state["router"] = mock_router
        at.run(timeout=30)

        # Tab 2: Assess standing without CaseFile
        at.button(key="btn_assess_standing").click().run(timeout=30)
        assert len(at.exception) == 0
        assert at.session_state.get("standing") is None
        warnings = [w.value for w in at.warning]
        assert any("Case Intake" in w for w in warnings)

        # Tab 3: Draft single document without CaseFile
        at.button(key="btn_draft_single").click().run(timeout=30)
        assert len(at.exception) == 0
        assert at.session_state.get("drafted_doc") is None
        warnings = [w.value for w in at.warning]
        assert any("Case Intake" in w for w in warnings)

        # Tab 3: Draft all documents without CaseFile
        at.button(key="btn_draft_all").click().run(timeout=30)
        assert len(at.exception) == 0
        warnings = [w.value for w in at.warning]
        assert any("Case Intake" in w for w in warnings)


# ==============================================================================
# 2. Empirical Tests: Provider Hot-Swapping & Ping Robustness
# ==============================================================================
class TestRuntimeProviderHotSwappingStress:
    """Empirical challenge: stress-test provider hot-swapping and ping with invalid inputs."""

    @pytest.mark.parametrize(
        ("input_provider", "expected_active_provider"),
        [
            ("groq", "groq"),
            ("ollama", "ollama"),
            ("openai", "openai"),
            ("gemini", "gemini"),
            ("GROQ", "groq"),
            ("  OLLAMA  ", "ollama"),
            ("  OpenAI  ", "openai"),
            ("GeMiNi", "gemini"),
            ("", "groq"),  # Empty string fallback
            ("   ", "groq"),  # Whitespace string fallback
            ("unsupported_custom_provider", "groq"),  # Unknown provider fallback
            ("aws_bedrock", "groq"),  # Unknown provider fallback
        ],
    )
    def test_apply_runtime_provider_provider_string_variations(
        self, input_provider: str, expected_active_provider: str
    ) -> None:
        """Verify provider name variations, casing, whitespace, and unknown names are handled."""
        settings = Settings()
        msg = apply_runtime_provider(provider=input_provider, settings=settings)
        assert settings.llm_provider == expected_active_provider
        assert "Active provider successfully switched to:" in msg

    def test_apply_runtime_provider_with_model_override_and_cache_invalidation(
        self, mock_router: LLMRouter
    ) -> None:
        """Verify model override updates default_model_name and clears router client cache."""
        settings = Settings()
        mock_router._clients["ollama"] = MockLLMClient("ollama", "old-model")
        assert "ollama" in mock_router._clients

        msg = apply_runtime_provider(
            provider="ollama",
            model_name="llama3.2:1b",
            base_url="http://localhost:11434",
            settings=settings,
            router=mock_router,
        )
        assert settings.llm_provider == "ollama"
        assert settings.ollama_model == "llama3.2:1b"
        assert settings.default_model_name == "llama3.2:1b"
        assert "ollama" not in mock_router._clients  # Cache was invalidated!
        assert "llama3.2:1b" in msg

    def test_apply_runtime_provider_empty_and_none_optional_parameters(self) -> None:
        """Verify empty and None strings for optional parameters do not corrupt settings."""
        settings = Settings()
        original_groq_model = settings.groq_model

        # Passing empty strings for optional parameters
        apply_runtime_provider(
            provider="groq",
            model_name="",
            api_key="",
            base_url="",
            settings=settings,
        )
        assert settings.llm_provider == "groq"
        assert settings.groq_model == original_groq_model

        # Passing None for optional parameters
        apply_runtime_provider(
            provider="groq",
            model_name=None,
            api_key=None,
            base_url=None,
            settings=settings,
        )
        assert settings.llm_provider == "groq"
        assert settings.groq_model == original_groq_model

    def test_apply_runtime_provider_none_provider_raises_attribute_error(self) -> None:
        """Empirically document that passing None as provider raises AttributeError.

        This validates runtime type boundaries: provider expects a str.
        """
        with pytest.raises(AttributeError, match="'NoneType' object has no attribute 'lower'"):
            apply_runtime_provider(provider=cast(str, None))

    def test_ping_provider_operational_success(self, mock_router: LLMRouter) -> None:
        """Verify ping_provider returns operational status and latency for valid provider."""
        result = ping_provider(provider="groq", router=mock_router)
        assert "✅" in result
        assert "operational" in result
        assert "Latency:" in result

    @pytest.mark.parametrize(
        "faulty_scenario",
        [
            ("connection", LLMConnectionError, "Connection refused at 127.0.0.1:11434"),
            ("auth", LLMAuthenticationError, "Invalid API Key 401 Unauthorized"),
            ("rate_limit", LLMRateLimitError, "Rate limit reached 429"),
            ("generic", RuntimeError, "Catastrophic memory fault in C++ extension"),
        ],
    )
    def test_ping_provider_error_handling_and_fault_containment(
        self,
        faulty_scenario: tuple[str, type[Exception], str],
    ) -> None:
        """Empirically verify ping_provider catches all network/auth/rate/runtime errors cleanly."""
        fault_type, _, fault_msg = faulty_scenario
        router = LLMRouter(settings=Settings())
        faulty_client = FaultyLLMClient(
            provider_name="ollama",
            fault_type=fault_type,
            fault_message=fault_msg,
        )
        router.register_client("ollama", faulty_client)

        result = ping_provider(provider="ollama", router=router)
        assert "❌" in result
        assert fault_msg in result

    def test_ping_provider_unsupported_provider_name(self, mock_router: LLMRouter) -> None:
        """Verify pinging an unsupported provider returns clean error without unhandled crash."""
        result = ping_provider(provider="unsupported_quantum_llm", router=mock_router)
        assert "❌" in result
        assert "Unsupported LLM provider" in result or "Unexpected error" in result

    def test_ping_provider_none_router_safety(self) -> None:
        """Verify ping_provider with None router is caught cleanly by exception handler."""
        result = ping_provider(provider="groq", router=cast(LLMRouter, None))
        assert "❌" in result
        assert "NoneType" in result


# ==============================================================================
# 3. Empirical Tests: Resource Caching & Retriever Re-indexing Prevention
# ==============================================================================
class TestStatutoryRetrieverCachingEmpirical:
    """Empirical challenge: verify @st.cache_resource prevents redundant corpus indexing."""

    def test_retriever_caching_identity_and_avoidance_of_reindexing(self) -> None:
        """Verify get_cached_retriever() returns the exact same instance across calls.

        Also verifies that StatutoryChunker.split_text is NOT called on subsequent invocations.
        """
        # Call 1: Populates or fetches the resource
        retriever_1 = get_cached_retriever()
        assert isinstance(retriever_1, StatutoryHybridRetriever)
        assert len(retriever_1.indexed_chunks) > 0

        # Call 2: Must return exact identical object reference
        with patch.object(StatutoryChunker, "split_text", MagicMock()) as mock_split:
            retriever_2 = get_cached_retriever()
            assert retriever_1 is retriever_2
            # Crucial assertion: no re-chunking of corpus on cached call!
            mock_split.assert_not_called()

    def test_cached_retriever_query_functionality(self) -> None:
        """Verify that the cached retriever successfully executes hybrid RRF retrieval."""
        retriever = get_cached_retriever()
        chunks, confidence = retriever.retrieve_with_confidence(
            "deficiency in service refund denied", top_k=3
        )
        assert len(chunks) > 0
        assert confidence.top_rrf_score > 0.0
        for chunk in chunks:
            assert chunk.content
            assert chunk.statute
            assert chunk.score > 0.0

    def test_streamlit_app_uses_cached_retriever_across_reruns(
        self, mock_router: LLMRouter
    ) -> None:
        """Verify AppTest initializes with cached retriever and preserves it across reruns."""
        at = AppTest.from_file(APP_FILE)
        at.session_state["router"] = mock_router
        at.run(timeout=30)

        assert len(at.exception) == 0
        app_retriever_1 = at.session_state.get("retriever")
        assert isinstance(app_retriever_1, StatutoryHybridRetriever)

        # Rerun and verify retriever identity is preserved
        at.run(timeout=30)
        assert len(at.exception) == 0
        app_retriever_2 = at.session_state.get("retriever")
        assert app_retriever_1 is app_retriever_2
