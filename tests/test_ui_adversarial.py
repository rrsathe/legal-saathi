"""Adversarial stress testing suite for Legal Saathi Gradio UI and Ingestion CLI.

Covers:
1. Programmatic `create_app()` stress testing with empty, default, and mock dependencies.
2. Interactive callbacks: multilingual inputs (Hindi/Hinglish), out-of-scope escalation
   guardrails, missing evidence audit, and extreme inputs.
3. Legal standing and visual provenance: XSS injection vectors, HTML sanitization,
   and visual <mark> highlighting.
4. Document drafter: generation of all 3 document types (Demand Notice, Grievance Email,
   e-Daakhil Complaint) with and without legal standing.
5. Defense Simulator: multi-turn dialogue progression, speaker alternation, and
   statutory scoring calibration.
6. Live Model Switcher: hot-swapping between Groq, Ollama, OpenAI, and Gemini;
   cache invalidation, and connection ping error handling.
7. CLI Ingestion: argument parsing, validation probes, and empirical failure surface.
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
from legal_assistant.llm.base import (
    BaseLLMClient,
    LLMAuthenticationError,
    LLMConnectionError,
    LLMRateLimitError,
    LLMResponse,
)
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
    OpposingCounselSimulator,
)


# ==============================================================================
# Deterministic Mock Infrastructure
# ==============================================================================
class DeterministicMockLLMClient(BaseLLMClient):
    """Deterministic mock LLM client for adversarial UI testing."""

    def __init__(
        self,
        provider_name: str = "mock_provider",
        model_name: str = "mock-model-v1",
        simulate_error: Exception | None = None,
    ) -> None:
        """Initialize mock LLM client.

        Args:
            provider_name: Provider identifier.
            model_name: Model identifier string.
            simulate_error: Optional exception to raise during generation.
        """
        self._provider_name = provider_name
        self._model_name = model_name
        self._simulate_error = simulate_error
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
        """Generate deterministic text response.

        Args:
            prompt: User prompt text.
            system_prompt: System prompt instructions.
            temperature: Sampling temperature.
            **kwargs: Extra parameters.

        Returns:
            LLMResponse: Structured response payload.

        Raises:
            Exception: If simulate_error is configured.
        """
        self.call_count += 1
        if self._simulate_error is not None:
            raise self._simulate_error

        text = "PONG" if "Ping test" in prompt else "Deterministic mock response"
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

        Raises:
            Exception: If simulate_error is configured.
        """
        self.call_count += 1
        if self._simulate_error is not None:
            raise self._simulate_error

        if schema is LegalStanding:
            return LegalStanding(
                is_consumer=True,
                consumer_rationale="Complainant purchased goods for consideration.",
                pecuniary_commission_forum="District Commission",
                pecuniary_jurisdiction_limit="District Commission (Up to ₹50 Lakhs)",
                jurisdiction_rationale="Pecuniary value within jurisdiction.",
                limitation_rationale="Filed within 2-year limitation period.",
                estimated_timeline="21-45 days",
                estimated_costs=CostEstimate(
                    court_fees_inr=0.0,
                    notice_costs_inr=150.0,
                    lawyer_required=False,
                    total_estimated_out_of_pocket_inr="₹0 court fee",
                ),
                statutory_violations=[
                    StatutoryViolation(
                        statute="Consumer Protection Act, 2019",
                        section_or_rule="Section 2(47)",
                        title="Unfair Trade Practice",
                        violation_nature="unfair_trade_practice",
                        explanation="Refusal to refund consideration for defective item.",
                    )
                ],
                resolution_pathway=[],
            )
        return MagicMock(spec=schema)


@pytest.fixture
def mock_adversarial_settings() -> Settings:
    """Create isolated settings for adversarial tests.

    Returns:
        Settings: Test configuration instance.
    """
    return Settings(
        llm_provider="groq",
        groq_model="llama-3.1-8b-instant",
        groq_api_key=SecretStr("gsk_mock_test_key_adversarial_001"),
        ollama_model="llama3.1:8b",
        ollama_base_url="http://localhost:11434",
        openai_model="gpt-4o-mini",
        openai_api_key=SecretStr("sk-mock-openai-key-001"),
        gemini_model="gemini-1.5-flash",
        gemini_api_key=SecretStr("mock-gemini-key-001"),
    )


@pytest.fixture
def mock_adversarial_router(mock_adversarial_settings: Settings) -> LLMRouter:
    """Create LLMRouter with deterministic mock clients.

    Args:
        mock_adversarial_settings: Settings fixture.

    Returns:
        LLMRouter: Pre-configured router instance.
    """
    router = LLMRouter(settings=mock_adversarial_settings)
    for p in ["groq", "ollama", "openai", "gemini"]:
        router.register_client(
            p,
            DeterministicMockLLMClient(provider_name=p, model_name=f"{p}-mock-model"),
        )
    return router


@pytest.fixture
def empty_retriever() -> StatutoryHybridRetriever:
    """Create retriever with zero chunks.

    Returns:
        StatutoryHybridRetriever: Empty retriever instance.
    """
    return StatutoryHybridRetriever(
        chunks=[],
        dense_retriever=InMemoryDenseRetriever(),
    )


@pytest.fixture
def realistic_retriever() -> StatutoryHybridRetriever:
    """Create retriever with representative statutory chunks.

    Returns:
        StatutoryHybridRetriever: Populated retriever instance.
    """
    chunks = [
        RetrievedChunk(
            chunk_id="cpa_2_47",
            content=(
                "[STATUTE: Consumer Protection Act, 2019 | SECTION: 2(47) | "
                "TITLE: Unfair Trade Practice]\n"
                "Unfair trade practice means refusing to refund consideration paid for "
                "defective goods within thirty days."
            ),
            statute="Consumer Protection Act, 2019",
            chapter="Chapter I - Preliminary",
            section="Section 2(47)",
            title="Unfair Trade Practice",
            score=0.045,
            rank=1,
            retrieval_method="hybrid_rrf",
        ),
        RetrievedChunk(
            chunk_id="ecom_rule_4",
            content=(
                "[STATUTE: Consumer Protection (E-Commerce) Rules, 2020 | RULE: Rule 4 | "
                "TITLE: Duties of E-Commerce Entities]\n"
                "Every e-commerce entity shall acknowledge consumer complaint within "
                "forty-eight hours and resolve within thirty days."
            ),
            statute="Consumer Protection (E-Commerce) Rules, 2020",
            chapter="Duties of E-Commerce Entities",
            section="Rule 4",
            title="Duties of E-Commerce Entities",
            score=0.038,
            rank=2,
            retrieval_method="hybrid_rrf",
        ),
    ]
    return StatutoryHybridRetriever(
        chunks=chunks,
        dense_retriever=InMemoryDenseRetriever(),
    )


@pytest.fixture
def sample_test_case_file() -> CaseFile:
    """Create realistic structured CaseFile for workflow UI testing.

    Returns:
        CaseFile: Populated dispute case file.
    """
    return CaseFile(
        case_id="case_adv_ui_001",
        title="Defective Smartphone Refund Dispute",
        disputed_amount_inr=32000.0,
        transaction_date="2026-01-15",
        cause_of_action_date="2026-01-20",
        facts_summary=(
            "Consumer bought a smartphone on 2026-01-15 for Rs 32,000 from an online retailer. "
            "On 2026-01-20, device failed to power on. Retailer refused refund or replacement."
        ),
        opposite_parties=[
            OppositeParty(
                name="MegaRetail India Pvt Ltd",
                role="E-Commerce Marketplace",
                city="Mumbai",
                state="Maharashtra",
            )
        ],
        timeline=[
            TimelineEvent(
                date="2026-01-15",
                description="Ordered smartphone online for Rs 32,000.",
                significance="Purchase date",
            ),
            TimelineEvent(
                date="2026-01-20",
                description="Device failed; refund request rejected.",
                significance="Cause of action arose",
            ),
        ],
        evidence_checklist=[
            EvidenceItem(
                item_name="Tax Invoice",
                description="Tax invoice with IMEI and date.",
                is_available=True,
            )
        ],
        complainant=PartyDetails(
            name="Priya Patel",
            email="priya.patel@example.com",
            phone="+91-9876543210",
            city="Ahmedabad",
            state="Gujarat",
        ),
    )


# ==============================================================================
# 1. Gradio `create_app()` Construction Stress Tests
# ==============================================================================
class TestGradioAppConstructionAdversarial:
    """Stress tests probing create_app() instantiation under adverse configurations."""

    def test_create_app_with_empty_retriever(
        self,
        mock_adversarial_settings: Settings,
        mock_adversarial_router: LLMRouter,
        empty_retriever: StatutoryHybridRetriever,
    ) -> None:
        """Verify create_app instantiates cleanly when retriever has zero chunks."""
        app = create_app(
            settings=mock_adversarial_settings,
            llm_router=mock_adversarial_router,
            retriever=empty_retriever,
            scope_checker=ScopeChecker(),
        )
        assert isinstance(app, gr.Blocks)
        assert len(app.blocks) > 50

    def test_create_app_with_all_none_defaults(self) -> None:
        """Verify create_app instantiates cleanly when all arguments are None."""
        app = create_app(
            settings=None,
            llm_router=None,
            retriever=None,
            scope_checker=None,
        )
        assert isinstance(app, gr.Blocks)
        assert len(app.blocks) > 50

    def test_create_app_all_five_tabs_present_and_labeled(
        self,
        mock_adversarial_settings: Settings,
        mock_adversarial_router: LLMRouter,
        realistic_retriever: StatutoryHybridRetriever,
    ) -> None:
        """Verify all 5 tabs exist with correct labels in UI Blocks hierarchy."""
        app = create_app(
            settings=mock_adversarial_settings,
            llm_router=mock_adversarial_router,
            retriever=realistic_retriever,
            scope_checker=ScopeChecker(),
        )
        tab_labels: list[str] = []
        for block in app.blocks.values():
            if isinstance(block, gr.Tab):
                lbl = getattr(block, "label", "") or getattr(block, "name", "")
                tab_labels.append(lbl.lower())

        required_keywords = ["intake", "standing", "drafter", "simulator", "switcher"]
        for kw in required_keywords:
            assert any(kw in lbl for lbl in tab_labels), f"Missing tab matching keyword: {kw}"

    def test_create_app_state_blocks_registration(
        self,
        mock_adversarial_settings: Settings,
        mock_adversarial_router: LLMRouter,
        realistic_retriever: StatutoryHybridRetriever,
    ) -> None:
        """Verify that required gr.State instances are registered in UI blocks."""
        app = create_app(
            settings=mock_adversarial_settings,
            llm_router=mock_adversarial_router,
            retriever=realistic_retriever,
            scope_checker=ScopeChecker(),
        )
        state_blocks = [b for b in app.blocks.values() if isinstance(b, gr.State)]
        # We expect at least 4 state blocks: case, standing, sim, active_provider
        assert len(state_blocks) >= 4


# ==============================================================================
# 2. Interactive Intake Callbacks Adversarial Tests
# ==============================================================================
class TestInteractiveCallbacksAdversarial:
    """Stress tests probing intake callback with multilingual, out-of-scope, and extreme inputs."""

    def test_intake_multilingual_devanagari_hindi(
        self,
        mock_adversarial_router: LLMRouter,
    ) -> None:
        """Verify intake callback processes pure Hindi Devanagari dispute narrative."""
        hindi_narrative = (
            "मैंने 10 जनवरी 2026 को ₹45,000 का मोबाइल खरीदा। फोन टूटा हुआ निकला और "
            "कंपनी पैसे वापस नहीं कर रही है। बिल नंबर INV-998877 है।"
        )
        case_file, alert, timeline, avail, missing = handle_case_intake(
            narrative=hindi_narrative,
            router=mock_adversarial_router,
            scope_checker=ScopeChecker(),
            complainant_name="अमित शर्मा",
            complainant_city="जयपुर",
            complainant_state="राजस्थान",
        )
        assert case_file is not None
        assert "jurisdiction" in alert.lower() or "within" in alert.lower()
        assert len(timeline) >= 1
        assert case_file.complainant is not None
        assert case_file.complainant.name == "अमित शर्मा"

    def test_intake_multilingual_hinglish_narrative(
        self,
        mock_adversarial_router: LLMRouter,
    ) -> None:
        """Verify intake callback processes colloquial Hinglish narrative."""
        hinglish_narrative = (
            "Maine 15th Jan ko 35000 ka laptop mangwaya tha Flipkart se. Delivered "
            "broken display. Platform refund dene se refuse kar raha hai bolte hain "
            "manufacturer se baat karo."
        )
        case_file, alert, timeline, avail, missing = handle_case_intake(
            narrative=hinglish_narrative,
            router=mock_adversarial_router,
            scope_checker=ScopeChecker(),
            complainant_name="Rahul Verma",
            complainant_city="Delhi",
            complainant_state="Delhi",
        )
        assert case_file is not None
        assert case_file.disputed_amount_inr == 35000.0 or case_file.disputed_amount_inr is not None
        assert len(missing) >= 1

    def test_intake_out_of_scope_criminal_bns_alert(
        self,
        mock_adversarial_router: LLMRouter,
    ) -> None:
        """Verify intake callback intercepts criminal murder/extortion under BNS."""
        criminal_narrative = (
            "My business partner stole Rs 10 Lakhs and is threatening to murder my family "
            "under BNS Section 103 with physical violence."
        )
        case_file, alert, timeline, avail, missing = handle_case_intake(
            narrative=criminal_narrative,
            router=mock_adversarial_router,
            scope_checker=ScopeChecker(),
        )
        assert case_file is None
        assert "⚠️" in alert
        assert "Advocate" in alert
        assert "criminal" in alert.lower() or "scope" in alert.lower()
        assert len(timeline) == 0

    def test_intake_out_of_scope_cheque_bounce_ni_act(
        self,
        mock_adversarial_router: LLMRouter,
    ) -> None:
        """Verify intake callback intercepts Section 138 NI Act cheque bounce dispute."""
        cheque_narrative = (
            "A client issued a cheque for Rs 5,00,000 that bounced with memo funds insufficient "
            "under Section 138 of the Negotiable Instruments Act."
        )
        case_file, alert, timeline, avail, missing = handle_case_intake(
            narrative=cheque_narrative,
            router=mock_adversarial_router,
            scope_checker=ScopeChecker(),
        )
        assert case_file is None
        assert "⚠️" in alert
        assert "Advocate" in alert
        assert "cheque" in alert.lower() or "138" in alert.lower() or "scope" in alert.lower()
        assert len(timeline) == 0

    def test_intake_out_of_scope_commercial_b2b_large_claim(
        self,
        mock_adversarial_router: LLMRouter,
    ) -> None:
        """Verify intake callback intercepts commercial B2B contract disputes."""
        commercial_narrative = (
            "Our company entered into a B2B vendor contract for wholesale raw material "
            "worth Rs 3.5 Crore. The supplier breached the commercial agreement."
        )
        case_file, alert, timeline, avail, missing = handle_case_intake(
            narrative=commercial_narrative,
            router=mock_adversarial_router,
            scope_checker=ScopeChecker(),
        )
        assert case_file is None
        assert "⚠️" in alert
        assert "commercial" in alert.lower() or "b2b" in alert.lower() or "scope" in alert.lower()

    def test_intake_empty_and_whitespace_narratives(
        self,
        mock_adversarial_router: LLMRouter,
    ) -> None:
        """Verify intake callback handles empty or whitespace-only inputs without crashing."""
        for empty_text in ["", "   ", "\n\t  \n"]:
            case_file, alert, timeline, avail, missing = handle_case_intake(
                narrative=empty_text,
                router=mock_adversarial_router,
                scope_checker=ScopeChecker(),
            )
            assert case_file is None
            assert "please enter" in alert.lower()
            assert len(timeline) == 0

    def test_intake_extreme_length_narrative(
        self,
        mock_adversarial_router: LLMRouter,
    ) -> None:
        """Verify intake callback handles very large narratives (10,000+ characters)."""
        large_narrative = "I ordered an appliance for Rs 20,000 on 2026-01-01. " + (
            "Defective unit. " * 800
        )
        case_file, alert, timeline, avail, missing = handle_case_intake(
            narrative=large_narrative,
            router=mock_adversarial_router,
            scope_checker=ScopeChecker(),
        )
        assert case_file is not None
        assert case_file.disputed_amount_inr == 20000.0 or case_file.disputed_amount_inr is not None


# ==============================================================================
# 3. Legal Standing & Provenance HTML / XSS Injection Tests
# ==============================================================================
class TestLegalStandingProvenanceAdversarial:
    """Stress tests probing provenance formatting, HTML escaping, and XSS sanitization."""

    def test_provenance_xss_script_injection_escaped(self) -> None:
        """Verify malicious <script> tags in chunk text are converted to HTML entities."""
        malicious_chunk = RetrievedChunk(
            chunk_id="xss_01",
            content=(
                "<script>alert('pwned')</script> CPA Section 2(47) refund unfair trade practice"
            ),
            statute="Act <script>alert(1)</script>",
            chapter="Chapter",
            section="2(47)",
            title="Unfair Trade Practice <img src=x onerror=alert(2)>",
            score=0.035,
        )
        rendered = format_ui_provenance_with_marks([malicious_chunk])

        # Raw executable HTML script tags must NOT exist
        assert "<script>" not in rendered
        assert "</script>" not in rendered
        assert "<img src=x" not in rendered
        # Escaped entities must exist
        assert "&lt;script&gt;alert(" in rendered
        assert "&lt;/script&gt;" in rendered
        # Highlighting mark tags should still be injected around safe keywords
        assert "<mark" in rendered
        assert "refund" in rendered

    def test_provenance_svg_and_iframe_injection_escaped(self) -> None:
        """Verify SVG onload and iframe injections are escaped cleanly."""
        chunk = RetrievedChunk(
            chunk_id="xss_02",
            content="<svg onload=alert(document.domain)> <iframe src='http://evil.com'></iframe>",
            statute="Evil Statute",
            chapter="Chapter",
            section="Section 1",
            title="SVG Attack",
            score=0.01,
        )
        rendered = format_ui_provenance_with_marks([chunk])
        assert "<svg onload" not in rendered
        assert "<iframe" not in rendered
        assert "&lt;svg onload" in rendered
        assert "&lt;iframe" in rendered

    def test_provenance_empty_chunks_returns_placeholder(self) -> None:
        """Verify format_ui_provenance_with_marks handles empty list safely."""
        rendered = format_ui_provenance_with_marks([])
        assert "No statutory grounds retrieved" in rendered

    def test_provenance_nested_mark_tags_prevention(self) -> None:
        """Verify overlapping terms in chunk text do not generate nested <mark> tags."""
        chunk = RetrievedChunk(
            chunk_id="overlap_test",
            content=(
                "A consumer complained of a deficiency in service and unfair trade practice "
                "due to defective goods without refund within thirty days."
            ),
            statute="Consumer Protection Act, 2019",
            chapter="Chapter I",
            section="Section 2(11)",
            title="Deficiency",
            score=0.045,
        )
        html_out = format_ui_provenance_with_marks([chunk])
        assert "<mark" in html_out
        assert "</mark>" in html_out
        assert not re.search(r"<mark[^>]*>[^<]*<mark", html_out)
        assert html_out.count("<mark") == html_out.count("</mark>")

    def test_handle_evaluate_standing_none_case_file(
        self,
        mock_adversarial_router: LLMRouter,
        realistic_retriever: StatutoryHybridRetriever,
    ) -> None:
        """Verify handle_evaluate_standing handles None case_file gracefully."""
        standing, overview, viol, path, prov = handle_evaluate_standing(
            case_file=None,
            router=mock_adversarial_router,
            retriever=realistic_retriever,
        )
        assert standing is None
        assert "please complete case intake" in overview.lower()
        assert len(viol) == 0
        assert len(path) == 0

    def test_handle_evaluate_standing_success(
        self,
        sample_test_case_file: CaseFile,
        mock_adversarial_router: LLMRouter,
        realistic_retriever: StatutoryHybridRetriever,
    ) -> None:
        """Verify handle_evaluate_standing produces structured analysis and provenance HTML."""
        standing, overview, viol, path, prov = handle_evaluate_standing(
            case_file=sample_test_case_file,
            router=mock_adversarial_router,
            retriever=realistic_retriever,
        )
        assert standing is not None
        assert standing.is_consumer is True
        assert len(path) == 4
        assert "<details" in prov
        assert "<mark" in prov


# ==============================================================================
# 4. Document Drafter Adversarial Tests
# ==============================================================================
class TestDocumentDrafterAdversarial:
    """Stress tests probing drafting for all 3 document types and edge cases."""

    @pytest.mark.parametrize(
        "doc_type_label,expected_keyword",
        [
            ("Legal Demand Notice (15-Day)", "LEGAL NOTICE"),
            ("Grievance Escalation Email", "GRIEVANCE"),
            ("e-Daakhil Consumer Complaint Draft", "CONSUMER COMPLAINT"),
        ],
    )
    def test_handle_draft_all_three_document_types(
        self,
        sample_test_case_file: CaseFile,
        mock_adversarial_router: LLMRouter,
        realistic_retriever: StatutoryHybridRetriever,
        tmp_path: Path,
        doc_type_label: str,
        expected_keyword: str,
    ) -> None:
        """Verify drafting callback handles all 3 document types properly."""
        doc, md_text, plain_text, file_path = handle_draft_single(
            case_file=sample_test_case_file,
            standing=None,
            doc_type=doc_type_label,
            notice_days=15,
            router=mock_adversarial_router,
            retriever=realistic_retriever,
            export_dir=tmp_path,
        )
        assert doc is not None
        assert expected_keyword in md_text.upper() or expected_keyword in doc.title.upper()
        assert Path(file_path).exists()
        assert Path(file_path).read_text(encoding="utf-8") == md_text

    def test_handle_draft_single_none_case_file(
        self,
        mock_adversarial_router: LLMRouter,
        realistic_retriever: StatutoryHybridRetriever,
        tmp_path: Path,
    ) -> None:
        """Verify handle_draft_single returns notice if case_file is None."""
        doc, md_text, plain_text, file_path = handle_draft_single(
            case_file=None,
            standing=None,
            doc_type="legal_notice",
            router=mock_adversarial_router,
            retriever=realistic_retriever,
            export_dir=tmp_path,
        )
        assert doc is None
        assert "complete case intake" in md_text.lower()
        assert file_path == ""

    def test_handle_draft_unrecognized_document_type_fallback(
        self,
        sample_test_case_file: CaseFile,
        mock_adversarial_router: LLMRouter,
        realistic_retriever: StatutoryHybridRetriever,
        tmp_path: Path,
    ) -> None:
        """Verify unrecognized document type falls back to complaint draft."""
        doc, md_text, plain_text, file_path = handle_draft_single(
            case_file=sample_test_case_file,
            standing=None,
            doc_type="unrecognized_arbitrary_doc_type",
            router=mock_adversarial_router,
            retriever=realistic_retriever,
            export_dir=tmp_path,
        )
        assert doc is not None
        assert "COMPLAINT" in doc.document_type.upper() or "EDAAKHIL" in doc.document_type.upper()


# ==============================================================================
# 5. Defense Simulator Adversarial Tests
# ==============================================================================
class TestSimulatorAdversarial:
    """Stress tests probing multi-turn dialogue progression and scoring calibration."""

    def test_simulator_multi_turn_progression(
        self,
        mock_adversarial_router: LLMRouter,
    ) -> None:
        """Verify multi-turn state preserves conversation history and alternates turns."""
        sim = OpposingCounselSimulator(router=mock_adversarial_router)
        dummy_case = CaseFile(
            case_id="sim_adv_001",
            title="Damaged Package Dispute",
            disputed_amount_inr=15000.0,
            transaction_date="2026-01-01",
            facts_summary="Delivered damaged package.",
            opposite_parties=[OppositeParty(name="Seller", role="Merchant")],
            complainant=PartyDetails(name="Consumer", city="Delhi", state="Delhi"),
        )
        state = sim.start_simulation(case=dummy_case)
        assert len(state.turns) == 1
        assert state.turns[0].speaker == "opposing_counsel"

        # Turn 1: Consumer responds
        state2, chat_hist, score_str, strengths, weaknesses, advice = handle_simulator_turn(
            user_argument="Under Section 2(47) CPA 2019, refusing refund is unfair trade practice.",
            state=state,
            router=mock_adversarial_router,
        )
        assert len(state2.turns) == 3  # Initial counsel + consumer + rebuttal counsel
        assert state2.turns[1].speaker == "consumer"
        assert state2.turns[2].speaker == "opposing_counsel"
        assert len(chat_hist) >= 2

        # Turn 2: Consumer responds again
        state3, chat_hist2, score_str2, strengths2, weaknesses2, advice2 = handle_simulator_turn(
            user_argument="Rule 6(3) of E-Commerce Rules prohibits refusing returns for defects.",
            state=state2,
            router=mock_adversarial_router,
        )
        assert len(state3.turns) == 5
        assert state3.turns[3].speaker == "consumer"
        assert state3.turns[4].speaker == "opposing_counsel"

    def test_simulator_scoring_calibration_weak_vs_strong(
        self,
        mock_adversarial_router: LLMRouter,
    ) -> None:
        """Verify strong statutory rebuttal scores significantly higher than weak emotional plea."""
        sim = OpposingCounselSimulator(router=mock_adversarial_router)
        dummy_case = CaseFile(
            case_id="sim_score_001",
            title="Refund Denial",
            disputed_amount_inr=10000.0,
            transaction_date="2026-01-01",
            facts_summary="Denied refund for broken television.",
            opposite_parties=[OppositeParty(name="Shop", role="Seller")],
            complainant=PartyDetails(name="Consumer", city="Delhi", state="Delhi"),
        )
        state_weak = sim.start_simulation(case=dummy_case)
        weak_turn = "Please refund my money this is very unfair and I am poor student."
        _, _, score_weak_str, _, _, _ = handle_simulator_turn(
            user_argument=weak_turn,
            state=state_weak,
            router=mock_adversarial_router,
        )

        state_strong = sim.start_simulation(case=dummy_case)
        strong_turn = (
            "Under Section 2(47) of the Consumer Protection Act, 2019 and Rule 6(3) of the "
            "Consumer Protection (E-Commerce) Rules, 2020, no seller can refuse refund for "
            "defective goods. Your unilateral no-refund policy is void under Section 2(46)."
        )
        _, _, score_strong_str, _, _, _ = handle_simulator_turn(
            user_argument=strong_turn,
            state=state_strong,
            router=mock_adversarial_router,
        )

        match_weak = re.search(r"(\d+(\.\d+)?)", score_weak_str)
        match_strong = re.search(r"(\d+(\.\d+)?)", score_strong_str)
        assert match_weak is not None and match_strong is not None
        score_weak = float(match_weak.group(1))
        score_strong = float(match_strong.group(1))
        assert score_strong > score_weak, (
            f"Expected strong score ({score_strong}) > weak score ({score_weak})"
        )


# ==============================================================================
# 6. Live Model Switcher Adversarial Tests
# ==============================================================================
class TestLiveModelSwitcherAdversarial:
    """Stress tests probing runtime provider swapping, ping health-checks, and error traps."""

    @pytest.mark.parametrize("target_provider", ["ollama", "groq", "openai", "gemini"])
    def test_switch_across_all_supported_providers(
        self,
        mock_adversarial_settings: Settings,
        mock_adversarial_router: LLMRouter,
        target_provider: str,
    ) -> None:
        """Verify runtime switching cleanly updates settings provider across all 4 options."""
        msg = apply_runtime_provider(
            provider=target_provider,
            settings=mock_adversarial_settings,
            router=mock_adversarial_router,
        )
        assert mock_adversarial_settings.llm_provider == target_provider
        assert target_provider in msg.lower()

    def test_switch_unrecognized_provider_defaults_to_groq(
        self,
        mock_adversarial_settings: Settings,
        mock_adversarial_router: LLMRouter,
    ) -> None:
        """Verify switching to an unrecognized provider name falls back safely to groq."""
        apply_runtime_provider(
            provider="unknown_provider_xyz",
            settings=mock_adversarial_settings,
            router=mock_adversarial_router,
        )
        assert mock_adversarial_settings.llm_provider == "groq"

    @pytest.mark.parametrize(
        ("provider", "override_model"),
        [
            ("groq", "llama-3.3-70b-versatile"),
            ("ollama", "mistral:7b"),
            ("openai", "gpt-4o"),
            ("gemini", "gemini-1.5-pro"),
        ],
    )
    def test_switch_provider_with_explicit_model_override_adversarial(
        self,
        mock_adversarial_settings: Settings,
        mock_adversarial_router: LLMRouter,
        provider: str,
        override_model: str,
    ) -> None:
        """Verify runtime model override updates active model across providers."""
        msg = apply_runtime_provider(
            provider=provider,
            model_name=override_model,
            settings=mock_adversarial_settings,
            router=mock_adversarial_router,
        )
        assert mock_adversarial_settings.llm_provider == provider
        assert mock_adversarial_settings.get_active_model(provider) == override_model
        assert mock_adversarial_settings.default_model_name == override_model
        assert override_model in msg

    def test_ping_provider_authentication_error_handling(
        self,
        mock_adversarial_router: LLMRouter,
    ) -> None:
        """Verify ping handler catches LLMAuthenticationError cleanly."""
        client = DeterministicMockLLMClient(
            provider_name="groq",
            simulate_error=LLMAuthenticationError("Invalid API key provided"),
        )
        mock_adversarial_router.register_client("groq", client)
        result = ping_provider(provider="groq", router=mock_adversarial_router)
        assert "❌" in result
        assert "Invalid API key" in result or "failed" in result.lower()

    def test_ping_provider_rate_limit_error_handling(
        self,
        mock_adversarial_router: LLMRouter,
    ) -> None:
        """Verify ping handler catches LLMRateLimitError cleanly."""
        client = DeterministicMockLLMClient(
            provider_name="groq",
            simulate_error=LLMRateLimitError("Rate limit exceeded. Try again in 30s."),
        )
        mock_adversarial_router.register_client("groq", client)
        result = ping_provider(provider="groq", router=mock_adversarial_router)
        assert "❌" in result
        assert "Rate limit" in result or "failed" in result.lower()

    def test_ping_provider_connection_error_handling(
        self,
        mock_adversarial_router: LLMRouter,
    ) -> None:
        """Verify ping handler catches LLMConnectionError cleanly."""
        client = DeterministicMockLLMClient(
            provider_name="ollama",
            simulate_error=LLMConnectionError("Failed to reach http://localhost:11434"),
        )
        mock_adversarial_router.register_client("ollama", client)
        result = ping_provider(provider="ollama", router=mock_adversarial_router)
        assert "❌" in result
        assert "Failed to reach" in result or "failed" in result.lower()


# ==============================================================================
# 7. CLI Ingestion Empirical Validation Tests
# ==============================================================================
class TestCLIValidationsAdversarial:
    """Empirical tests probing CLI argument options and validation surface."""

    def test_cli_help_flag_displays_options(self) -> None:
        """Verify ingest_corpus.py --help documentation."""
        from scripts.ingest_corpus import parse_args

        with pytest.raises(SystemExit) as exc_info:
            parse_args(["--help"])
        assert exc_info.value.code == 0

    def test_cli_flag_no_validate_exists(self) -> None:
        """Verify parser sets validate=False when --no-validate is passed."""
        from scripts.ingest_corpus import parse_args

        args = parse_args(["--no-validate"])
        assert args.validate is False

    def test_cli_argument_validate_accepted(self) -> None:
        """Verify that passing --validate is accepted and sets validate=True."""
        from scripts.ingest_corpus import parse_args

        args = parse_args(["--in-memory", "--validate"])
        assert args.validate is True

    def test_statutory_corpus_top_k_for_colloquial_refund_query(
        self,
        realistic_retriever: StatutoryHybridRetriever,
    ) -> None:
        """Verify Section 2(47) retrieval behavior for colloquial refund queries."""
        query = "refusal to refund consideration paid for defective goods"
        results = realistic_retriever.retrieve(query, top_k=5)
        # Check that relevant section is retrieved in top results
        sections = [r.section for r in results]
        assert any("2(47)" in s for s in sections)
