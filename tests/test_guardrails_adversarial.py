"""Adversarial stress-testing suite for Milestone 4 3-Layer Guardrails Engine.

Empirically challenges:
1. Layer 1 Scope Checker (ScopeChecker):
   - Out-of-scope rejections (crimes, NI Act 138, commercial B2B, family, injunctions)
   - Mandatory consumer overrides (Instagram UPI scam Scenario 2, Xerox machine)
   - Identified vulnerabilities: Regex gaps allowing 'raw material for factory resale',
     'eviction injunction', 'urgent injunction', and 'custody of children' to pass.
2. Layer 2 Retrieval Confidence Gate (RetrievalConfidenceGate & StatutoryHybridRetriever):
   - In-domain query confidence clearing
   - Deterministic abstention on out-of-domain queries (astronomy, cooking, nonsense)
3. Layer 3 Citation Verifier (CitationVerifier):
   - Verified statutory citations vs fabricated sections (Section 999) and repealed CPA 1986
   - Case law precedent detection (Sharma v. Flipkart 2022 CPJ 105 SC)
   - Identified vulnerabilities: Parenthesized citations like '(2022) CPJ 105 SC'
     bypassing detection due to regex word boundary bug, fabricated subclauses,
     and false positives on plural 'Sections X and Y'.
"""

from __future__ import annotations

import pytest

from legal_assistant.guardrails.scope_checker import ScopeChecker
from legal_assistant.guardrails.verifier import (
    CitationVerifier,
    RetrievalConfidenceGate,
)
from legal_assistant.rag.chunker import StatutoryChunk, StatutoryChunkMetadata
from legal_assistant.rag.hybrid_retriever import (
    InMemoryDenseRetriever,
    RetrievedChunk,
    StatutoryHybridRetriever,
)
from legal_assistant.schemas import ScopeCategory, ScopeResult, VerifiedResponse
from legal_assistant.workflows.case_builder import (
    CaseBuilder,
    OutOfScopeDisputeError,
)

# ==============================================================================
# 1. LAYER 1: Scope Checker Adversarial Tests & Edge Cases
# ==============================================================================


class TestScopeCheckerAdversarial:
    """Empirical challenge suite for Layer 1 Scope Checker."""

    @pytest.fixture
    def checker(self) -> ScopeChecker:
        """Provide a ScopeChecker instance."""
        return ScopeChecker()

    @pytest.mark.parametrize(
        ("crime_query", "trigger_word"),
        [
            ("The accused committed murder in broad daylight.", "murder"),
            ("An armed robbery took place at my store.", "robbery"),
            ("The gang is demanding money through blackmail and extortion.", "extortion"),
            ("I want to register an FIR with the police against the accused.", "fir"),
        ],
    )
    def test_criminal_offences_rejected(
        self,
        checker: ScopeChecker,
        crime_query: str,
        trigger_word: str,
    ) -> None:
        """Verify criminal offences (murder, robbery, extortion, FIR) are rejected."""
        res: ScopeResult = checker.check_scope(crime_query)
        assert res.is_in_scope is False
        assert res.out_of_scope_category == ScopeCategory.CRIMINAL_OFFENSE.value
        assert res.escalation_advice is not None
        assert "police" in res.escalation_advice.lower() or "fir" in res.escalation_advice.lower()
        assert any(trigger_word in t.lower() for t in res.detected_triggers)

    def test_cheque_bounce_section_138_rejected(self, checker: ScopeChecker) -> None:
        """Verify cheque bounce under Section 138 Negotiable Instruments Act is rejected."""
        query = (
            "A cheque issued to me bounced due to insufficient funds. "
            "How do I issue a notice under Section 138 of the Negotiable Instruments Act?"
        )
        res = checker.check_scope(query)
        assert res.is_in_scope is False
        assert res.out_of_scope_category == ScopeCategory.CHEQUE_BOUNCE.value
        assert res.escalation_advice is not None
        assert "negotiable instruments act" in res.escalation_advice.lower()

    def test_commercial_b2b_nclt_insolvency_rejected(self, checker: ScopeChecker) -> None:
        """Verify corporate insolvency before NCLT under IBC is rejected."""
        query = (
            "The corporate debtor has defaulted on operational credit. We are filing "
            "an insolvency petition before the NCLT under the Insolvency and Bankruptcy Code (IBC)."
        )
        res = checker.check_scope(query)
        assert res.is_in_scope is False
        assert res.out_of_scope_category == ScopeCategory.COMMERCIAL_B2B.value
        assert res.escalation_advice is not None
        assert "nclt" in res.escalation_advice.lower()

    @pytest.mark.parametrize(
        "family_query",
        [
            "I want to file for mutual consent divorce under Hindu Marriage Act.",
            "My ex-spouse refuses to pay monthly maintenance under personal law.",
            "We are locked in a child custody dispute before the family court.",
        ],
    )
    def test_family_matrimonial_disputes_rejected(
        self,
        checker: ScopeChecker,
        family_query: str,
    ) -> None:
        """Verify family, divorce, child custody, and maintenance disputes are rejected."""
        res = checker.check_scope(family_query)
        assert res.is_in_scope is False
        assert res.out_of_scope_category == ScopeCategory.FAMILY_DIVORCE.value
        assert res.escalation_advice is not None
        assert "family court" in res.escalation_advice.lower()

    def test_urgent_stay_order_demolition_rejected(self, checker: ScopeChecker) -> None:
        """Verify urgent stay orders against municipal demolition are rejected."""
        query = (
            "The municipal corporation issued a demolition notice and the demolition squad "
            "is arriving tomorrow. I need an urgent stay order immediately."
        )
        res = checker.check_scope(query)
        assert res.is_in_scope is False
        assert res.out_of_scope_category == ScopeCategory.URGENT_INJUNCTION.value
        assert res.escalation_advice is not None
        assert "injunction" in res.escalation_advice.lower()

    def test_consumer_override_instagram_upi_scam_scenario_2(
        self,
        checker: ScopeChecker,
    ) -> None:
        """Verify Instagram UPI seller scam remains IN SCOPE under CPA Section 2(47)."""
        query = (
            "I ordered clothes on Instagram and paid ₹4,500 via UPI. "
            "The seller blocked the buyer and did not deliver the products."
        )
        res = checker.check_scope(query)
        assert res.is_in_scope is True
        assert res.out_of_scope_category is None
        assert res.escalation_advice is None

    def test_consumer_override_livelihood_small_shopkeeper_xerox(
        self,
        checker: ScopeChecker,
    ) -> None:
        """Verify livelihood exception under Section 2(7) Explanation (a) remains IN SCOPE."""
        query = (
            "I am a small shopkeeper buying a Xerox photocopier machine for "
            "earning my personal self-employment livelihood. The machine failed in 2 days."
        )
        res = checker.check_scope(query)
        assert res.is_in_scope is True
        assert res.out_of_scope_category is None
        assert res.escalation_advice is None

    def test_raw_material_for_factory_resale_rejected(
        self,
        checker: ScopeChecker,
    ) -> None:
        """Verify 'raw material for factory resale' is rejected as commercial B2B."""
        query = "We purchased raw material for factory resale to industrial manufacturers."
        res = checker.check_scope(query)
        assert res.is_in_scope is False
        assert res.out_of_scope_category == ScopeCategory.COMMERCIAL_B2B.value

    def test_eviction_injunction_rejected(
        self,
        checker: ScopeChecker,
    ) -> None:
        """Verify 'eviction injunction' is rejected as urgent court injunction."""
        query = "The landlord issued a notice and I need an eviction injunction immediately."
        res = checker.check_scope(query)
        assert res.is_in_scope is False
        assert res.out_of_scope_category == ScopeCategory.URGENT_INJUNCTION.value

    def test_custody_of_children_rejected(
        self,
        checker: ScopeChecker,
    ) -> None:
        """Verify non-adjacent 'custody of children' is rejected as family dispute."""
        query = "I am filing a suit seeking custody of my children."
        res = checker.check_scope(query)
        assert res.is_in_scope is False
        assert res.out_of_scope_category == ScopeCategory.FAMILY_DIVORCE.value

    def test_blast_radius_downstream_casebuilder_rejects_eviction_injunction(
        self,
        checker: ScopeChecker,
    ) -> None:
        """Verify CaseBuilder rejects out-of-scope eviction injunction dispute."""
        builder = CaseBuilder(scope_checker=checker)
        with pytest.raises(OutOfScopeDisputeError) as exc_info:
            builder.build_case(
                "The landlord sent an eviction notice and we need an eviction injunction.",
                use_llm=False,
            )
        assert exc_info.value.scope_result is not None
        cat = exc_info.value.scope_result.out_of_scope_category
        assert cat == ScopeCategory.URGENT_INJUNCTION.value


# ==============================================================================
# 2. LAYER 2: Retrieval Confidence Gate Adversarial Tests
# ==============================================================================


class TestRetrievalConfidenceGateAdversarial:
    """Empirical challenge suite for Layer 2 Retrieval Confidence Gate."""

    @pytest.fixture
    def test_retriever(self) -> StatutoryHybridRetriever:
        """Provide hybrid retriever with representative statutory chunks."""
        chunks = [
            StatutoryChunk(
                chunk_id="cpa_2_47",
                content=(
                    "Section 2(47) defines unfair trade practice as adopting any unfair "
                    "method or deceptive practice including refusal to refund consideration."
                ),
                metadata=StatutoryChunkMetadata(
                    statute="Consumer Protection Act, 2019",
                    chapter="Preliminary",
                    section="Section 2(47)",
                    section_title="Unfair Trade Practice",
                    clause="",
                    act_year=2019,
                    chunk_id="cpa_2_47",
                    breadcrumb="CPA 2019 > Preliminary > Section 2(47)",
                ),
            ),
            StatutoryChunk(
                chunk_id="ecom_4_5",
                content=(
                    "Rule 4(5) Every e-commerce entity shall acknowledge receipt of consumer "
                    "grievance within 48 hours and redressed within one month."
                ),
                metadata=StatutoryChunkMetadata(
                    statute="Consumer Protection (E-Commerce) Rules, 2020",
                    chapter="Rules",
                    section="Rule 4(5)",
                    section_title="Grievance Redressal Mechanism",
                    clause="",
                    act_year=2020,
                    chunk_id="ecom_4_5",
                    breadcrumb="E-Commerce Rules 2020 > Rules > Rule 4(5)",
                ),
            ),
        ]
        dense = InMemoryDenseRetriever()
        return StatutoryHybridRetriever(chunks=chunks, dense_retriever=dense)

    def test_in_domain_query_passes_confidence_gate(
        self,
        test_retriever: StatutoryHybridRetriever,
    ) -> None:
        """Verify in-domain statutory query passes confidence gate."""
        query = "unfair trade practice refund refusal under Section 2(47)"
        chunks, conf = test_retriever.retrieve_with_confidence(query, top_k=2)
        assert len(chunks) > 0
        assert conf.confidence_passed is True
        assert conf.abstention_triggered is False
        assert conf.top_rrf_score >= test_retriever.confidence_threshold
        assert conf.abstention_message is None

    @pytest.mark.parametrize(
        "out_of_domain_query",
        [
            "astronomy black hole event horizon general relativity stellar nucleosynthesis",
            "how to bake a chocolate fudge cake recipe using flour sugar and baking powder",
            "asdfghjkl qwertyuiop zxcvbnm 1234567890",
        ],
    )
    def test_out_of_domain_queries_trigger_abstention(
        self,
        test_retriever: StatutoryHybridRetriever,
        out_of_domain_query: str,
    ) -> None:
        """Verify astronomy, cooking, and nonsense queries trigger deterministic abstention."""
        chunks, conf = test_retriever.retrieve_with_confidence(out_of_domain_query, top_k=2)
        assert len(chunks) == 0
        assert conf.confidence_passed is False
        assert conf.abstention_triggered is True
        assert conf.abstention_message is not None
        assert conf.abstention_message == StatutoryHybridRetriever.DEFAULT_ABSTENTION_MESSAGE

    def test_empty_chunk_list_triggers_abstention_deterministically(self) -> None:
        """Verify empty chunk list passed to RetrievalConfidenceGate triggers abstention."""
        gate = RetrievalConfidenceGate()
        eval_res = gate.evaluate([])
        assert eval_res.confidence_passed is False
        assert eval_res.abstention_triggered is True
        assert eval_res.top_rrf_score == 0.0
        assert eval_res.retrieved_chunk_count == 0
        assert eval_res.abstention_message == StatutoryHybridRetriever.DEFAULT_ABSTENTION_MESSAGE


# ==============================================================================
# 3. LAYER 3: Citation Verifier Adversarial Tests
# ==============================================================================


class TestCitationVerifierAdversarial:
    """Empirical challenge suite for Layer 3 Citation Verifier."""

    @pytest.fixture
    def verifier(self) -> CitationVerifier:
        """Provide CitationVerifier instance."""
        return CitationVerifier()

    @pytest.fixture
    def ground_truth_chunks(self) -> list[RetrievedChunk]:
        """Provide ground truth statutory chunks."""
        return [
            RetrievedChunk(
                chunk_id="cpa_2_47",
                content=(
                    "Section 2(47) defines unfair trade practice as adopting unfair methods "
                    "including refusing to refund consideration for defective goods."
                ),
                statute="Consumer Protection Act, 2019",
                chapter="Preliminary",
                section="Section 2(47)",
                title="Unfair Trade Practice",
                score=0.035,
                retrieval_method="hybrid_rrf",
            ),
            RetrievedChunk(
                chunk_id="ecom_4_5",
                content="Rule 4(5) requires acknowledgment of consumer grievance within 48 hours.",
                statute="Consumer Protection (E-Commerce) Rules, 2020",
                chapter="Rules",
                section="Rule 4(5)",
                title="Grievance Redressal Mechanism",
                score=0.030,
                retrieval_method="hybrid_rrf",
            ),
        ]

    def test_valid_statutory_citations_pass(
        self,
        verifier: CitationVerifier,
        ground_truth_chunks: list[RetrievedChunk],
    ) -> None:
        """Verify genuine statutory citations matching corpus pass without flagging."""
        text = (
            "Under Section 2(47) of the Consumer Protection Act, 2019, refusal to refund "
            "is prohibited. Further, Rule 4(5) of the E-Commerce Rules requires 48-hour response."
        )
        res: VerifiedResponse = verifier.verify_response(text, ground_truth_chunks)
        assert res.hallucination_detected is False
        assert len(res.flagged_citations) == 0
        assert "Section 2(47)" in res.verified_citations
        assert "Rule 4(5)" in res.verified_citations
        assert res.cleaned_text == text

    def test_fabricated_section_999_flagged(
        self,
        verifier: CitationVerifier,
        ground_truth_chunks: list[RetrievedChunk],
    ) -> None:
        """Verify fabricated Section 999 is flagged as unverified citation."""
        text = "Under Section 999 of the Consumer Protection Act, 2019, you get punitive damages."
        res = verifier.verify_response(text, ground_truth_chunks, action="flag")
        assert res.hallucination_detected is True
        assert "Section 999" in res.flagged_citations
        assert "<flag>Section 999: Unverified citation</flag>" in res.cleaned_text

    def test_fabricated_section_999_stripped(
        self,
        verifier: CitationVerifier,
        ground_truth_chunks: list[RetrievedChunk],
    ) -> None:
        """Verify fabricated Section 999 is stripped from text in strip mode."""
        text = "Under Section 999 of the Act, compensation is mandatory."
        res = verifier.verify_response(text, ground_truth_chunks, action="strip")
        assert res.hallucination_detected is True
        assert "Section 999" not in res.cleaned_text
        assert "[Citation omitted - unverified in statutory corpus]" in res.cleaned_text

    def test_repealed_1986_act_prohibited(
        self,
        verifier: CitationVerifier,
        ground_truth_chunks: list[RetrievedChunk],
    ) -> None:
        """Verify citations to repealed Consumer Protection Act 1986 are flagged as invalid."""
        text = (
            "Pursuant to the Consumer Protection Act, 1986, "
            "the district forum can order replacement."
        )
        res = verifier.verify_response(text, ground_truth_chunks)
        assert res.hallucination_detected is True
        assert any("1986" in f for f in res.flagged_citations)

    def test_fabricated_case_law_sharma_v_flipkart_detected(
        self,
        verifier: CitationVerifier,
        ground_truth_chunks: list[RetrievedChunk],
    ) -> None:
        """Verify fabricated case law 'Sharma v. Flipkart 2022 CPJ 105 SC' is caught."""
        text = "In Sharma v. Flipkart 2022 CPJ 105 SC, the Supreme Court mandated full refund."
        res = verifier.verify_response(text, ground_truth_chunks)
        assert res.hallucination_detected is True
        assert any("Sharma v. Flipkart" in f for f in res.flagged_citations)

    def test_parenthesized_year_citation_detected(
        self,
        verifier: CitationVerifier,
        ground_truth_chunks: list[RetrievedChunk],
    ) -> None:
        """Verify '(2022) CPJ 105 SC' is caught as unverified judicial precedent."""
        text = "As held in (2022) CPJ 105 SC, e-commerce platforms cannot disclaim liability."
        res = verifier.verify_response(text, ground_truth_chunks)
        assert res.hallucination_detected is True
        assert any("(2022) CPJ 105 SC" in f for f in res.flagged_citations)

    def test_fabricated_subclause_on_valid_base_section_rejected(
        self,
        verifier: CitationVerifier,
        ground_truth_chunks: list[RetrievedChunk],
    ) -> None:
        """Verify fabricated subclause 'Section 2(47)(xyz999)' is flagged as unverified."""
        text = "Under Section 2(47)(xyz999), deceptive algorithmic pricing is prohibited."
        res = verifier.verify_response(text, ground_truth_chunks)
        assert res.hallucination_detected is True
        assert "Section 2(47)(xyz999)" in res.flagged_citations

    def test_plural_sections_correctly_verified(
        self,
        verifier: CitationVerifier,
        ground_truth_chunks: list[RetrievedChunk],
    ) -> None:
        """Verify plural 'Sections 2(47) and 2(47)' is cleanly verified without false positive."""
        text = "Under Sections 2(47) and 2(47), refunds must be processed."
        res = verifier.verify_response(text, ground_truth_chunks)
        assert res.hallucination_detected is False
        assert "Sections 2(47) and 2(47)" in res.verified_citations
