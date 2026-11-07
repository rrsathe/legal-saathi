"""Empirical Challenger Stress-Testing Suite for Workflows 2, 3, 4, 8, and 9.

Adversarial verification suite covering:
1. Workflow 2 (Jurisdiction Analysis):
   - 2021 Pecuniary boundaries (District vs State vs National Commission)
   - e-Daakhil court fee calculations across all 18 fee slabs
   - Section 69 2-year limitation period math with boundary dates, leap years, and urgency
2. Workflow 3 (Statutory Provenance):
   - format_ui_provenance_with_marks against XSS vectors (<script>, <svg>, <iframe>, <img>)
   - Overlapping and regex-special highlight terms
   - CitationVerifier against fabricated sections, repealed CPA 1986 citations, and fake case laws
3. Workflow 4 (Evidence Audit):
   - CaseBuilder.audit_missing_evidence edge cases: missing invoice vs missing unboxing video
     vs missing service center job sheet vs fully documented case
4. Workflow 8 (Model Switching):
   - Runtime provider switching across Groq, Ollama, OpenAI, Gemini
   - Cache invalidation and parameter updates
   - Multi-provider fallback chain under simulated 429 rate limit and 500 errors
5. Workflow 9 (RAG Retrieval):
   - StatutoryHybridRetriever with ChromaDB 1.5.9 backend (ChromaDenseRetriever)
   - BM25 and Dense RRF score fusion
   - Exact section lookup (Section 2(47))
   - Retrieval confidence gating and abstention on out-of-domain queries
   - LegalTokenizer statutory, section subclause, and Indian currency notation
"""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from unittest.mock import MagicMock

import pytest
from pydantic import SecretStr

from legal_assistant.config import Settings
from legal_assistant.guardrails.verifier import (
    CitationVerifier,
    RetrievalConfidenceGate,
)
from legal_assistant.llm.base import (
    LLMAllProvidersFailedError,
    LLMAuthenticationError,
    LLMConnectionError,
    LLMRateLimitError,
    LLMResponse,
    TokenUsage,
)
from legal_assistant.llm.router import LLMRouter
from legal_assistant.rag.hybrid_retriever import (
    ChromaDenseRetriever,
    LegalTokenizer,
    RetrievedChunk,
    StatutoryHybridRetriever,
)
from legal_assistant.schemas import (
    CaseFile,
    EvidenceItem,
    OppositeParty,
    PartyDetails,
    PecuniaryForum,
    calculate_edaakhil_fee,
    check_limitation_status,
    determine_pecuniary_forum,
)
from legal_assistant.ui.app import (
    apply_runtime_provider,
    format_ui_provenance_with_marks,
    ping_provider,
)
from legal_assistant.workflows.case_builder import CaseBuilder

# ==============================================================================
# 1. WORKFLOW 2: JURISDICTION ANALYSIS & PECUNIARY/LIMITATION BOUNDARIES
# ==============================================================================


class TestWorkflow2JurisdictionEmpirical:
    """Empirical verification of 2021 Pecuniary Rules, e-Daakhil slabs, and Section 69."""

    @pytest.mark.parametrize(
        ("amount", "expected_forum", "expected_rule"),
        [
            # District Commission boundaries: <= ₹50 Lakhs (₹5,000,000)
            (0.0, PecuniaryForum.DISTRICT_COMMISSION.value, "Rule 3"),
            (1.0, PecuniaryForum.DISTRICT_COMMISSION.value, "Rule 3"),
            (100_000.0, PecuniaryForum.DISTRICT_COMMISSION.value, "Rule 3"),
            (4_999_999.99, PecuniaryForum.DISTRICT_COMMISSION.value, "Rule 3"),
            (5_000_000.0, PecuniaryForum.DISTRICT_COMMISSION.value, "Rule 3"),
            # State Commission boundaries: > ₹50 Lakhs and <= ₹2 Crores (₹20,000,000)
            (5_000_000.01, PecuniaryForum.STATE_COMMISSION.value, "Rule 4"),
            (5_000_001.0, PecuniaryForum.STATE_COMMISSION.value, "Rule 4"),
            (10_000_000.0, PecuniaryForum.STATE_COMMISSION.value, "Rule 4"),
            (19_999_999.99, PecuniaryForum.STATE_COMMISSION.value, "Rule 4"),
            (20_000_000.0, PecuniaryForum.STATE_COMMISSION.value, "Rule 4"),
            # National Commission boundaries: > ₹2 Crores (> ₹20,000,000)
            (20_000_000.01, PecuniaryForum.NATIONAL_COMMISSION.value, "Rule 5"),
            (20_000_001.0, PecuniaryForum.NATIONAL_COMMISSION.value, "Rule 5"),
            (50_000_000.0, PecuniaryForum.NATIONAL_COMMISSION.value, "Rule 5"),
            (100_000_000.0, PecuniaryForum.NATIONAL_COMMISSION.value, "Rule 5"),
            (1_000_000_000.0, PecuniaryForum.NATIONAL_COMMISSION.value, "Rule 5"),
        ],
    )
    def test_pecuniary_boundaries_2021_rules(
        self, amount: float, expected_forum: str, expected_rule: str
    ) -> None:
        """Challenge: Exact pecuniary jurisdiction thresholds under 2021 Rules."""
        forum, rationale = determine_pecuniary_forum(amount)
        assert forum == expected_forum
        assert expected_rule in rationale
        assert "2021" in rationale

    @pytest.mark.parametrize(
        ("amount", "expected_fee"),
        [
            # Slabs 1-18 testing full schedule transitions
            (0.0, 0),
            (250_000.0, 0),
            (500_000.0, 0),
            (500_000.50, 200),
            (500_001.0, 200),
            (1_000_000.0, 200),
            (1_000_001.0, 400),
            (2_000_000.0, 400),
            (2_000_001.0, 1000),
            (5_000_000.0, 1000),
            (5_000_001.0, 2000),
            (10_000_000.0, 2000),
            (10_000_001.0, 2500),
            (20_000_000.0, 2500),
            (20_000_001.0, 3000),
            (40_000_000.0, 3000),
            (40_000_001.0, 4000),
            (60_000_000.0, 4000),
            (60_000_001.0, 5000),
            (80_000_000.0, 5000),
            (80_000_001.0, 6000),
            (100_000_000.0, 6000),
            (100_000_001.0, 7500),
            (500_000_000.0, 7500),
        ],
    )
    def test_edaakhil_court_fee_all_slabs(self, amount: float, expected_fee: int) -> None:
        """Challenge: e-Daakhil court fee calculations across all statutory fee slabs."""
        actual_fee = calculate_edaakhil_fee(amount)
        assert actual_fee == expected_fee

    def test_section_69_limitation_math_and_urgency_tiers(self) -> None:
        """Challenge: Section 69 730-day limitation math, countdown, and urgent triage."""
        # Tier 1: Well within limitation (<= 600 days)
        is_in, rem, rat = check_limitation_status(0)
        assert is_in is True
        assert rem == 730
        assert "well within" in rat.lower()

        is_in, rem, rat = check_limitation_status(600)
        assert is_in is True
        assert rem == 130
        assert "well within" in rat.lower()

        # Tier 2: Urgent expiring soon (601 to 730 days)
        is_in, rem, rat = check_limitation_status(601)
        assert is_in is True
        assert rem == 129
        assert "URGENT" in rat
        assert "expiring soon" in rat.lower()

        is_in, rem, rat = check_limitation_status(729)
        assert is_in is True
        assert rem == 1
        assert "URGENT" in rat

        # Exact boundary: day 730 (0 days remaining)
        is_in, rem, rat = check_limitation_status(730)
        assert is_in is True
        assert rem == 0
        assert "URGENT" in rat

        # Tier 3: Limitation expired (> 730 days)
        is_in, rem, rat = check_limitation_status(731)
        assert is_in is False
        assert rem == -1
        assert "expired" in rat.lower()
        assert "condonation of delay" in rat.lower()
        assert "Section 69(2)" in rat

        is_in, rem, rat = check_limitation_status(900)
        assert is_in is False
        assert rem == -170
        assert "exceeded by 170 days" in rat

    def test_section_69_calendar_date_and_leap_year(self) -> None:
        """Challenge: Section 69 date math with ISO strings, leap year, and explicit filing date."""
        # Test 1: Leap year 2024 (2024-01-01 to 2026-01-01 is 731 calendar days)
        coa = "2024-01-01"
        filing_on_day_730 = (date.fromisoformat(coa) + timedelta(days=730)).isoformat()
        filing_on_day_731 = (date.fromisoformat(coa) + timedelta(days=731)).isoformat()

        is_in_730, rem_730, _ = check_limitation_status(coa, filing_on_day_730)
        assert is_in_730 is True
        assert rem_730 == 0

        is_in_731, rem_731, rat_731 = check_limitation_status(coa, filing_on_day_731)
        assert is_in_731 is False
        assert rem_731 == -1
        assert "condonation of delay" in rat_731.lower()

        # Test 2: Datetime and date inputs
        dt_coa = datetime(2025, 1, 1, 10, 30, 0)
        dt_filing = datetime(2025, 4, 1, 15, 0, 0)
        is_in, rem, _ = check_limitation_status(dt_coa, dt_filing)
        assert is_in is True
        assert rem == 730 - 90


# ==============================================================================
# 2. WORKFLOW 3: STATUTORY PROVENANCE & XSS / CITATION VERIFICATION
# ==============================================================================


class TestWorkflow3StatutoryProvenanceEmpirical:
    """Empirical stress-testing of UI provenance rendering and CitationVerifier."""

    def test_format_ui_provenance_xss_injection(self) -> None:
        """Challenge: XSS injection vectors (<script>, <svg>, <iframe>, <img>) in chunk cards."""
        malicious_chunks = [
            RetrievedChunk(
                chunk_id="xss_1",
                statute="<script>alert('statute_xss')</script>",
                section="<svg onload=alert(1)>2(47)</svg>",
                title="<iframe src='javascript:alert(2)'>Title</iframe>",
                content="Consumer protection under <img src=x onerror=alert('content_xss')> Act.",
                score=0.035,
                rank=1,
            )
        ]

        rendered_html = format_ui_provenance_with_marks(
            chunks=malicious_chunks,
            cited_sections=["<svg onload=alert(1)>2(47)</svg>"],
            highlight_terms=["<script>alert(1)</script>", "consumer protection"],
        )

        # Confirm all HTML angle brackets from malicious payloads were escaped
        assert "<script>" not in rendered_html
        assert "</script>" not in rendered_html
        assert "<svg" not in rendered_html
        assert "<iframe" not in rendered_html
        assert "<img src=x onerror=" not in rendered_html
        assert "&lt;script&gt;" in rendered_html or "&lt;svg" in rendered_html
        # Confirm valid <mark> highlighting still operates safely
        assert "<mark" in rendered_html

    def test_format_ui_provenance_overlapping_and_regex_marks(self) -> None:
        """Challenge: Overlapping terms and regex metacharacters in highlight_terms."""
        chunks = [
            RetrievedChunk(
                chunk_id="chunk_overlap",
                statute="Consumer Protection Act, 2019",
                section="Section 2(47)",
                title="Unfair Trade Practice",
                content=(
                    "An unfair trade practice includes deceptive practice, false statement, "
                    "misleading advertisement of goods for ₹50,000 consideration "
                    "under Section 2(47)."
                ),
                score=0.042,
                rank=1,
            )
        ]

        # Terms containing overlapping phrases and regex special chars
        tricky_terms = [
            "unfair trade practice",
            "unfair",
            "trade practice",
            "Section 2(47)",
            "₹50,000",
            "(e-commerce)",
            "[*+?^$|(){}\\]",
        ]

        rendered = format_ui_provenance_with_marks(
            chunks=chunks,
            highlight_terms=tricky_terms,
        )

        assert rendered is not None
        assert "statutory-provenance-card" in rendered
        # Verify no unclosed nested mark tag corruption
        mark_opens = len(re.findall(r"<mark\b", rendered))
        mark_closes = len(re.findall(r"</mark>", rendered))
        assert mark_opens == mark_closes
        assert mark_opens > 0

    def test_citation_verifier_fabricated_sections_and_repealed_acts(self) -> None:
        """Challenge: CitationVerifier flags fabricated sections and repealed acts."""
        verifier = CitationVerifier(default_action="flag")

        # Ground truth corpus containing ONLY Section 2(7) and Section 2(47)
        ground_truth = [
            RetrievedChunk(
                chunk_id="c1",
                statute="Consumer Protection Act, 2019",
                section="Section 2(7)",
                title="Definition of Consumer",
                content="Definition of consumer who buys goods for consideration.",
                score=0.04,
                rank=1,
            ),
            RetrievedChunk(
                chunk_id="c2",
                statute="Consumer Protection Act, 2019",
                section="Section 2(47)",
                title="Unfair Trade Practice",
                content="Definition of unfair trade practice including misleading ads.",
                score=0.03,
                rank=2,
            ),
        ]

        # Adversarial LLM text with genuine, fabricated, and repealed references
        adversarial_text = (
            "Under Section 2(7) and Section 2(47), the complainant is a consumer. "
            "However, pursuant to Section 999 and Section 404 of CPA 2019, triple damages apply. "
            "Furthermore, as per the Consumer Protection Act, 1986 and CPA 1986, "
            "the opposite party is strictly liable. Refer to fake precedent "
            "Sharma v. MegaCorp Retail (2024) 5 SCC 210."
        )

        result_flag = verifier.verify_citations(adversarial_text, ground_truth, action="flag")

        # Must detect hallucination
        assert result_flag.hallucination_detected is True
        assert result_flag.is_valid is False
        assert len(result_flag.flagged_citations) >= 3

        # Fabricated sections must be flagged
        flagged_str = " ".join(result_flag.flagged_citations).lower()
        assert "999" in flagged_str
        assert "404" in flagged_str

        # Repealed act must be caught
        assert any("1986" in fc for fc in result_flag.flagged_citations)

        # Fake case law must be flagged
        assert any(
            "sharma v. megacorp" in fc.lower() or "scc" in fc.lower()
            for fc in result_flag.flagged_citations
        )

        # Genuine citations must be verified
        assert any("2(7)" in vc for vc in result_flag.verified_citations)
        assert any("2(47)" in vc for vc in result_flag.verified_citations)

        # In "strip" mode, ungrounded citations should be omitted
        result_strip = verifier.verify_citations(adversarial_text, ground_truth, action="strip")
        assert "[Citation omitted" in result_strip.cleaned_text
        assert "Section 999" not in result_strip.cleaned_text
        assert "Consumer Protection Act, 1986" not in result_strip.cleaned_text


# ==============================================================================
# 3. WORKFLOW 4: EVIDENCE AUDIT & EDGE CASES
# ==============================================================================


class TestWorkflow4EvidenceAuditEmpirical:
    """Empirical audit of missing evidence across edge cases."""

    @pytest.fixture
    def case_builder(self) -> CaseBuilder:
        return CaseBuilder(llm_router=MagicMock())

    def test_missing_critical_tax_invoice(self, case_builder: CaseBuilder) -> None:
        """Challenge: Case with payment receipt and support email but missing Tax Invoice."""
        case = CaseFile(
            case_id="case_no_invoice",
            title="Smartwatch charging failure",
            transaction_date="2024-01-01",
            disputed_amount_inr=3499.0,
            facts_summary="Purchased a smartwatch online, stopped charging within 1 week.",
            evidence_checklist=[
                EvidenceItem(
                    item_name="UPI Bank Statement",
                    is_available=True,
                    description="UPI transaction of ₹3,499 to seller account",
                ),
                EvidenceItem(
                    item_name="Customer Support Email",
                    is_available=True,
                    description="Email trail lodging grievance with helpdesk",
                ),
            ],
            complainant=PartyDetails(name="Amit Sharma"),
            opposite_parties=[OppositeParty(name="Gizmo Retail", role="Seller")],
        )

        missing = case_builder.audit_missing_evidence(case)
        missing_names = [m.item_name.lower() for m in missing]

        assert any("tax invoice" in name for name in missing_names)
        invoice_item = next(m for m in missing if "tax invoice" in m.item_name.lower())
        assert invoice_item.importance == "critical"
        assert "Section 2(7)" in invoice_item.why_needed

    def test_missing_high_importance_unboxing_video(self, case_builder: CaseBuilder) -> None:
        """Challenge: Tampered/sabun/empty box delivery missing continuous unboxing footage."""
        case = CaseFile(
            case_id="case_sabun",
            title="Smartphone delivery sabun received",
            transaction_date="2024-01-01",
            disputed_amount_inr=25000.0,
            facts_summary=(
                "Consumer ordered a smartphone worth ₹25,000, opened box "
                "and found bathing soap / sabun."
            ),
            evidence_checklist=[
                EvidenceItem(
                    item_name="Tax Invoice",
                    is_available=True,
                    description="Official tax invoice with GSTIN",
                ),
                EvidenceItem(
                    item_name="Payment Receipt",
                    is_available=True,
                    description="Credit card statement showing ₹25,000 paid",
                ),
                EvidenceItem(
                    item_name="Grievance Ticket",
                    is_available=True,
                    description="Ticket #99482 opened within 1 hour of delivery",
                ),
            ],
            complainant=PartyDetails(name="Priya Patel"),
            opposite_parties=[OppositeParty(name="FastShip Marketplace", role="Marketplace")],
        )

        missing = case_builder.audit_missing_evidence(case)
        missing_names = [m.item_name.lower() for m in missing]

        assert any("unboxing video" in name for name in missing_names)
        unboxing_item = next(m for m in missing if "unboxing video" in m.item_name.lower())
        assert unboxing_item.importance == "high"
        assert "tampering" in unboxing_item.why_needed.lower()

    def test_missing_critical_service_center_job_sheet(self, case_builder: CaseBuilder) -> None:
        """Challenge: Electronic hardware manufacturing defect missing authorized service sheet."""
        case = CaseFile(
            case_id="case_laptop_defect",
            title="Laptop defect motherboard dead",
            transaction_date="2024-01-01",
            disputed_amount_inr=65000.0,
            facts_summary=(
                "Consumer purchased a laptop, display defect and motherboard dead after 3 days."
            ),
            evidence_checklist=[
                EvidenceItem(
                    item_name="Tax Invoice with Serial Number",
                    is_available=True,
                    description="Invoice showing laptop serial number",
                ),
                EvidenceItem(
                    item_name="Credit Card Payment Slip",
                    is_available=True,
                    description="Payment proof",
                ),
                EvidenceItem(
                    item_name="Continuous Unboxing Video",
                    is_available=True,
                    description="Recorded unboxing showing sealed parcel opened",
                ),
                EvidenceItem(
                    item_name="Support Rejection Email",
                    is_available=True,
                    description="Platform refused return request",
                ),
            ],
            complainant=PartyDetails(name="Vikas Roy"),
            opposite_parties=[OppositeParty(name="PC Hub", role="Seller")],
        )

        missing = case_builder.audit_missing_evidence(case)
        missing_names = [m.item_name.lower() for m in missing]

        assert any("job sheet" in name for name in missing_names)
        sheet_item = next(m for m in missing if "job sheet" in m.item_name.lower())
        assert sheet_item.importance == "critical"
        assert "Section 2(10)" in sheet_item.why_needed

    def test_completely_documented_case_produces_zero_missing_evidence(
        self, case_builder: CaseBuilder
    ) -> None:
        """Challenge: A completely documented case must produce 0 missing evidence items."""
        case = CaseFile(
            case_id="case_perfect",
            title="Completely documented smartphone defect",
            transaction_date="2024-01-01",
            disputed_amount_inr=25000.0,
            facts_summary="Consumer bought a smartphone, received defective unit.",
            evidence_checklist=[
                EvidenceItem(
                    item_name="Tax Invoice with GSTIN",
                    is_available=True,
                    description="Invoice attached",
                ),
                EvidenceItem(
                    item_name="UPI Bank Statement",
                    is_available=True,
                    description="Transaction receipt attached",
                ),
                EvidenceItem(
                    item_name="Continuous Unboxing Video",
                    is_available=True,
                    description="Complete unboxing footage attached",
                ),
                EvidenceItem(
                    item_name="Support Rejection Email / Grievance Ticket",
                    is_available=True,
                    description="Formal denial email with ticket #441",
                ),
                EvidenceItem(
                    item_name="Authorized Service Center Job Sheet",
                    is_available=True,
                    description="Official service report confirming manufacturing defect",
                ),
            ],
            complainant=PartyDetails(name="Rohit Verma"),
            opposite_parties=[OppositeParty(name="Tech Store", role="Seller")],
        )

        missing = case_builder.audit_missing_evidence(case)
        assert len(missing) == 0


# ==============================================================================
# 4. WORKFLOW 8: MODEL SWITCHING, CACHE INVALIDATION & FALLBACK CHAIN
# ==============================================================================


class TestWorkflow8ModelSwitchingEmpirical:
    """Empirical verification of runtime provider switching, pinging, and fallback."""

    def test_apply_runtime_provider_across_all_providers(self) -> None:
        """Challenge: Switching across Groq, Ollama, OpenAI, and Gemini with cache invalidation."""
        settings = Settings()
        router = LLMRouter(settings=settings)

        # Pre-populate router client cache
        dummy_client = MagicMock()
        router._clients["groq"] = dummy_client
        router._clients["ollama"] = dummy_client
        router._clients["openai"] = dummy_client
        router._clients["gemini"] = dummy_client

        # 1. Switch to Ollama
        msg1 = apply_runtime_provider(
            provider="ollama",
            model_name="mistral:latest",
            base_url="http://192.168.1.50:11434",
            settings=settings,
            router=router,
        )
        assert str(settings.llm_provider) == "ollama"
        assert settings.ollama_model == "mistral:latest"
        assert settings.ollama_base_url == "http://192.168.1.50:11434"
        assert "ollama" not in router._clients
        assert "switched to: ollama" in msg1

        # 2. Switch to OpenAI
        msg2 = apply_runtime_provider(
            provider="openai",
            model_name="gpt-4o",
            api_key="sk-test-openai-key-12345",
            settings=settings,
            router=router,
        )
        assert str(settings.llm_provider) == "openai"
        assert settings.openai_model == "gpt-4o"
        assert settings.openai_api_key.get_secret_value() == "sk-test-openai-key-12345"
        assert "openai" not in router._clients
        assert "switched to: openai" in msg2

        # 3. Switch to Gemini
        msg3 = apply_runtime_provider(
            provider="gemini",
            model_name="gemini-2.0-flash",
            api_key="gemini-secret-test-key",
            settings=settings,
            router=router,
        )
        assert str(settings.llm_provider) == "gemini"
        assert settings.gemini_model == "gemini-2.0-flash"
        assert settings.gemini_api_key.get_secret_value() == "gemini-secret-test-key"
        assert "gemini" not in router._clients
        assert "switched to: gemini" in msg3

        # 4. Switch back to Groq
        msg4 = apply_runtime_provider(
            provider="groq",
            model_name="llama-3.3-70b-versatile",
            api_key="gsk-test-groq-key-789",
            settings=settings,
            router=router,
        )
        assert str(settings.llm_provider) == "groq"
        assert settings.groq_model == "llama-3.3-70b-versatile"
        assert settings.groq_api_key.get_secret_value() == "gsk-test-groq-key-789"
        assert "groq" not in router._clients
        assert "switched to: groq" in msg4

    def test_ping_provider_operational_and_error_handling(self) -> None:
        """Challenge: ping_provider handles success, 429 rate limit, 401 auth, and errors."""
        router = LLMRouter()

        # Case A: Operational success
        mock_success_client = MagicMock()
        mock_success_client.generate.return_value = LLMResponse(
            content="PONG",
            model="llama-3.3-70b-versatile",
            provider="groq",
            usage=TokenUsage(total_tokens=12),
        )
        router.register_client("groq", mock_success_client)

        ping_ok = ping_provider("groq", router)
        assert "✅ Provider 'groq' operational!" in ping_ok
        assert "llama-3.3-70b-versatile" in ping_ok

        # Case B: 429 Rate Limit Error
        mock_rate_limit_client = MagicMock()
        mock_rate_limit_client.generate.side_effect = LLMRateLimitError("TPM limit exceeded")
        router.register_client("groq", mock_rate_limit_client)

        ping_429 = ping_provider("groq", router)
        assert "❌ Connection failed for provider 'groq': TPM limit exceeded" in ping_429

        # Case C: 401 Authentication Error
        mock_auth_client = MagicMock()
        mock_auth_client.generate.side_effect = LLMAuthenticationError("Invalid API key")
        router.register_client("openai", mock_auth_client)

        ping_401 = ping_provider("openai", router)
        assert "❌ Connection failed for provider 'openai': Invalid API key" in ping_401

        # Case D: Network Connection Failure
        mock_conn_client = MagicMock()
        mock_conn_client.generate.side_effect = LLMConnectionError("Failed to connect to daemon")
        router.register_client("ollama", mock_conn_client)

        ping_conn = ping_provider("ollama", router)
        assert (
            "❌ Connection failed for provider 'ollama': Failed to connect to daemon" in ping_conn
        )

    def test_multi_provider_fallback_chain_under_failures(self) -> None:
        """Challenge: LLMRouter fallback advances from failing provider to working provider."""
        settings = Settings(
            llm_provider="groq",
            fallback_providers=["ollama", "openai"],
            groq_api_key=SecretStr("mock_groq_key"),
            openai_api_key=SecretStr("mock_openai_key"),
        )
        router = LLMRouter(settings=settings)

        # Provider 1 (groq) fails with 429 Rate Limit
        mock_groq = MagicMock()
        mock_groq.generate.side_effect = LLMRateLimitError("Groq 429 rate limit")
        router.register_client("groq", mock_groq)

        # Provider 2 (ollama) succeeds
        mock_ollama = MagicMock()
        mock_ollama.model_name = "llama3:8b"
        mock_ollama.generate.return_value = LLMResponse(
            content="Advice generated from Ollama fallback",
            model="llama3:8b",
            provider="ollama",
            usage=TokenUsage(total_tokens=150),
        )
        router.register_client("ollama", mock_ollama)

        resp = router.generate_with_fallback(
            prompt="Analyze this case",
            provider_order=["groq", "ollama"],
        )

        assert resp.content == "Advice generated from Ollama fallback"
        assert resp.provider == "ollama"

        # Case where ALL providers fail
        mock_ollama.generate.side_effect = LLMConnectionError("Ollama daemon down")
        with pytest.raises(LLMAllProvidersFailedError) as exc_info:
            router.generate_with_fallback(
                prompt="Analyze this case",
                provider_order=["groq", "ollama"],
            )
        assert "All configured providers failed" in str(exc_info.value)


# ==============================================================================
# 5. WORKFLOW 9: RAG RETRIEVAL & CHROMADB 1.5.9 HYBRID RRF RETRIEVER
# ==============================================================================


class TestWorkflow9RAGRetrievalEmpirical:
    """Empirical verification of ChromaDB 1.5.9 backend, BM25 RRF fusion, and tokenizer."""

    @pytest.fixture
    def statutory_corpus(self) -> list[RetrievedChunk]:
        return [
            RetrievedChunk(
                chunk_id="cpa_sec_2_7",
                statute="Consumer Protection Act, 2019",
                section="Section 2(7)",
                title="Definition of Consumer",
                content=(
                    "(7) 'consumer' means any person who buys any goods for a consideration "
                    "which has been paid or promised or partly paid and partly promised... "
                    "Explanation: commercial purpose does not include goods bought and used "
                    "exclusively for earning livelihood by self-employment."
                ),
                score=0.0,
            ),
            RetrievedChunk(
                chunk_id="cpa_sec_2_10",
                statute="Consumer Protection Act, 2019",
                section="Section 2(10)",
                title="Definition of Defect",
                content=(
                    "(10) 'defect' means any fault, imperfection or shortcoming in the quality, "
                    "quantity, potency, purity or standard which is required to be maintained "
                    "by or under any law for the time being in force."
                ),
                score=0.0,
            ),
            RetrievedChunk(
                chunk_id="cpa_sec_2_47",
                statute="Consumer Protection Act, 2019",
                section="Section 2(47)",
                title="Unfair Trade Practice",
                content=(
                    "(47) 'unfair trade practice' means a trade practice which, for the purpose "
                    "of promoting the sale, use or supply of any goods or for the provision of "
                    "any service, adopts any unfair method or unfair or deceptive practice "
                    "including false representation, misleading advertisement, "
                    "non-issuance of bill."
                ),
                score=0.0,
            ),
            RetrievedChunk(
                chunk_id="cpa_sec_35",
                statute="Consumer Protection Act, 2019",
                section="Section 35",
                title="Manner of Complaint Filing",
                content=(
                    "Section 35 provides the procedure for filing a complaint before the "
                    "District Commission along with the prescribed e-Daakhil court fee."
                ),
                score=0.0,
            ),
            RetrievedChunk(
                chunk_id="cpa_sec_69",
                statute="Consumer Protection Act, 2019",
                section="Section 69",
                title="Limitation Period",
                content=(
                    "Section 69(1) dictates that the District Commission, State Commission or "
                    "National Commission shall not admit a complaint unless it is filed within "
                    "two years (730 days) from the date on which the cause of action has arisen."
                ),
                score=0.0,
            ),
        ]

    def test_chroma_dense_retriever_1_5_9_ephemeral(
        self, statutory_corpus: list[RetrievedChunk]
    ) -> None:
        """Challenge: ChromaDenseRetriever with modern ChromaDB 1.5.9 EphemeralClient."""
        dense = ChromaDenseRetriever(collection_name="test_empirical_collection")
        dense.index(statutory_corpus)

        results = dense.search("unfair trade practice deceptive statement", top_k=3)
        assert len(results) > 0
        top_chunk, score = results[0]
        assert getattr(top_chunk, "section", "") == "Section 2(47)"
        assert score > 0.0

    def test_statutory_hybrid_retriever_exact_section_lookup(
        self, statutory_corpus: list[RetrievedChunk]
    ) -> None:
        """Challenge: Exact section lookup Section 2(47) fuses BM25 and Chroma to rank #1."""
        dense = ChromaDenseRetriever(collection_name="test_exact_lookup")
        retriever = StatutoryHybridRetriever(
            chunks=statutory_corpus,
            dense_retriever=dense,
            rrf_k=60,
        )

        query = "What is Section 2(47) regarding unfair trade practice?"
        results = retriever.retrieve(query, top_k=3)

        assert len(results) > 0
        top_chunk = results[0]
        assert top_chunk.section == "Section 2(47)"
        assert top_chunk.rank == 1
        # Validate mathematical RRF score bounds:
        # w / (60 + 1) + w / (60 + 1) + bonus (0.02) ~ 0.0528
        assert top_chunk.score > 0.025
        assert top_chunk.score <= (1.0 / 61.0 + 1.0 / 61.0 + 0.0201)

    def test_retrieval_confidence_gate_abstains_on_out_of_domain(
        self, statutory_corpus: list[RetrievedChunk]
    ) -> None:
        """Challenge: Out-of-domain query fails confidence threshold, triggering abstention."""
        dense = ChromaDenseRetriever(collection_name="test_confidence_abstain")
        retriever = StatutoryHybridRetriever(
            chunks=statutory_corpus,
            dense_retriever=dense,
            min_confidence_threshold=0.012,
        )

        gate = RetrievalConfidenceGate(min_rrf_threshold=0.012)

        # Unrelated query with zero statutory relevance
        gibberish = "astrobiology exoplanet magnetic atmospheric methane detection quantum spin"
        chunks, conf_result = retriever.retrieve_with_confidence(gibberish)

        assert conf_result.confidence_passed is False
        assert conf_result.abstention_triggered is True
        assert conf_result.abstention_message is not None
        assert "unable to locate verified statutory provisions" in conf_result.abstention_message

        gate_result = gate.evaluate(chunks, query=gibberish)
        assert gate_result.is_grounded is False
        assert gate_result.abstention_triggered is True

    def test_legal_tokenizer_statutory_and_currency_preservation(self) -> None:
        """Challenge: LegalTokenizer preserves Indian currency, sections, and subclauses."""
        text = (
            "Under Section 2(47)(viii) of CPA 2019, compensation of ₹50,000 and "
            "₹2,50,000 was claimed via e-Daakhil against the e-commerce seller."
        )

        tokens = LegalTokenizer.tokenize(text)
        token_set = set(tokens)

        # Statutory citations preserved
        assert any("2(47)" in t for t in token_set)
        # Currency notations preserved
        assert any("50,000" in t or "50000" in t for t in token_set)
        assert any("2,50,000" in t or "250000" in t for t in token_set)
        # Indian e-commerce / court terms preserved
        assert any("daakhil" in t for t in token_set)
        assert any("commerce" in t for t in token_set)
        # Stopwords stripped
        assert "under" not in token_set
        assert "of" not in token_set
        assert "was" not in token_set
