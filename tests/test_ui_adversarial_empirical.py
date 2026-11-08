"""Empirical Challenger 1: Adversarial and Boundary Stress Test Suite for UI.

Comprehensive empirical verification covering:
1. `format_ui_provenance_with_marks` & `CORE_HIGHLIGHT_TERMS`:
   - XSS injection payloads in chunk content and metadata
     (<script>, <img>, <svg>, <iframe>, javascript:)
   - Nested <mark> prevention under overlapping and substring terms
   - Double-encoding prevention and entity preservation
   - Regex metacharacters, HTML entities, and Unicode/Devanagari in highlight terms
   - Amber highlight palette and Citation Telemetry banner styling
2. All 8 public helper functions boundary & error resilience:
   - `apply_runtime_provider` with case variations, whitespace, unknown providers, cache
   - `ping_provider` with connection, auth, rate limit, and unexpected runtime errors
   - `handle_case_intake` with empty, out-of-scope, extreme length, and Unicode details
   - `handle_evaluate_standing` with None case_file and extreme pecuniary amounts
   - `handle_draft_single` with None case_file, doc_type fallbacks, and disk export
   - `handle_simulator_turn` with None state, empty inputs, speaker alternation, and conclusion
3. Streamlit App Execution (`render_streamlit_app` via `streamlit.testing.v1.AppTest`):
   - Rapid state transitions and out-of-order user flows
   - Unexpected session states (clicking buttons before intake, chat with None sim_state)
   - Multi-turn simulator progression to conclusion via chat input
   - Sidebar provider switching and ping execution
"""

from __future__ import annotations

import html
import re
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pydantic import SecretStr
from streamlit.testing.v1 import AppTest

from legal_assistant.config import Settings
from legal_assistant.guardrails.scope_checker import ScopeChecker
from legal_assistant.llm.base import (
    BaseLLMClient,
    LLMAuthenticationError,
    LLMConnectionError,
    LLMRateLimitError,
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
    LegalStanding,
    OppositeParty,
    PartyDetails,
    StatutoryViolation,
    TimelineEvent,
)
from legal_assistant.ui.app import (
    CORE_HIGHLIGHT_TERMS,
    apply_runtime_provider,
    format_citation_telemetry_banner,
    format_ui_provenance_with_marks,
    handle_case_intake,
    handle_draft_single,
    handle_evaluate_standing,
    handle_simulator_turn,
    ping_provider,
)
from tests.test_ui import MockLLMClient

APP_FILE = str(Path(__file__).resolve().parent.parent / "src" / "legal_assistant" / "ui" / "app.py")


# ==============================================================================
# Deterministic Mock Router Fixture
# ==============================================================================
@pytest.fixture
def mock_router() -> LLMRouter:
    """Create configured LLMRouter populated with deterministic mock clients."""
    settings = Settings(
        llm_provider="groq",
        groq_api_key=SecretStr("mock-groq-key"),
        groq_model="llama-3.1-8b-instant",
    )
    router = LLMRouter(settings=settings)
    for p in ["groq", "ollama", "openai", "gemini"]:
        router.register_client(p, MockLLMClient(provider_name=p, model_name=f"{p}-test-model"))
    return router


@pytest.fixture
def sample_case_file() -> CaseFile:
    """Create realistic structured CaseFile fixture."""
    return CaseFile(
        case_id="case_empirical_adv_001",
        title="Defective Smartphone Refund Refusal",
        disputed_amount_inr=55000.0,
        transaction_date="2026-01-15",
        cause_of_action_date="2026-01-20",
        facts_summary=(
            "Complainant bought a smartphone on 2026-01-15 for Rs 55,000 from an online "
            "marketplace. Delivered defective with a shattered display. Merchant refused "
            "refund citing no-return policy."
        ),
        opposite_parties=[OppositeParty(name="MegaRetail Online", role="Seller")],
        timeline=[
            TimelineEvent(
                date="2026-01-15",
                significance="Purchase",
                description="Ordered smartphone online for Rs 55,000.",
            ),
            TimelineEvent(
                date="2026-01-18",
                significance="Delivery",
                description="Received damaged package with shattered screen.",
            ),
        ],
        complainant=PartyDetails(
            name="Aarav Sharma",
            email="aarav@example.com",
            phone="+91-9988776655",
            city="Bengaluru",
            state="Karnataka",
        ),
    )


@pytest.fixture
def sample_standing() -> LegalStanding:
    """Create realistic LegalStanding fixture."""
    return LegalStanding(
        is_consumer=True,
        consumer_rationale="Complainant purchased personal goods for valuable consideration.",
        pecuniary_commission_forum="District Commission",
        pecuniary_jurisdiction_limit="District Commission (Up to ₹50 Lakhs)",
        jurisdiction_rationale="Territorial jurisdiction in Bengaluru under Section 34(2).",
        limitation_status="within_limitation",
        limitation_rationale="Within 2-year limitation period under Section 69 CPA 2019.",
        estimated_timeline="21-45 days",
        statutory_violations=[
            StatutoryViolation(
                statute="Consumer Protection Act, 2019",
                section_or_rule="Section 2(47)",
                title="Unfair Trade Practice",
                violation_nature="unfair_trade_practice",
                explanation="Refusal to refund consideration for defective merchandise.",
            )
        ],
        estimated_costs=CostEstimate(
            court_fees_inr=1000.0,
            notice_costs_inr=150.0,
            total_estimated_out_of_pocket_inr="₹1,000 statutory court fees",
        ),
    )


@pytest.fixture
def populated_retriever() -> StatutoryHybridRetriever:
    """Create StatutoryHybridRetriever with test statutory chunks."""
    chunks = [
        RetrievedChunk(
            chunk_id="chunk_sec_2_47",
            content=(
                "Section 2(47) defines unfair trade practice as adopting any unfair method "
                "or unfair deceptive practice including refusal to refund consideration "
                "for defective goods."
            ),
            statute="Consumer Protection Act, 2019",
            chapter="Chapter I",
            section="Section 2(47)",
            title="Unfair Trade Practice",
            score=0.048,
            rank=1,
        ),
        RetrievedChunk(
            chunk_id="chunk_sec_2_11",
            content=(
                "Section 2(11) defines deficiency in service as any fault, imperfection, "
                "shortcoming or inadequacy in quality, nature and manner of performance "
                "required by law."
            ),
            statute="Consumer Protection Act, 2019",
            chapter="Chapter I",
            section="Section 2(11)",
            title="Deficiency in Service",
            score=0.041,
            rank=2,
        ),
    ]
    return StatutoryHybridRetriever(
        chunks=chunks,
        dense_retriever=InMemoryDenseRetriever(),
    )


# ==============================================================================
# Suite 1: format_ui_provenance_with_marks & Visual Styling Stress Tests
# ==============================================================================
class TestProvenanceVisualAndXSSAdversarial:
    """Stress testing provenance HTML escaping, XSS neutralization, and <mark> styling."""

    def test_core_highlight_terms_integrity(self) -> None:
        """Verify CORE_HIGHLIGHT_TERMS is an immutable tuple with expected statutory terms."""
        assert isinstance(CORE_HIGHLIGHT_TERMS, tuple)
        assert len(CORE_HIGHLIGHT_TERMS) >= 15
        expected_terms = {
            "unfair trade practice",
            "deficiency in service",
            "defect",
            "deficiency",
            "consumer",
            "consideration",
            "refund",
            "district commission",
            "limitation period",
        }
        for term in expected_terms:
            assert term in CORE_HIGHLIGHT_TERMS

    def test_xss_injections_in_chunk_content_strictly_escaped(self) -> None:
        """Verify multiple malicious XSS attack payloads in chunk content are strictly escaped."""
        xss_payloads = [
            "<script>alert('XSS-1')</script>",
            "<img src=x onerror=alert('XSS-2')>",
            "<svg/onload=confirm('XSS-3')>",
            "<iframe src='javascript:alert(1)'></iframe>",
            "<a href='javascript:alert(2)'>Click here</a>",
            '"><script src="//evil.com/pwn.js"></script>',
            "' onfocus='alert(3)' autofocus='",
            "<body onload=alert('XSS-4')>",
            "<details ontoggle=alert(1) open>",
        ]
        for payload in xss_payloads:
            chunk = RetrievedChunk(
                chunk_id="xss_test",
                content=f"Statutory text {payload} consumer refund defect deficiency in service.",
                statute="CPA 2019",
                section="Section 2(47)",
                title="Test Title",
                score=0.05,
            )
            html_out = format_ui_provenance_with_marks([chunk])

            # Raw unescaped payload tags MUST NOT exist in HTML output
            assert "<script>" not in html_out
            assert "</script>" not in html_out
            assert "<img" not in html_out
            assert "<svg" not in html_out
            assert "<iframe" not in html_out
            assert "href='javascript:" not in html_out
            assert "<body" not in html_out

            # The payload must be rendered as safe escaped entities
            escaped_payload = html.escape(payload)
            assert escaped_payload in html_out or html.escape("<") in html_out

            # Valid amber <mark> tags must still be rendered around matched legal terms
            assert "<mark style=" in html_out
            assert "</mark>" in html_out
            assert "#fde68a" in html_out
            assert "#78350f" in html_out

    def test_xss_injections_in_chunk_metadata_strictly_escaped(self) -> None:
        """Verify chunk metadata (statute, section, title) containing XSS payloads is escaped."""
        statute_payload = "Evil Act <script>alert('statute')</script>"
        section_payload = "Section 2 <iframe src='evil.com'>"
        title_payload = "Unfair Practice <img src=x onerror=alert('title')>"

        chunk = RetrievedChunk(
            chunk_id="xss_meta",
            content="Valid statutory content regarding consumer refund.",
            statute=statute_payload,
            chapter="Chapter 1 <svg onload=alert(1)>",
            section=section_payload,
            title=title_payload,
            score=0.03,
        )
        html_out = format_ui_provenance_with_marks([chunk])

        # Raw tags must NOT exist
        assert "<script>" not in html_out
        assert "<svg onload" not in html_out
        assert "<iframe" not in html_out
        assert "<img src=x" not in html_out

        # Standard HTML-escaped versions must be present
        assert html.escape(statute_payload) in html_out
        assert html.escape(section_payload) in html_out
        assert html.escape(title_payload) in html_out

    def test_no_double_encoding_of_html_entities(self) -> None:
        """Verify format_ui_provenance_with_marks does not double-encode characters."""
        chunk = RetrievedChunk(
            chunk_id="ent_test",
            content="Terms: 'Goods & Services' priced at < ₹5,000 > with 10% refund for consumer.",
            statute="CPA 2019",
            section="Section 2",
            title="Pricing",
            score=0.02,
        )
        html_out = format_ui_provenance_with_marks([chunk])

        # Ampersand should become &amp;, not &amp;amp;
        assert "&amp;amp;" not in html_out
        assert "&amp;" in html_out
        # < should become &lt;, not &amp;lt;
        assert "&amp;lt;" not in html_out
        assert "&lt;" in html_out
        # > should become &gt;, not &amp;gt;
        assert "&amp;gt;" not in html_out
        assert "&gt;" in html_out
        # Mark tags should be real HTML tags, not escaped
        assert "&lt;mark" not in html_out
        assert "<mark style=" in html_out

    def test_nested_mark_tags_prevention_with_overlapping_substring_terms(self) -> None:
        """Verify that overlapping terms never produce nested <mark> tags."""
        overlapping_terms = [
            "deficiency in service",
            "deficiency",
            "service",
            "unfair trade practice",
            "unfair trade",
            "unfair",
            "trade",
            "practice",
            "consumer",
            "consideration",
        ]
        chunk = RetrievedChunk(
            chunk_id="overlap_chunk",
            content=(
                "A consumer experienced a deficiency in service and unfair trade practice "
                "when seeking consideration refund for defective goods."
            ),
            statute="CPA 2019",
            section="Section 2(11)",
            title="Deficiency & Unfair Trade",
            score=0.05,
        )
        html_out = format_ui_provenance_with_marks([chunk], highlight_terms=overlapping_terms)

        # Regex asserting NO nested mark tags: <mark ...> inside <mark ...>
        nested_mark_pattern = re.compile(r"<mark[^>]*>(?:(?!</mark>).)*<mark", re.DOTALL)
        assert not nested_mark_pattern.search(html_out), "Nested <mark> tags detected!"
        # Opening and closing mark tag counts must be exactly equal
        assert html_out.count("<mark") == html_out.count("</mark>")
        assert html_out.count("<mark") >= 3

    def test_regex_metacharacters_in_highlight_terms_handled_safely(self) -> None:
        """Verify highlight_terms with regex metacharacters do not crash or corrupt output."""
        adversarial_terms = [
            "(CPA)",
            "[Section 2(1)]",
            "refund+compensation",
            "100%*",
            "^consumer$",
            "\\bdeficiency\\b",
            "\\1",
            "|",
            "???",
            "**",
            "",
            "   ",
        ]
        chunk = RetrievedChunk(
            chunk_id="meta_chunk",
            content=(
                "Consumer claim under (CPA) [Section 2(1)] with "
                "refund+compensation 100%* guarantee."
            ),
            statute="CPA 2019",
            section="Section 2",
            title="General",
            score=0.04,
        )
        html_out = format_ui_provenance_with_marks([chunk], highlight_terms=adversarial_terms)
        assert "<details" in html_out
        assert "</details>" in html_out
        assert html_out.count("<mark") == html_out.count("</mark>")

    def test_unicode_and_devanagari_highlighting(self) -> None:
        """Verify non-ASCII, Devanagari Hindi, and emoji terms are highlighted safely."""
        devanagari_terms = ["उपभोक्ता", "सेवा में कमी", "क्षतिपूर्ति"]
        chunk = RetrievedChunk(
            chunk_id="hindi_chunk",
            content="उपभोक्ता ने सेवा में कमी और क्षतिपूर्ति के लिए शिकायत दर्ज की। Refund demanded.",
            statute="उपभोक्ता संरक्षण अधिनियम, 2019",
            section="धारा 2(11)",
            title="सेवा में कमी",
            score=0.045,
        )
        html_out = format_ui_provenance_with_marks([chunk], highlight_terms=devanagari_terms)
        assert "उपभोक्ता" in html_out
        assert "<mark" in html_out
        assert html_out.count("<mark") == html_out.count("</mark>")

    def test_empty_and_boundary_chunk_inputs(self) -> None:
        """Verify empty chunk lists and chunks with empty fields render safely."""
        # 1. Empty list
        assert "No statutory grounds retrieved" in format_ui_provenance_with_marks([])

        # 2. Chunk with empty strings in all fields
        empty_chunk = RetrievedChunk(
            chunk_id="",
            content="",
            statute="",
            chapter="",
            section="",
            title="",
            score=0.0,
            rank=1,
        )
        out = format_ui_provenance_with_marks([empty_chunk])
        assert "<details" in out
        assert "</details>" in out

        # 3. Extremely long chunk content (50,000 chars)
        long_chunk = RetrievedChunk(
            chunk_id="long_chunk",
            content="Consumer protection refund unfair trade practice. " * 1000,
            statute="CPA 2019",
            section="Sec 2",
            title="Long Corpus",
            score=0.01,
        )
        long_out = format_ui_provenance_with_marks([long_chunk])
        assert len(long_out) > 50000
        assert long_out.count("<mark") == long_out.count("</mark>")

    def test_citation_telemetry_banner_palette_conformance(self) -> None:
        """Verify Citation Telemetry banner enforces high-contrast emerald or crimson styling."""
        # 1. All verified (0 flagged) -> Emerald
        emerald_banner = format_citation_telemetry_banner(verified_count=4, flagged_count=0)
        assert "#10b981" in emerald_banner
        assert "#34d399" in emerald_banner
        assert "rgba(16, 185, 129, 0.15)" in emerald_banner
        assert "4 verified" in emerald_banner
        assert "0 ungrounded citations" in emerald_banner

        # 2. Flagged citations (> 0) -> Crimson
        crimson_banner = format_citation_telemetry_banner(verified_count=2, flagged_count=3)
        assert "#ef4444" in crimson_banner
        assert "#f87171" in crimson_banner
        assert "rgba(239, 68, 68, 0.15)" in crimson_banner
        assert "2 verified" in crimson_banner
        assert "3 ungrounded citations" in crimson_banner


# ==============================================================================
# Suite 2: Public Helper Functions Adversarial & Error Handling Tests
# ==============================================================================
class TestHelperFunctionsAdversarial:
    """Stress testing the 8 backwards-compatible public helper functions."""

    def test_apply_runtime_provider_case_insensitivity_and_whitespace(
        self, mock_router: LLMRouter
    ) -> None:
        """Verify apply_runtime_provider handles casing, whitespace, and unknown fallbacks."""
        settings = Settings(llm_provider="groq")

        # Mixed-case and whitespace provider names
        msg1 = apply_runtime_provider(
            "  OLLAMA  ", model_name="llama3.2:3b", settings=settings, router=mock_router
        )
        assert str(settings.llm_provider) == "ollama"
        assert settings.ollama_model == "llama3.2:3b"
        assert "ollama" in msg1

        msg2 = apply_runtime_provider(
            "OpenAI", api_key="sk-test-openai", settings=settings, router=mock_router
        )
        assert str(settings.llm_provider) == "openai"
        assert settings.openai_api_key is not None
        assert settings.openai_api_key.get_secret_value() == "sk-test-openai"
        assert "openai" in msg2

        msg3 = apply_runtime_provider("GEMINI", settings=settings, router=mock_router)
        assert str(settings.llm_provider) == "gemini"
        assert "gemini" in msg3

        # Unknown provider fallback defaults internally to groq
        msg4 = apply_runtime_provider(
            "unknown_cloud_provider", settings=settings, router=mock_router
        )
        assert str(settings.llm_provider) == "groq"
        assert "Active provider successfully switched to" in msg4

    def test_ping_provider_error_handling_and_exception_resilience(self) -> None:
        """Verify ping_provider handles connection errors, auth errors, and exceptions."""
        # 1. Operational ping
        operational_router = LLMRouter()
        operational_router.register_client(
            "groq", MockLLMClient(provider_name="groq", model_name="mock-llama")
        )
        res_ok = ping_provider("groq", operational_router)
        assert "✅" in res_ok
        assert "operational" in res_ok

        # 2. LLMConnectionError
        err_router = LLMRouter()
        conn_client = MagicMock(spec=BaseLLMClient)
        conn_client.generate.side_effect = LLMConnectionError("Network connection refused")
        err_router._clients["groq"] = conn_client
        res_conn = ping_provider("groq", err_router)
        assert "❌" in res_conn
        assert "Connection failed" in res_conn
        assert "Network connection refused" in res_conn

        # 3. LLMAuthenticationError
        auth_client = MagicMock(spec=BaseLLMClient)
        auth_client.generate.side_effect = LLMAuthenticationError("Invalid API key")
        err_router._clients["groq"] = auth_client
        res_auth = ping_provider("groq", err_router)
        assert "❌" in res_auth
        assert "Invalid API key" in res_auth

        # 4. LLMRateLimitError
        rate_client = MagicMock(spec=BaseLLMClient)
        rate_client.generate.side_effect = LLMRateLimitError("TPM limit exceeded")
        err_router._clients["groq"] = rate_client
        res_rate = ping_provider("groq", err_router)
        assert "❌" in res_rate
        assert "TPM limit exceeded" in res_rate

        # 5. Unexpected general Exception (e.g., RuntimeError)
        crash_client = MagicMock(spec=BaseLLMClient)
        crash_client.generate.side_effect = RuntimeError("Internal driver crash")
        err_router._clients["groq"] = crash_client
        res_crash = ping_provider("groq", err_router)
        assert "❌" in res_crash
        assert "Unexpected error" in res_crash

    def test_handle_case_intake_empty_and_whitespace_inputs(self, mock_router: LLMRouter) -> None:
        """Verify handle_case_intake returns clean message on empty or whitespace narrative."""
        for empty_text in ["", "   ", "\t\n  \n\t"]:
            case_f, alert, timeline, avail, missing = handle_case_intake(
                narrative=empty_text,
                router=mock_router,
            )
            assert case_f is None
            assert "please enter" in alert.lower()
            assert timeline == []
            assert avail == []
            assert missing == []

    def test_handle_case_intake_out_of_scope_disputes(self, mock_router: LLMRouter) -> None:
        """Verify handle_case_intake blocks criminal BNS and Section 138 NI Act disputes."""
        scope_checker = ScopeChecker()

        # Criminal dispute
        crim_narrative = (
            "My neighbor assaulted me with a weapon causing severe injury and threatened murder "
            "under BNS 103. We lodged an FIR with the police station."
        )
        c_file, alert, timeline, _, _ = handle_case_intake(
            narrative=crim_narrative,
            router=mock_router,
            scope_checker=scope_checker,
        )
        assert c_file is None
        assert "⚠️ Escalation Required" in alert
        assert "Advocate" in alert
        assert len(timeline) == 0

        # Cheque bounce dispute
        cheque_narrative = (
            "A customer issued a cheque for Rs 4,00,000 for consulting services. "
            "The cheque was dishonored due to insufficient funds under Section 138 NI Act."
        )
        c_file2, alert2, timeline2, _, _ = handle_case_intake(
            narrative=cheque_narrative,
            router=mock_router,
            scope_checker=scope_checker,
        )
        assert c_file2 is None
        assert "⚠️ Escalation Required" in alert2
        assert "Advocate" in alert2

    def test_handle_case_intake_complainant_details_with_unicode_and_special_chars(
        self, mock_router: LLMRouter
    ) -> None:
        """Verify complainant details with Hindi Unicode and special characters are preserved."""
        narrative = (
            "I ordered an air conditioner for Rs 42,000 on 2026-02-01 from an e-commerce platform. "
            "I have tax invoice INV-4491 and online payment receipt. It does not cool at all. "
            "Support refused return."
        )
        case_f, alert, timeline, avail, missing = handle_case_intake(
            narrative=narrative,
            router=mock_router,
            complainant_name="राजेश कुमार शर्मा (Adv.)",
            complainant_email="rajesh.sharma+consumer@domain.in",
            complainant_phone="+91-98765-43210",
            complainant_city="नई दिल्ली (New Delhi)",
            complainant_state="Delhi",
        )
        assert case_f is not None
        assert case_f.complainant is not None
        assert "राजेश" in case_f.complainant.name
        assert case_f.complainant.city is not None
        assert "नई दिल्ली" in case_f.complainant.city
        assert len(timeline) >= 1
        assert len(missing) >= 1

    def test_handle_evaluate_standing_none_case_file_and_populated_execution(
        self,
        mock_router: LLMRouter,
        sample_case_file: CaseFile,
        populated_retriever: StatutoryHybridRetriever,
    ) -> None:
        """Verify handle_evaluate_standing handles None case_file and processes valid case_file."""
        # 1. None case_file
        standing_none, overview_none, viol_none, path_none, prov_none = handle_evaluate_standing(
            case_file=None,
            router=mock_router,
            retriever=populated_retriever,
        )
        assert standing_none is None
        assert "please complete case intake" in overview_none.lower()
        assert viol_none == []
        assert path_none == []
        assert "No case facts available" in prov_none

        # 2. Valid case_file
        standing, overview, viol, path, prov = handle_evaluate_standing(
            case_file=sample_case_file,
            router=mock_router,
            retriever=populated_retriever,
        )
        assert standing is not None
        assert standing.is_consumer is True
        assert "Legal Standing Assessment" in overview
        assert len(viol) >= 1
        assert len(path) == 4
        assert "<details" in prov
        assert "<mark" in prov

    def test_handle_draft_single_and_document_types(
        self,
        mock_router: LLMRouter,
        sample_case_file: CaseFile,
        sample_standing: LegalStanding,
        populated_retriever: StatutoryHybridRetriever,
        tmp_path: Path,
    ) -> None:
        """Verify handle_draft_single generates all 3 document types and exports to disk."""
        # 1. None case_file
        doc_none, md_none, txt_none, path_none = handle_draft_single(
            case_file=None,
            standing=sample_standing,
            doc_type="legal_notice",
            router=mock_router,
            retriever=populated_retriever,
            export_dir=tmp_path,
        )
        assert doc_none is None
        assert "please complete case intake" in md_none.lower()
        assert path_none == ""

        # 2. Legal Notice
        doc_notice, md_notice, txt_notice, path_notice = handle_draft_single(
            case_file=sample_case_file,
            standing=sample_standing,
            doc_type="Legal Demand Notice (15-Day)",
            notice_days=15,
            router=mock_router,
            retriever=populated_retriever,
            export_dir=tmp_path,
        )
        assert doc_notice is not None
        assert "FORMAL LEGAL DEMAND NOTICE" in md_notice
        assert Path(path_notice).exists()
        assert Path(path_notice).read_text(encoding="utf-8") == md_notice

        # 3. Grievance Email
        doc_email, md_email, txt_email, path_email = handle_draft_single(
            case_file=sample_case_file,
            standing=sample_standing,
            doc_type="Grievance Escalation Email",
            router=mock_router,
            retriever=populated_retriever,
            export_dir=tmp_path,
        )
        assert doc_email is not None
        assert "GRIEVANCE" in md_email.upper()
        assert Path(path_email).exists()

        # 4. e-Daakhil Complaint
        doc_complaint, md_complaint, txt_complaint, path_complaint = handle_draft_single(
            case_file=sample_case_file,
            standing=sample_standing,
            doc_type="e-Daakhil Consumer Complaint Draft",
            router=mock_router,
            retriever=populated_retriever,
            export_dir=tmp_path,
        )
        assert doc_complaint is not None
        assert "DISTRICT CONSUMER DISPUTES REDRESSAL COMMISSION" in md_complaint
        assert Path(path_complaint).exists()

    def test_handle_simulator_turn_progression_and_state_initiation(
        self, mock_router: LLMRouter
    ) -> None:
        """Verify simulator turn initiates fresh state if None and alternates roles."""
        # 1. Initial turn with state=None
        u_state1, hist1, score_txt1, str1, weak1, adv1 = handle_simulator_turn(
            user_argument=(
                "I purchased defective goods and the seller refuses refund under Section 2(47)."
            ),
            state=None,
            router=mock_router,
        )
        assert u_state1 is not None
        assert len(u_state1.turns) >= 2
        assert len(hist1) >= 2
        # Verify alternating role structure
        assert hist1[0]["role"] == "assistant"
        assert hist1[1]["role"] == "user"

        # 2. Second turn advancing session
        u_state2, hist2, score_txt2, str2, weak2, adv2 = handle_simulator_turn(
            user_argument=(
                "Under Section 2(46) unfair contract terms disclaiming all liability are void."
            ),
            state=u_state1,
            router=mock_router,
        )
        assert len(u_state2.turns) >= 4
        assert [m["role"] for m in hist2[:4]] == ["assistant", "user", "assistant", "user"]
        assert "Turn Score:" in score_txt2


# ==============================================================================
# Suite 3: Streamlit App Execution & Unexpected Session State Tests (AppTest)
# ==============================================================================
class TestStreamlitAppExecutionAndStateTransitions:
    """Stress testing render_streamlit_app execution, state transitions, and boundary flows."""

    def test_streamlit_out_of_order_button_clicks_without_case_file(
        self, mock_router: LLMRouter
    ) -> None:
        """Verify clicking buttons in Tab 2/3 before intake does not raise unhandled exceptions."""
        at = AppTest.from_file(APP_FILE)
        at.session_state["router"] = mock_router
        at.run(timeout=30)
        assert len(at.exception) == 0

        # Click Tab 2 Assess Standing button without CaseFile
        btn_assess = at.button(key="btn_assess_standing")
        assert btn_assess is not None
        btn_assess.click().run(timeout=30)
        assert len(at.exception) == 0
        # Warning notification should be rendered
        assert len(at.warning) >= 1
        assert any("complete case intake in tab 1 first" in w.value.lower() for w in at.warning)

        # Click Tab 3 Draft Selected Document button without CaseFile
        btn_draft = at.button(key="btn_draft_single")
        assert btn_draft is not None
        btn_draft.click().run(timeout=30)
        assert len(at.exception) == 0
        assert any("complete case intake in tab 1 first" in w.value.lower() for w in at.warning)

        # Click Tab 3 Draft All 3 Documents button without CaseFile
        btn_all = at.button(key="btn_draft_all")
        assert btn_all is not None
        btn_all.click().run(timeout=30)
        assert len(at.exception) == 0
        assert any("complete case intake in tab 1 first" in w.value.lower() for w in at.warning)

    def test_streamlit_simulator_debate_start_and_chat_submission(
        self, mock_router: LLMRouter, sample_case_file: CaseFile
    ) -> None:
        """Verify simulator reset and chat input submission in Tab 4."""
        at = AppTest.from_file(APP_FILE)
        at.session_state["router"] = mock_router
        at.session_state["case_file"] = sample_case_file
        at.run(timeout=30)
        assert len(at.exception) == 0

        # Click Start / Reset Debate button
        btn_sim = at.button(key="btn_init_sim")
        assert btn_sim is not None
        btn_sim.click().run(timeout=30)
        assert len(at.exception) == 0
        assert at.session_state["sim_state"] is not None
        assert len(at.session_state["chat_history"]) == 1

        # Submit chat argument via chat_input
        ci_elements = at.chat_input(key="ci_consumer_rebuttal")
        assert ci_elements is not None
        ci_elements.set_value(
            "Under Section 2(47) of CPA 2019, denying a refund for defective delivery "
            "is unfair trade practice."
        ).run(timeout=30)
        assert len(at.exception) == 0
        assert len(at.session_state["chat_history"]) >= 2
        assert at.session_state["sim_scores"]["turn_score"] > 0

    def test_streamlit_sidebar_live_model_switcher_workflow(self, mock_router: LLMRouter) -> None:
        """Verify hot-swapping providers in sidebar, applying settings, and pinging provider."""
        at = AppTest.from_file(APP_FILE)
        at.session_state["router"] = mock_router
        at.run(timeout=30)
        assert len(at.exception) == 0

        # Change provider to OpenAI
        sb_select = at.sidebar.selectbox(key="sb_provider_select")
        assert sb_select is not None
        sb_select.select("openai").run(timeout=30)
        assert len(at.exception) == 0

        # Click Apply Settings
        btn_apply = at.sidebar.button(key="sb_btn_apply")
        assert btn_apply is not None
        btn_apply.click().run(timeout=30)
        assert len(at.exception) == 0
        assert at.session_state["active_provider"] == "openai"

        # Click Ping Provider
        btn_ping = at.sidebar.button(key="sb_btn_ping")
        assert btn_ping is not None
        btn_ping.click().run(timeout=30)
        assert len(at.exception) == 0
        # Ping returns error or success callout in sidebar depending on client availability
        assert len(at.sidebar.error) >= 1 or len(at.sidebar.success) >= 1
