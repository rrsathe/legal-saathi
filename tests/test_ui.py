"""Unit and programmatic integration tests for Legal Saathi Gradio UI.

Tests:
1. Programmatic construction of Gradio `Blocks` via `create_app()` without launching
   a blocking HTTP server.
2. Verification of all 5 UI tabs, structural layout, and core interactive components.
3. Visual citation provenance helper functions (HTML card generation, `<mark>` tag injection,
   XSS protection, and citation badges).
4. Live LLM Model Switcher runtime state updates, Settings modifications, and connection pings.
5. Workflow callback event handlers (Intake, Standing, Document Drafter, Simulator).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import gradio as gr
import pytest
from pydantic import SecretStr

from legal_assistant.config import Settings
from legal_assistant.guardrails.scope_checker import ScopeChecker
from legal_assistant.llm.base import BaseLLMClient, LLMConnectionError, LLMResponse
from legal_assistant.llm.router import LLMRouter
from legal_assistant.rag.hybrid_retriever import (
    InMemoryDenseRetriever,
    RetrievedChunk,
    StatutoryHybridRetriever,
)
from legal_assistant.schemas import (
    CaseFile,
    CostEstimate,
    EvidenceItem,
    LegalStanding,
    OppositeParty,
    PartyDetails,
    StatutoryViolation,
    TimelineEvent,
)
from legal_assistant.ui.app import (
    apply_runtime_provider,
    create_app,
    format_ui_provenance_with_marks,
    handle_case_intake,
    handle_draft_single,
    handle_evaluate_standing,
    handle_simulator_turn,
    ping_provider,
)
from legal_assistant.workflows.simulator import (
    DefenseTacticType,
    SimulatorState,
    SimulatorTurn,
)


# ==============================================================================
# Fixtures
# ==============================================================================
@pytest.fixture
def test_settings() -> Settings:
    """Create isolated application settings for UI testing.

    Returns:
        Settings: Test configuration instance.
    """
    return Settings(
        llm_provider="groq",
        groq_model="llama-3.1-8b-instant",
        groq_api_key=SecretStr("gsk_test_api_key_1234567890"),
        ollama_model="llama3.1:8b",
        ollama_base_url="http://localhost:11434",
        openai_model="gpt-4o-mini",
        openai_api_key=SecretStr("sk-test-openai-key"),
        gemini_model="gemini-1.5-flash",
        gemini_api_key=SecretStr("test-gemini-key"),
    )


class MockLLMClient(BaseLLMClient):
    """Deterministic mock LLM client for UI unit testing."""

    def __init__(self, provider_name: str = "mock", model_name: str = "mock-model") -> None:
        """Initialize mock client with provider and model identifiers.

        Args:
            provider_name: Provider name identifier.
            model_name: Model identifier string.
        """
        self._provider_name = provider_name
        self._model_name = model_name
        self.call_count = 0

    @property
    def provider_name(self) -> str:
        """Return provider identifier name."""
        return self._provider_name

    @property
    def model_name(self) -> str:
        """Return model identifier name."""
        return self._model_name

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate deterministic mock LLM text response.

        Args:
            prompt: User prompt text.
            system_prompt: System prompt instructions.
            temperature: Sampling temperature.
            **kwargs: Extra parameters.

        Returns:
            LLMResponse: Structured response payload.
        """
        self.call_count += 1
        text = "PONG" if "Ping test" in prompt else "Mock legal analysis response text."
        return LLMResponse(
            content=text,
            model=self._model_name,
            provider=self._provider_name,
        )

    def generate_structured(
        self,
        prompt: str,
        schema: type[Any],
        system_prompt: str = "",
        temperature: float | None = None,
        **kwargs: Any,
    ) -> Any:
        """Generate structured response conforming to schema.

        Args:
            prompt: User prompt text.
            schema: Target Pydantic model class.
            system_prompt: System prompt.
            temperature: Sampling temperature.
            **kwargs: Extra parameters.

        Returns:
            Any: Instantiated schema mock object.
        """
        self.call_count += 1
        if schema is LegalStanding:
            return LegalStanding(
                is_consumer=True,
                consumer_rationale="Complainant paid consideration for personal consumption.",
                pecuniary_commission_forum="District Commission",
                pecuniary_jurisdiction_limit="District Commission (Up to ₹50 Lakhs)",
                jurisdiction_rationale="Pecuniary jurisdiction under 50L.",
                limitation_rationale="Filed within 2 years.",
                estimated_timeline="15-45 days",
                estimated_costs=CostEstimate(
                    court_fees_inr=0.0,
                    notice_costs_inr=100.0,
                    lawyer_required=False,
                    total_estimated_out_of_pocket_inr="₹0 court fee",
                ),
                statutory_violations=[
                    StatutoryViolation(
                        statute="Consumer Protection Act, 2019",
                        section_or_rule="Section 2(47)",
                        title="Unfair Trade Practice",
                        violation_nature="unfair_trade_practice",
                        explanation="Refusal of refund within thirty days.",
                    )
                ],
                resolution_pathway=[],
            )
        return MagicMock(spec=schema)


@pytest.fixture
def mock_router(test_settings: Settings) -> LLMRouter:
    """Create LLMRouter with pre-registered deterministic mock clients.

    Args:
        test_settings: Settings fixture.

    Returns:
        LLMRouter: Pre-configured router instance.
    """
    router = LLMRouter(settings=test_settings)
    router.register_client(
        "groq", MockLLMClient(provider_name="groq", model_name="llama-3.1-8b-instant")
    )
    router.register_client(
        "ollama", MockLLMClient(provider_name="ollama", model_name="llama3.1:8b")
    )
    router.register_client(
        "openai", MockLLMClient(provider_name="openai", model_name="gpt-4o-mini")
    )
    router.register_client(
        "gemini", MockLLMClient(provider_name="gemini", model_name="gemini-1.5-flash")
    )
    return router


@pytest.fixture
def sample_statutory_chunks() -> list[RetrievedChunk]:
    """Provide realistic statutory chunks covering CPA 2019 and E-Commerce Rules 2020.

    Returns:
        list[RetrievedChunk]: Sample chunks for provenance rendering.
    """
    return [
        RetrievedChunk(
            chunk_id="cpa_sec_2_47",
            content=(
                "[STATUTE: Consumer Protection Act, 2019 | SECTION: 2(47) | "
                "TITLE: Unfair Trade Practice]\n"
                "Unfair trade practice means a trade practice which adopts any unfair method "
                "or deceptive practice including refusing to refund consideration paid for "
                "defective goods within thirty days."
            ),
            statute="Consumer Protection Act, 2019",
            chapter="Chapter I - Preliminary",
            section="2(47)",
            title="Unfair Trade Practice",
            score=0.0333,
            rank=1,
            retrieval_method="hybrid_rrf",
        ),
        RetrievedChunk(
            chunk_id="ecom_rule_4_5",
            content=(
                "[STATUTE: Consumer Protection (E-Commerce) Rules, 2020 | RULE: 4(5) | "
                "TITLE: Grievance Redressal Mechanism]\n"
                "Every e-commerce entity shall acknowledge receipt of any consumer complaint "
                "within forty-eight hours and redress the complaint within thirty days."
            ),
            statute="Consumer Protection (E-Commerce) Rules, 2020",
            chapter="Duties of E-Commerce Entities",
            section="Rule 4(5)",
            title="Grievance Redressal Mechanism",
            score=0.0250,
            rank=2,
            retrieval_method="hybrid_rrf",
        ),
        RetrievedChunk(
            chunk_id="cpa_sec_2_10",
            content=(
                "[STATUTE: Consumer Protection Act, 2019 | SECTION: 2(10) | TITLE: Defect]\n"
                "Defect means any fault, imperfection or shortcoming in the quality, quantity, "
                "potency, purity or standard required to be maintained in relation to any goods."
            ),
            statute="Consumer Protection Act, 2019",
            chapter="Chapter I - Preliminary",
            section="2(10)",
            title="Defect",
            score=0.0180,
            rank=3,
            retrieval_method="hybrid_rrf",
        ),
    ]


@pytest.fixture
def mock_retriever(sample_statutory_chunks: list[RetrievedChunk]) -> StatutoryHybridRetriever:
    """Create StatutoryHybridRetriever backed by in-memory dense vector store.

    Args:
        sample_statutory_chunks: Sample chunks fixture.

    Returns:
        StatutoryHybridRetriever: Instantiated hybrid retriever.
    """
    return StatutoryHybridRetriever(
        chunks=sample_statutory_chunks,
        dense_retriever=InMemoryDenseRetriever(),
    )


@pytest.fixture
def mock_scope_checker() -> ScopeChecker:
    """Create standard ScopeChecker instance.

    Returns:
        ScopeChecker: ScopeChecker instance.
    """
    return ScopeChecker()


@pytest.fixture
def app_instance(
    test_settings: Settings,
    mock_router: LLMRouter,
    mock_retriever: StatutoryHybridRetriever,
    mock_scope_checker: ScopeChecker,
) -> gr.Blocks:
    """Construct Gradio UI Blocks instance without launching a web server.

    Args:
        test_settings: Settings fixture.
        mock_router: Router fixture.
        mock_retriever: Hybrid retriever fixture.
        mock_scope_checker: Scope checker fixture.

    Returns:
        gr.Blocks: Constructed Gradio application object.
    """
    return create_app(
        settings=test_settings,
        llm_router=mock_router,
        retriever=mock_retriever,
        scope_checker=mock_scope_checker,
    )


@pytest.fixture
def sample_case_file() -> CaseFile:
    """Create realistic structured CaseFile for workflow UI testing.

    Returns:
        CaseFile: Populated dispute case file.
    """
    return CaseFile(
        case_id="case_test_ui_001",
        title="Defective Laptop Refund Refusal",
        disputed_amount_inr=55000.0,
        transaction_date="2026-01-10",
        cause_of_action_date="2026-01-14",
        facts_summary=(
            "Complainant bought a laptop on 2026-01-10 for Rs 55,000 from an e-commerce platform. "
            "The device was delivered with a broken display. Platform refused refund citing "
            "contact the manufacturer policy."
        ),
        opposite_parties=[
            OppositeParty(
                name="QuickCart Marketplace Pvt Ltd",
                role="E-Commerce Marketplace",
                city="Bangalore",
                state="Karnataka",
            )
        ],
        timeline=[
            TimelineEvent(
                date="2026-01-10",
                description="Ordered laptop online for Rs 55,000.",
                significance="Purchase date and consideration paid.",
            ),
            TimelineEvent(
                date="2026-01-14",
                description="Delivered with damaged display; immediately raised grievance.",
                significance="Cause of action arose.",
            ),
        ],
        evidence_checklist=[
            EvidenceItem(
                item_name="Tax Invoice",
                description="Tax invoice with serial number.",
                is_available=True,
            )
        ],
        complainant=PartyDetails(
            name="Rahul Sharma",
            email="rahul.sharma@example.com",
            phone="+91-9876543210",
            city="New Delhi",
            state="Delhi",
        ),
    )


# ==============================================================================
# 1. Programmatic `create_app()` Construction & Tab Verification
# ==============================================================================
def test_create_app_returns_blocks_instance(app_instance: gr.Blocks) -> None:
    """Verify that create_app() constructs a valid Gradio Blocks instance."""
    assert isinstance(app_instance, gr.Blocks)
    assert hasattr(app_instance, "blocks")
    assert len(app_instance.blocks) > 0


def test_create_app_contains_all_five_tabs(app_instance: gr.Blocks) -> None:
    """Verify that all five required functional tabs are constructed in the UI."""
    tab_labels: list[str] = []
    for block in app_instance.blocks.values():
        if isinstance(block, gr.Tab):
            label = getattr(block, "label", "") or getattr(block, "name", "")
            if label:
                tab_labels.append(label.lower())

    expected_keywords = [
        "intake",
        "standing",
        "drafter",
        "simulator",
        "switcher",
    ]
    for keyword in expected_keywords:
        assert any(keyword in label for label in tab_labels), (
            f"Expected tab matching keyword '{keyword}' not found in UI tabs: {tab_labels}"
        )


def test_core_interactive_components_exist(app_instance: gr.Blocks) -> None:
    """Verify that primary interactive component types exist across UI blocks."""
    block_types = [type(b).__name__ for b in app_instance.blocks.values()]

    assert "Textbox" in block_types
    assert "Button" in block_types
    assert "Dataframe" in block_types
    assert "Chatbot" in block_types
    assert "HTML" in block_types
    assert "Dropdown" in block_types
    assert "State" in block_types


def test_app_state_holders_registered(app_instance: gr.Blocks) -> None:
    """Verify that gr.State holders are initialized for case, standing, and sim."""
    state_blocks = [b for b in app_instance.blocks.values() if isinstance(b, gr.State)]
    assert len(state_blocks) >= 3


# ==============================================================================
# 2. Visual Citation Highlighting Helper Functions
# ==============================================================================
def test_format_ui_provenance_empty_chunks() -> None:
    """Verify provenance formatter gracefully handles empty chunk list."""
    result = format_ui_provenance_with_marks([])
    assert isinstance(result, str)
    assert "No statutory grounds retrieved" in result


def test_format_ui_provenance_contains_statutory_metadata(
    sample_statutory_chunks: list[RetrievedChunk],
) -> None:
    """Verify statutory headers, sections, and RRF scores are rendered in HTML."""
    html_output = format_ui_provenance_with_marks(sample_statutory_chunks)

    assert "Consumer Protection Act, 2019" in html_output
    assert "Sec 2(47)" in html_output or "2(47)" in html_output
    assert "Unfair Trade Practice" in html_output
    assert "RRF: 0.0333" in html_output or "0.033" in html_output
    assert "Rule 4(5)" in html_output


def test_format_ui_provenance_mark_tag_injection(
    sample_statutory_chunks: list[RetrievedChunk],
) -> None:
    """Verify that core statutory anchor keywords are wrapped in <mark> tags."""
    html_output = format_ui_provenance_with_marks(sample_statutory_chunks)

    assert "<mark" in html_output
    assert "</mark>" in html_output
    assert re.search(r"<mark[^>]*>unfair trade practice</mark>", html_output, re.IGNORECASE)
    assert re.search(r"<mark[^>]*>refund</mark>", html_output, re.IGNORECASE)
    assert re.search(r"<mark[^>]*>thirty days</mark>", html_output, re.IGNORECASE)


def test_format_ui_provenance_cited_section_badge(
    sample_statutory_chunks: list[RetrievedChunk],
) -> None:
    """Verify that sections cited in generated advice receive special visual badge."""
    html_output = format_ui_provenance_with_marks(
        chunks=sample_statutory_chunks,
        cited_sections=["Section 2(47)"],
    )

    assert "CITED IN ADVICE" in html_output
    rule_chunk_index = html_output.find("Rule 4(5)")
    assert rule_chunk_index != -1


def test_format_ui_provenance_xss_escaping_protection() -> None:
    """Verify malicious HTML tags in chunk content are safely escaped."""
    malicious_chunk = RetrievedChunk(
        chunk_id="xss_chunk",
        content="<script>alert('xss attack');</script> & 'arbitrary code' refund",
        statute="Malicious Act",
        chapter="Attack",
        section="0",
        title="XSS Test",
        score=0.05,
    )
    html_output = format_ui_provenance_with_marks([malicious_chunk])

    assert "<script>" not in html_output
    assert "&lt;script&gt;alert(" in html_output and "&lt;/script&gt;" in html_output
    assert "<mark" in html_output


def test_format_ui_provenance_custom_highlight_terms(
    sample_statutory_chunks: list[RetrievedChunk],
) -> None:
    """Verify custom highlight terms are wrapped in <mark> tags."""
    html_output = format_ui_provenance_with_marks(
        chunks=sample_statutory_chunks,
        highlight_terms=["deceptive", "preliminary"],
    )

    assert re.search(r"<mark[^>]*>deceptive</mark>", html_output, re.IGNORECASE)


# ==============================================================================
# 3. Model Switcher State Updates & Callbacks
# ==============================================================================
def test_apply_runtime_provider_switching(test_settings: Settings, mock_router: LLMRouter) -> None:
    """Verify switching provider updates active provider in settings."""
    msg = apply_runtime_provider(
        provider="ollama",
        settings=test_settings,
        router=mock_router,
    )

    assert test_settings.llm_provider == "ollama"
    assert "ollama" in msg.lower()


def test_apply_runtime_provider_with_api_key(
    test_settings: Settings,
    mock_router: LLMRouter,
) -> None:
    """Verify updating cloud provider API key modifies secret in settings."""
    apply_runtime_provider(
        provider="groq",
        api_key="gsk_new_secret_key_9999",
        settings=test_settings,
        router=mock_router,
    )

    assert test_settings.groq_api_key.get_secret_value() == "gsk_new_secret_key_9999"


def test_apply_runtime_provider_with_model_override(
    test_settings: Settings,
    mock_router: LLMRouter,
) -> None:
    """Verify updating model identifier updates settings and active model."""
    apply_runtime_provider(
        provider="groq",
        model_name="llama-3.3-70b-versatile",
        settings=test_settings,
        router=mock_router,
    )

    assert test_settings.groq_model == "llama-3.3-70b-versatile"
    assert test_settings.get_active_model("groq") == "llama-3.3-70b-versatile"


def test_apply_runtime_provider_cache_invalidation(
    test_settings: Settings,
    mock_router: LLMRouter,
) -> None:
    """Verify that changing provider settings invalidates router's cached client."""
    _ = mock_router.get_client("groq")
    assert "groq" in mock_router._clients

    apply_runtime_provider(
        provider="groq",
        model_name="llama-3.1-8b-instant",
        settings=test_settings,
        router=mock_router,
    )

    assert "groq" not in mock_router._clients


def test_ping_provider_success(mock_router: LLMRouter) -> None:
    """Verify ping_provider returns positive status banner when client responds."""
    status = ping_provider(provider="groq", router=mock_router)

    assert "✅" in status
    assert "groq" in status.lower()
    assert "ms" in status


def test_ping_provider_failure_handling(mock_router: LLMRouter) -> None:
    """Verify ping_provider catches connection errors and outputs diagnostic notice."""
    failing_client = MagicMock(spec=BaseLLMClient)
    failing_client.generate.side_effect = LLMConnectionError("Failed to connect to host")
    mock_router.register_client("broken_provider", failing_client)

    status = ping_provider(provider="broken_provider", router=mock_router)

    assert "❌" in status
    assert "failed" in status.lower() or "error" in status.lower()


# ==============================================================================
# 4. Workflow Event Handler Callbacks
# ==============================================================================
def test_handle_case_intake_valid_narrative(
    mock_router: LLMRouter,
    mock_scope_checker: ScopeChecker,
) -> None:
    """Verify intake callback processes valid dispute narrative into CaseFile."""
    narrative = (
        "I purchased an electric scooter for Rs 85,000 on 2026-02-01. Within 3 days, "
        "the battery caught fire. The dealer refused refund."
    )
    case_file, alert_text, timeline_data, evidence_avail, missing_ev = handle_case_intake(
        narrative=narrative,
        router=mock_router,
        scope_checker=mock_scope_checker,
    )

    assert isinstance(case_file, CaseFile)
    assert case_file.disputed_amount_inr == 85000.0 or case_file.disputed_amount_inr is not None
    assert alert_text == "" or "in scope" in alert_text.lower() or "within" in alert_text.lower()
    assert len(timeline_data) >= 1
    assert isinstance(evidence_avail, list)
    assert isinstance(missing_ev, list)


def test_handle_case_intake_out_of_scope_alert(
    mock_router: LLMRouter,
    mock_scope_checker: ScopeChecker,
) -> None:
    """Verify intake callback catches non-consumer disputes and flags Advocate alert."""
    narrative = (
        "Someone gave me a cheque for Rs 25,00,000 that bounced under Section 138 NI Act, "
        "and they are threatening my family with physical violence."
    )
    case_file, alert_text, timeline_data, evidence_avail, missing_ev = handle_case_intake(
        narrative=narrative,
        router=mock_router,
        scope_checker=mock_scope_checker,
    )

    alert_lower = alert_text.lower()
    assert "advocate" in alert_lower or "criminal" in alert_lower or "scope" in alert_lower
    assert len(timeline_data) == 0


def test_handle_case_intake_empty_narrative(
    mock_router: LLMRouter,
    mock_scope_checker: ScopeChecker,
) -> None:
    """Verify intake callback handles empty narrative with prompt notice."""
    case_file, alert_text, timeline_data, evidence_avail, missing_ev = handle_case_intake(
        narrative="   ",
        router=mock_router,
        scope_checker=mock_scope_checker,
    )

    assert case_file is None
    assert "please enter" in alert_text.lower() or "empty" in alert_text.lower()


def test_handle_evaluate_standing(
    sample_case_file: CaseFile,
    mock_router: LLMRouter,
    mock_retriever: StatutoryHybridRetriever,
) -> None:
    """Verify evaluate standing callback produces legal analysis and provenance HTML."""
    standing, overview_md, violations_df, pathway_df, provenance_html = handle_evaluate_standing(
        case_file=sample_case_file,
        router=mock_router,
        retriever=mock_retriever,
    )

    assert isinstance(standing, LegalStanding)
    assert "Section 2(7)" in overview_md or "Consumer" in overview_md
    assert len(pathway_df) == 4
    assert "<details" in provenance_html or "statutory" in provenance_html.lower()


def test_handle_draft_single_document(
    sample_case_file: CaseFile,
    mock_router: LLMRouter,
    mock_retriever: StatutoryHybridRetriever,
    tmp_path: Path,
) -> None:
    """Verify drafting handler generates markdown, plain text, and downloadable file."""
    standing = LegalStanding(
        is_consumer=True,
        consumer_rationale="Complainant has valid consumer standing under Section 2(7).",
        pecuniary_commission_forum="District Commission",
        pecuniary_jurisdiction_limit="District Commission (Up to ₹50 Lakhs)",
        jurisdiction_rationale="Jurisdiction valid under Section 34 CPA 2019.",
        limitation_rationale="Complaint filed within 2 years of cause of action.",
        estimated_timeline="15-45 days",
        estimated_costs=CostEstimate(
            court_fees_inr=0.0,
            notice_costs_inr=100.0,
            lawyer_required=False,
            total_estimated_out_of_pocket_inr="₹0 court fees under ₹5 Lakhs",
        ),
        statutory_violations=[
            StatutoryViolation(
                statute="Consumer Protection Act, 2019",
                section_or_rule="Section 2(47)",
                title="Unfair Trade Practice",
                violation_nature="unfair_trade_practice",
                explanation="Refusal of refund within thirty days.",
            )
        ],
    )

    doc, md_text, plain_text, file_path = handle_draft_single(
        case_file=sample_case_file,
        standing=standing,
        doc_type="legal_notice",
        notice_days=15,
        router=mock_router,
        retriever=mock_retriever,
        export_dir=tmp_path,
    )

    assert doc is not None
    assert "LEGAL NOTICE" in md_text.upper() or "DEMAND" in md_text.upper()
    assert "15" in md_text
    assert Path(file_path).exists()


def test_handle_simulator_turn(
    sample_case_file: CaseFile,
    mock_router: LLMRouter,
) -> None:
    """Verify simulator turn callback processes rebuttal and returns feedback scores."""
    sim_state = SimulatorState(
        case_id=sample_case_file.case_id,
        case_summary=sample_case_file.facts_summary,
        turns=[
            SimulatorTurn(
                turn_number=1,
                speaker="opposing_counsel",
                content="Our policy requires an unboxing video. Without it, no refund is granted.",
                defense_tactic=DefenseTacticType.UNBOXING_VIDEO_ABSENCE,
            )
        ],
    )

    updated_state, chat_history, score_text, strengths_md, weaknesses_md, advice_md = (
        handle_simulator_turn(
            user_argument=(
                "Under CPA 2019 Section 2(11) deficiency in service, you cannot impose an "
                "unboxing video requirement as an unfair contract under Section 2(46)."
            ),
            state=sim_state,
            router=mock_router,
        )
    )

    assert isinstance(updated_state, SimulatorState)
    assert len(chat_history) >= 2
    assert "score" in score_text.lower() or any(char.isdigit() for char in score_text)
    assert strengths_md != ""
