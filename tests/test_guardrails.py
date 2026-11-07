"""Comprehensive offline unit tests for 3-Layer Anti-Hallucination Guardrails.

Verifies 100% offline with zero external network dependencies:
1. Layer 1 Scope Checker (ScopeChecker): Pre-retrieval filtering for Criminal (BNS/IPC),
   NI Act 138 cheque bounce, commercial B2B, family/matrimonial, and urgent court injunctions.
2. Layer 2 Retrieval Confidence Gate (RetrievalConfidenceGate): Grounding verification,
   RRF score thresholding, token overlap safeguards, and deterministic abstention.
3. Layer 3 Post-Generation Citation Verifier (CitationVerifier): Section validation,
   fabricated section flagging/stripping (<flag>...</flag>), and hallucinated case law detection.

Execution time: < 2.0 seconds. Zero # noqa or # type: ignore comments.
"""

from __future__ import annotations

import pytest

from legal_assistant.guardrails.scope_checker import ScopeChecker
from legal_assistant.guardrails.verifier import (
    CitationVerifier,
    RetrievalConfidenceGate,
    RetrievalUngroundedError,
)
from legal_assistant.rag.chunker import StatutoryChunk, StatutoryChunkMetadata
from legal_assistant.rag.hybrid_retriever import (
    InMemoryDenseRetriever,
    RetrievedChunk,
    StatutoryHybridRetriever,
)
from legal_assistant.schemas import ScopeCategory, ScopeResult, VerifiedResponse

# ==============================================================================
# Layer 1: Scope Checker Unit Tests
# ==============================================================================


class TestScopeChecker:
    """Offline unit test suite for Layer 1 Scope Checker."""

    @pytest.fixture
    def checker(self) -> ScopeChecker:
        """Provide a ScopeChecker instance."""
        return ScopeChecker()

    def test_criminal_offense_bns_detection(self, checker: ScopeChecker) -> None:
        """Verify criminal offences under BNS/IPC are flagged as out of scope."""
        query = (
            "The merchant physically attacked me, broke my door and stole my laptop. "
            "I want to register an FIR under Bharatiya Nyaya Sanhita (BNS) for theft and assault."
        )
        result: ScopeResult = checker.check_scope(query)
        assert result.is_in_scope is False
        assert result.out_of_scope_category == ScopeCategory.CRIMINAL_OFFENSE.value
        assert result.escalation_advice is not None
        assert (
            "police" in result.escalation_advice.lower()
            or "fir" in result.escalation_advice.lower()
        )
        assert len(result.detected_triggers) > 0

    def test_cheque_bounce_ni_act_138_detection(self, checker: ScopeChecker) -> None:
        """Verify Section 138 Negotiable Instruments Act cheque bounce is flagged."""
        query = (
            "The client issued a cheque of Rs 50,000 which bounced due to insufficient funds. "
            "How do I issue a demand notice under Section 138 of the Negotiable Instruments Act?"
        )
        result = checker.check_scope(query)
        assert result.is_in_scope is False
        assert result.out_of_scope_category == ScopeCategory.CHEQUE_BOUNCE.value
        assert result.escalation_advice is not None
        assert (
            "138" in result.escalation_advice
            or "negotiable instruments" in result.escalation_advice.lower()
        )

    def test_commercial_b2b_litigation_detection(self, checker: ScopeChecker) -> None:
        """Verify commercial B2B dispute is flagged due to Section 2(7) commercial exclusion."""
        query = (
            "Our company bought 2,000 industrial transformers for commercial resale and "
            "distribution to factory clients. The vendor breached the wholesale contract."
        )
        result = checker.check_scope(query)
        assert result.is_in_scope is False
        assert result.out_of_scope_category == ScopeCategory.COMMERCIAL_B2B.value
        assert result.escalation_advice is not None
        assert "commercial" in result.escalation_advice.lower()

    def test_family_divorce_matrimonial_detection(self, checker: ScopeChecker) -> None:
        """Verify matrimonial and divorce disputes are routed to Family Court."""
        query = "My spouse filed for divorce and I want maintenance and custody of our child."
        result = checker.check_scope(query)
        assert result.is_in_scope is False
        assert result.out_of_scope_category == ScopeCategory.FAMILY_DIVORCE.value
        assert result.escalation_advice is not None
        assert "family court" in result.escalation_advice.lower()

    def test_urgent_injunction_stay_order_detection(self, checker: ScopeChecker) -> None:
        """Verify emergency court stay order requests trigger immediate advocate escalation."""
        query = (
            "The demolition squad is arriving tomorrow morning at 7 AM. "
            "I need an urgent physical stay order and emergency injunction from the High Court."
        )
        result = checker.check_scope(query)
        assert result.is_in_scope is False
        assert result.out_of_scope_category == ScopeCategory.URGENT_INJUNCTION.value
        assert result.escalation_advice is not None
        assert "advocate" in result.escalation_advice.lower()

    def test_valid_consumer_dispute_ecommerce(self, checker: ScopeChecker) -> None:
        """Verify standard e-commerce defective product dispute is classified as in-scope."""
        query = (
            "I purchased a smartphone for Rs. 24,999 on Flipkart. The device received has "
            "a cracked screen and seller refuses refund citing return policy expired."
        )
        result = checker.check_scope(query)
        assert result.is_in_scope is True
        assert result.out_of_scope_category is None
        assert result.escalation_advice is None

    def test_valid_consumer_dispute_food_delivery_hinglish(self, checker: ScopeChecker) -> None:
        """Verify Hinglish food delivery grievance is correctly retained in scope."""
        query = (
            "Zomato se dinner mangwaya tha Rs 650 ka. Delivery boy ne order deliver nahi kiya "
            "par app me delivered mark ho gaya. Customer support refund nahi de raha."
        )
        result = checker.check_scope(query)
        assert result.is_in_scope is True
        assert result.out_of_scope_category is None

    def test_livelihood_exception_protection(self, checker: ScopeChecker) -> None:
        """Verify livelihood self-employment under Section 2(7) Explanation (a) remains in scope."""
        query = (
            "I run a small xerox shop for my personal livelihood and self-employment. "
            "I bought a photocopier machine for Rs 85,000 which broke down in 2 weeks."
        )
        result = checker.check_scope(query)
        assert result.is_in_scope is True
        assert result.out_of_scope_category is None

    def test_empty_and_whitespace_queries(self, checker: ScopeChecker) -> None:
        """Verify empty and whitespace inputs do not raise unhandled exceptions."""
        result_empty = checker.check_scope("")
        assert result_empty.is_in_scope is False
        assert result_empty.out_of_scope_category == ScopeCategory.OTHER_NON_CONSUMER.value

        result_ws = checker.check_scope("    \n\t  ")
        assert result_ws.is_in_scope is False

    def test_violent_assault_and_death_threat_with_refund_rejected(
        self,
        checker: ScopeChecker,
    ) -> None:
        """Verify violent crimes accompanied by consumer words are strictly rejected."""
        q1 = "The shopkeeper assaulted me when I demanded a refund."
        res1: ScopeResult = checker.check_scope(q1)
        assert res1.is_in_scope is False
        assert res1.out_of_scope_category == ScopeCategory.CRIMINAL_OFFENSE.value

        q2 = "The merchant gave me a threat to kill when I asked for a refund."
        res2: ScopeResult = checker.check_scope(q2)
        assert res2.is_in_scope is False
        assert res2.out_of_scope_category == ScopeCategory.CRIMINAL_OFFENSE.value

    def test_cheque_dishonour_variations_rejected(
        self,
        checker: ScopeChecker,
    ) -> None:
        """Verify colloquial cheque dishonour phrasing is routed out of consumer forum."""
        queries = [
            "The supplier gave me a bad cheque that dishonoured.",
            "A cheque was dishonoured due to stop payment.",
            "I received a dishonoured cheque from the client.",
        ]
        for q in queries:
            res = checker.check_scope(q)
            assert res.is_in_scope is False
            assert res.out_of_scope_category == ScopeCategory.CHEQUE_BOUNCE.value

    def test_commercial_b2b_wholesale_and_contracts_rejected(
        self,
        checker: ScopeChecker,
    ) -> None:
        """Verify commercial wholesale resale and B2B contracts are rejected."""
        queries = [
            "We bought 500 units of widgets for wholesale resale.",
            "We bought goods for resale to retailers.",
            "Commercial contract dispute between two private limited companies.",
        ]
        for q in queries:
            res = checker.check_scope(q)
            assert res.is_in_scope is False
            assert res.out_of_scope_category == ScopeCategory.COMMERCIAL_B2B.value

    def test_urgent_injunction_stop_construction_and_eviction_orders_rejected(
        self,
        checker: ScopeChecker,
    ) -> None:
        """Verify stop construction orders and tenant eviction orders are rejected."""
        queries = [
            "We need an injunction to stop construction on our land.",
            "The tenant refuses to vacate and we want an eviction order.",
        ]
        for q in queries:
            res = checker.check_scope(q)
            assert res.is_in_scope is False
            assert res.out_of_scope_category == ScopeCategory.URGENT_INJUNCTION.value


# ==============================================================================
# Layer 2: Retrieval Confidence Gate Unit Tests
# ==============================================================================


class TestRetrievalConfidenceGate:
    """Offline unit test suite for Layer 2 Retrieval Confidence Gate."""

    @pytest.fixture
    def populated_retriever(self) -> StatutoryHybridRetriever:
        """Provide retriever with representative statutory chunks."""
        chunks = [
            StatutoryChunk(
                chunk_id="cpa_2_47",
                content="Section 2(47) defines unfair trade practice including refusing to refund.",
                metadata=StatutoryChunkMetadata(
                    statute="CPA 2019",
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
                chunk_id="ecom_6_3",
                content="Rule 6(3) Seller shall not refuse to take back goods or refuse refund.",
                metadata=StatutoryChunkMetadata(
                    statute="E-Commerce Rules 2020",
                    chapter="Sellers",
                    section="Rule 6(3)",
                    section_title="Duties of Sellers",
                    clause="",
                    act_year=2020,
                    chunk_id="ecom_6_3",
                    breadcrumb="E-Commerce Rules 2020 > Sellers > Rule 6(3)",
                ),
            ),
            StatutoryChunk(
                chunk_id="cpa_86",
                content="Section 86 Product liability of e-commerce marketplace entity.",
                metadata=StatutoryChunkMetadata(
                    statute="CPA 2019",
                    chapter="Product Liability",
                    section="Section 86",
                    section_title="Product Liability of Marketplace",
                    clause="",
                    act_year=2019,
                    chunk_id="cpa_86",
                    breadcrumb="CPA 2019 > Product Liability > Section 86",
                ),
            ),
        ]
        dense = InMemoryDenseRetriever()
        retriever = StatutoryHybridRetriever(chunks=chunks, dense_retriever=dense)
        return retriever

    def test_in_domain_query_passes_confidence_gate(
        self,
        populated_retriever: StatutoryHybridRetriever,
    ) -> None:
        """Verify valid consumer law query clears the confidence threshold."""
        query = "defective laptop refund under unfair trade practice Section 2(47)"
        chunks, conf = populated_retriever.retrieve_with_confidence(query, top_k=3)
        assert len(chunks) > 0
        assert conf.confidence_passed is True
        assert conf.abstention_triggered is False
        assert conf.top_rrf_score >= populated_retriever.confidence_threshold

    def test_out_of_domain_query_triggers_abstention(
        self,
        populated_retriever: StatutoryHybridRetriever,
    ) -> None:
        """Verify completely unrelated query triggers deterministic abstention."""
        query = "quantum mechanics schrodinger wave function eigenvalue particle in a box"
        chunks, conf = populated_retriever.retrieve_with_confidence(query, top_k=3)
        assert len(chunks) == 0
        assert conf.confidence_passed is False
        assert conf.abstention_triggered is True
        assert conf.abstention_message is not None
        assert "unable to locate verified statutory provisions" in conf.abstention_message

    def test_empty_query_abstains_immediately(
        self,
        populated_retriever: StatutoryHybridRetriever,
    ) -> None:
        """Verify empty query abstains without error."""
        chunks, conf = populated_retriever.retrieve_with_confidence("", top_k=3)
        assert len(chunks) == 0
        assert conf.abstention_triggered is True

    def test_custom_threshold_override(
        self,
        populated_retriever: StatutoryHybridRetriever,
    ) -> None:
        """Verify passing explicit min_score strictly controls gate decision."""
        query = "defective laptop refund Section 2(47)"
        # Set impossibly high threshold 0.99
        _, conf_strict = populated_retriever.retrieve_with_confidence(
            query, top_k=3, min_score=0.99
        )
        assert conf_strict.confidence_passed is False
        assert conf_strict.abstention_triggered is True


class TestRetrievalConfidenceGateDirect:
    """Offline unit tests for standalone RetrievalConfidenceGate class."""

    @pytest.fixture
    def sample_chunks(self) -> list[RetrievedChunk]:
        """Provide sample retrieved chunks for direct evaluation."""
        return [
            RetrievedChunk(
                chunk_id="chunk_1",
                statute="CPA 2019",
                chapter="Chapter I",
                section="Section 2(47)",
                title="Unfair Trade Practice",
                content="Section 2(47) defines unfair trade practice as adopting unfair methods.",
                score=0.035,
                retrieval_method="hybrid_rrf",
            ),
            RetrievedChunk(
                chunk_id="chunk_2",
                statute="E-Commerce Rules 2020",
                chapter="Rules",
                section="Rule 4(5)",
                title="Grievance Redressal Mechanism",
                content="Rule 4(5) Every e-commerce entity shall acknowledge within 48 hours.",
                score=0.031,
                retrieval_method="hybrid_rrf",
            ),
        ]

    def test_direct_evaluate_with_grounded_chunks(
        self, sample_chunks: list[RetrievedChunk]
    ) -> None:
        """Verify evaluate with high-confidence chunks passes gate."""
        gate = RetrievalConfidenceGate(min_rrf_threshold=0.012)
        res = gate.evaluate(sample_chunks, query="refund refusal under Section 2(47)")
        assert res.is_grounded is True
        assert res.confidence_passed is True
        assert res.abstention_triggered is False
        assert res.top_rrf_score == 0.035
        assert res.retrieved_chunk_count == 2
        assert res.abstention_message is None

    def test_direct_evaluate_with_low_score_abstains(
        self, sample_chunks: list[RetrievedChunk]
    ) -> None:
        """Verify evaluate abstains when scores fall below threshold."""
        gate = RetrievalConfidenceGate(min_rrf_threshold=0.050)
        res = gate.evaluate(sample_chunks)
        assert res.is_grounded is False
        assert res.confidence_passed is False
        assert res.abstention_triggered is True
        assert res.top_rrf_score == 0.035
        assert res.abstention_message is not None

    def test_direct_evaluate_empty_chunk_list(self) -> None:
        """Verify evaluate returns abstention on empty chunk list."""
        gate = RetrievalConfidenceGate()
        res = gate.evaluate([])
        assert res.is_grounded is False
        assert res.confidence_passed is False
        assert res.abstention_triggered is True
        assert res.top_rrf_score == 0.0
        assert res.retrieved_chunk_count == 0
        assert res.abstention_message is not None

    def test_direct_is_grounded_method(self, sample_chunks: list[RetrievedChunk]) -> None:
        """Verify is_grounded boolean convenience helper."""
        gate = RetrievalConfidenceGate(min_rrf_threshold=0.012)
        assert gate.is_grounded(sample_chunks) is True
        assert gate.is_grounded([]) is False

    def test_direct_get_abstention_response_behavior(
        self, sample_chunks: list[RetrievedChunk]
    ) -> None:
        """Verify get_abstention_response_if_ungrounded returns appropriate text."""
        gate = RetrievalConfidenceGate(min_rrf_threshold=0.012)
        assert gate.get_abstention_response_if_ungrounded(sample_chunks) is None
        assert gate.get_abstention_response_if_ungrounded([]) is not None

    def test_retrieval_ungrounded_error_instantiation(self) -> None:
        """Verify RetrievalUngroundedError can be instantiated and caught."""
        with pytest.raises(RetrievalUngroundedError) as exc_info:
            raise RetrievalUngroundedError("Confidence score below threshold")
        assert "Confidence score below threshold" in str(exc_info.value)


# ==============================================================================
# Layer 3: Citation Verifier Unit Tests
# ==============================================================================


class TestCitationVerifier:
    """Offline unit test suite for Layer 3 Post-Generation Citation Verifier."""

    @pytest.fixture
    def verifier(self) -> CitationVerifier:
        """Provide a CitationVerifier instance."""
        return CitationVerifier()

    @pytest.fixture
    def sample_source_chunks(self) -> list[RetrievedChunk]:
        """Provide sample ground truth retrieved chunks."""
        return [
            RetrievedChunk(
                chunk_id="chunk_1",
                statute="Consumer Protection Act, 2019",
                chapter="Chapter I",
                section="Section 2(47)",
                title="Unfair Trade Practice",
                content="Section 2(47) defines unfair trade practice as adopting unfair methods.",
                score=0.035,
                retrieval_method="hybrid_rrf",
            ),
            RetrievedChunk(
                chunk_id="chunk_2",
                statute="Consumer Protection (E-Commerce) Rules, 2020",
                chapter="Rules",
                section="Rule 4(5)",
                title="Grievance Redressal Mechanism",
                content="Rule 4(5) Every e-commerce entity shall acknowledge within 48 hours.",
                score=0.031,
                retrieval_method="hybrid_rrf",
            ),
        ]

    def test_valid_statutory_citations_pass(
        self,
        verifier: CitationVerifier,
        sample_source_chunks: list[RetrievedChunk],
    ) -> None:
        """Verify text with authentic citations physically present in chunks passes validation."""
        llm_text = (
            "Under Section 2(47) of the Consumer Protection Act, 2019, refusing a refund is an "
            "unfair trade practice. Additionally, under Rule 4(5) of the E-Commerce Rules, 2020, "
            "the platform must acknowledge your grievance within 48 hours."
        )
        result: VerifiedResponse = verifier.verify_response(llm_text, sample_source_chunks)
        assert result.hallucination_detected is False
        assert len(result.flagged_citations) == 0
        assert "Section 2(47)" in result.verified_citations
        assert "Rule 4(5)" in result.verified_citations
        assert result.cleaned_text == llm_text

    def test_fabricated_section_number_flagged(
        self,
        verifier: CitationVerifier,
        sample_source_chunks: list[RetrievedChunk],
    ) -> None:
        """Verify nonexistent section number is flagged with <flag> tag."""
        llm_text = (
            "Under Section 999 of the Consumer Protection Act, 2019, "
            "you are entitled to triple damages."
        )
        result = verifier.verify_response(llm_text, sample_source_chunks, flag_mode="flag")
        assert result.hallucination_detected is True
        assert len(result.flagged_citations) > 0
        assert any("999" in f for f in result.flagged_citations)
        assert "<flag>" in result.cleaned_text
        assert "Unverified citation" in result.cleaned_text

    def test_fabricated_section_number_stripped(
        self,
        verifier: CitationVerifier,
        sample_source_chunks: list[RetrievedChunk],
    ) -> None:
        """Verify nonexistent section number is completely excised in strip mode."""
        llm_text = (
            "Under Section 888 of the Consumer Protection Act, 2019, the merchant must pay a fine."
        )
        result = verifier.verify_response(llm_text, sample_source_chunks, flag_mode="strip")
        assert result.hallucination_detected is True
        assert "Section 888" not in result.cleaned_text

    def test_repealed_1986_act_prohibited(
        self,
        verifier: CitationVerifier,
        sample_source_chunks: list[RetrievedChunk],
    ) -> None:
        """Verify citations to repealed Consumer Protection Act 1986 are caught and flagged."""
        llm_text = (
            "Under Section 14 of the Consumer Protection Act, 1986, "
            "the Forum can order replacement."
        )
        result = verifier.verify_response(llm_text, sample_source_chunks)
        assert result.hallucination_detected is True
        assert any("1986" in f or "Section 14" in f for f in result.flagged_citations)

    def test_hallucinated_judicial_precedent_detected(
        self,
        verifier: CitationVerifier,
        sample_source_chunks: list[RetrievedChunk],
    ) -> None:
        """Verify hallucinated case citations are caught when absent from statutory corpus."""
        llm_text = (
            "As settled in the landmark case Ramesh Sharma v. Flipkart Private Limited "
            "(2022) CPJ 45 NCDRC, platforms cannot deny refunds."
        )
        result = verifier.verify_response(llm_text, sample_source_chunks)
        assert result.hallucination_detected is True
        assert any("Ramesh Sharma" in f or "CPJ" in f for f in result.flagged_citations)

    def test_repeated_unverified_citations_no_nested_tags(self, verifier: CitationVerifier) -> None:
        """Verify repeated unverified citations do not produce nested <flag><flag> tags."""
        text = "Section 999 applies. In fact, Section 999 is crucial. As noted, Section 999."
        res = verifier.verify_response(text, [])
        assert "<flag><flag>" not in res.cleaned_text
        assert res.cleaned_text.count("<flag>") == 3
        assert res.flagged_citations == ["Section 999"]
        assert res.hallucination_detected is True

    def test_substring_matching_year_and_numbers_not_grounded(
        self, verifier: CitationVerifier
    ) -> None:
        """Verify numbers inside year 2019 or amounts do not verify single/double digit sections."""
        chunk = RetrievedChunk(
            chunk_id="c_year",
            statute="CPA 2019",
            chapter="Chapter I",
            section="Section 86",
            title="Product Liability",
            content="Enacted in 2019 for claims up to Rs 21000. Section 86 applies.",
            score=0.03,
            retrieval_method="hybrid_rrf",
        )
        res = verifier.verify_response(
            "Under Section 2, Section 19, Section 20, and Section 21 of CPA",
            [chunk],
        )
        assert res.hallucination_detected is True
        assert "Section 2" in res.flagged_citations
        assert "Section 19" in res.flagged_citations
        assert "Section 20" in res.flagged_citations
        assert "Section 21" in res.flagged_citations

    def test_fabricated_subclause_on_valid_base_section_flagged(
        self, verifier: CitationVerifier, sample_source_chunks: list[RetrievedChunk]
    ) -> None:
        """Verify fabricated subclause attached to valid Section 2(47) is flagged."""
        text = "Under Section 2(47)(xyz999), deceptive algorithmic pricing is prohibited."
        res = verifier.verify_response(text, sample_source_chunks)
        assert res.hallucination_detected is True
        assert "Section 2(47)(xyz999)" in res.flagged_citations

    def test_parenthesized_case_law_flagged(self, verifier: CitationVerifier) -> None:
        """Verify parenthesized case law citations like (2022) CPJ 105 SC are detected."""
        text = "As held in (2022) CPJ 105 SC, e-commerce platforms cannot disclaim liability."
        res = verifier.verify_response(text, [])
        assert res.hallucination_detected is True
        assert any("(2022) CPJ 105 SC" in f for f in res.flagged_citations)

    def test_plural_sections_clean_extraction_and_verification(
        self, verifier: CitationVerifier
    ) -> None:
        """Verify plural citations Sections 2(11) and 2(47) are verified when both present."""
        chunks = [
            RetrievedChunk(
                chunk_id="c1",
                statute="CPA 2019",
                chapter="Chapter I",
                section="Section 2(11)",
                title="Deficiency",
                content="Section 2(11) defines deficiency in service.",
                score=0.03,
                retrieval_method="hybrid_rrf",
            ),
            RetrievedChunk(
                chunk_id="c2",
                statute="CPA 2019",
                chapter="Chapter I",
                section="Section 2(47)",
                title="Unfair Trade Practice",
                content="Section 2(47) defines unfair trade practice.",
                score=0.03,
                retrieval_method="hybrid_rrf",
            ),
        ]
        res = verifier.verify_response(
            "Under Sections 2(11) and 2(47), refunds must be processed.",
            chunks,
        )
        assert res.hallucination_detected is False
        assert "Sections 2(11) and 2(47)" in res.verified_citations

    def test_ccpa_guidelines_extraction_and_verification(self, verifier: CitationVerifier) -> None:
        """Verify CCPA Guidelines are extracted and verified against CCPA ground truth."""
        ccpa_chunk = RetrievedChunk(
            chunk_id="ccpa_1",
            statute="CCPA Guidelines",
            chapter="Dark Patterns",
            section="Guidelines 2022",
            title="Prevention of Dark Patterns",
            content="Central Consumer Protection Authority CCPA Guidelines 2022 on Dark Patterns.",
            score=0.03,
            retrieval_method="hybrid_rrf",
        )
        res1 = verifier.verify_response(
            "Under CCPA Guidelines 2022 on Dark Patterns, drip pricing is illegal.",
            [ccpa_chunk],
        )
        assert res1.hallucination_detected is False
        assert any("CCPA Guidelines" in c for c in res1.verified_citations)

        res2 = verifier.verify_response(
            "Under CCPA Guidelines 2022 on Dark Patterns, drip pricing is illegal.",
            [],
        )
        assert res2.hallucination_detected is True
        assert any("CCPA Guidelines" in c for c in res2.flagged_citations)

    def test_fabricated_subclauses_with_underscores_and_hyphens_flagged(
        self,
        verifier: CitationVerifier,
        sample_source_chunks: list[RetrievedChunk],
    ) -> None:
        """Verify non-alphanumeric subclauses are flagged and stripped appropriately."""
        text_underscore = "Under Section 2(47)(fake_subclause), seller is penalized."
        res_u = verifier.verify_response(text_underscore, sample_source_chunks, flag_mode="flag")
        assert res_u.hallucination_detected is True
        assert "Section 2(47)(fake_subclause)" in res_u.flagged_citations
        flagged_tag = "<flag>Section 2(47)(fake_subclause): Unverified citation</flag>"
        assert flagged_tag in res_u.cleaned_text

        text_hyphen = "Under Section 2(47)(fake-subclause), unfair trade applies."
        res_h = verifier.verify_response(text_hyphen, sample_source_chunks, flag_mode="strip")
        assert res_h.hallucination_detected is True
        assert "Section 2(47)(fake-subclause)" not in res_h.cleaned_text
        assert "[Citation omitted - unverified in statutory corpus]" in res_h.cleaned_text
