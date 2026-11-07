"""Comprehensive offline unit tests for 4 Legal Workflows (Modes 1 to 4).

Verifies 100% offline with zero external network dependencies:
1. Mode 1 Case Builder (CaseBuilder): Narrative intake (English, Hindi, Hinglish),
   currency sanitization, chronological timeline, evidence auditing.
2. Mode 2 Legal Advisor (LegalAdvisor): Section 2(7) standing, 2021 Pecuniary Rules forum,
   e-Daakhil court fees, Section 69 limitation, 4-step resolution ladder.
3. Mode 3 Document Drafter (DocumentDrafter): Grievance Escalation Email, 15-day Legal Notice,
   and 7-part e-Daakhil Complaint Petition markdown generation.
4. Mode 4 Opposing Counsel Simulator (OpposingCounselSimulator): Adversarial defense roleplay,
   argument scoring (0-100), statutory counter-arguments, and state machine transitions.

Execution time: < 2.5 seconds. Zero # noqa or # type: ignore comments.
"""

from __future__ import annotations

import pytest

from legal_assistant.schemas import (
    CaseFile,
    DraftedDocument,
    LegalStanding,
    OppositeParty,
    PartyDetails,
    PecuniaryForum,
    ScopeResult,
    SimulationSession,
    calculate_edaakhil_fee,
    check_limitation_status,
    determine_pecuniary_forum,
)
from legal_assistant.workflows.advisor import LegalAdvisor
from legal_assistant.workflows.case_builder import CaseBuilder, OutOfScopeDisputeError
from legal_assistant.workflows.drafter import DocumentDrafter
from legal_assistant.workflows.simulator import (
    ArgumentFeedback,
    DefenseTacticType,
    OpposingCounselSimulator,
    SimulatorState,
)

# ==============================================================================
# Mode 1: Case Builder Unit Tests
# ==============================================================================


class TestCaseBuilder:
    """Offline unit test suite for Mode 1 Case Builder."""

    @pytest.fixture
    def builder(self) -> CaseBuilder:
        """Provide a CaseBuilder instance."""
        return CaseBuilder()

    def test_english_narrative_to_casefile(self, builder: CaseBuilder) -> None:
        """Verify English dispute narrative extraction into structured CaseFile."""
        narrative = (
            "My name is Amit Sharma (amit@example.com, 9876543210), residing in New Delhi. "
            "On 2024-03-10, I ordered an ASUS ROG Strix gaming laptop from Flipkart "
            "(Flipkart Internet Pvt Ltd) for Rs. 84,999/-. Order ID OD123456789. "
            "The parcel arrived on 2024-03-14. When I opened the box, the screen was cracked "
            "and power cord was missing. I immediately contacted Flipkart customer care "
            "on 2024-03-14 requesting a replacement or refund, but on 2024-03-16 they rejected "
            "my request, stating their policy does not cover physical damage once delivered. "
            "I have the tax invoice #INV-9988 and delivery slip, "
            "but I do not have an unboxing video."
        )
        case_file: CaseFile = builder.build_case(narrative, use_llm=False)
        assert isinstance(case_file, CaseFile)
        assert case_file.disputed_amount_inr == 84999.0
        assert case_file.transaction_date == "2024-03-10"
        assert len(case_file.opposite_parties) >= 1
        assert "Flipkart" in case_file.opposite_parties[0].name
        assert len(case_file.timeline) >= 2
        assert any(e.is_available for e in case_file.evidence_checklist)
        assert any(m.importance != "" for m in case_file.missing_evidence)

    def test_hinglish_narrative_to_casefile(self, builder: CaseBuilder) -> None:
        """Verify Hinglish colloquial narrative extraction into structured CaseFile."""
        narrative = (
            "Mera naam Priya Verma hai. Maine 5 January 2024 ko Amazon se ek mixer grinder "
            "mangwaya tha ₹3,499 ka. 8 Jan ko delivery aayi to jar pehle se toota hua tha. "
            "Maine usi din return request daala par seller ne reject kar diya bola policy expired. "
            "Mera refund karwa do."
        )
        case_file = builder.build_case(narrative, use_llm=False)
        assert isinstance(case_file, CaseFile)
        assert case_file.disputed_amount_inr == 3499.0
        assert "Amazon" in case_file.opposite_parties[0].name or "Amazon" in case_file.facts_summary

    def test_empty_narrative_raises_value_error(self, builder: CaseBuilder) -> None:
        """Verify CaseBuilder raises ValueError when narrative is blank or whitespace."""
        with pytest.raises(ValueError, match="narrative cannot be empty"):
            builder.build_case("   ")

    def test_scope_checker_rejection(self) -> None:
        """Verify CaseBuilder rejects non-consumer narratives when scope checker flags them."""

        class MockScopeChecker:
            def check_scope(self, text: str) -> ScopeResult:
                return ScopeResult(
                    is_in_scope=False,
                    out_of_scope_category="criminal_offense",
                    escalation_advice="Consult police or an Advocate regarding criminal offenses.",
                )

        builder = CaseBuilder(scope_checker=MockScopeChecker())
        with pytest.raises(OutOfScopeDisputeError, match="criminal offenses") as exc_info:
            builder.build_case("Someone broke into my shop and stole all merchandise.")

        assert exc_info.value.scope_result is not None
        assert exc_info.value.scope_result.out_of_scope_category == "criminal_offense"

    def test_currency_sanitization(self) -> None:
        """Verify CaseFile parse_inr_amount handles varied currency notations."""
        assert CaseFile.parse_inr_amount("₹54,999/-") == 54999.0
        assert CaseFile.parse_inr_amount("Rs. 1,25,000.50") == 125000.5
        assert CaseFile.parse_inr_amount("INR 4500") == 4500.0
        assert CaseFile.parse_inr_amount(15000) == 15000.0


# ==============================================================================
# Mode 2: Legal Advisor Unit Tests
# ==============================================================================


class TestLegalAdvisor:
    """Offline unit test suite for Mode 2 Legal Advisor."""

    @pytest.fixture
    def advisor(self) -> LegalAdvisor:
        """Provide a LegalAdvisor instance."""
        return LegalAdvisor()

    @pytest.fixture
    def sample_case(self) -> CaseFile:
        """Provide standard test CaseFile."""
        return CaseFile(
            case_id="case_test_01",
            title="Defective Gaming Laptop Refund Refusal",
            complainant=PartyDetails(name="Amit Sharma", city="Delhi", state="Delhi"),
            opposite_parties=[
                OppositeParty(name="Flipkart Internet Pvt Ltd", role="E-Commerce Marketplace")
            ],
            transaction_date="2024-03-10",
            cause_of_action_date="2024-03-16",
            disputed_amount_inr=84999.0,
            compensation_claimed_inr=25000.0,
            facts_summary="Purchased laptop for Rs 84,999. Arrived defective. Refund refused.",
        )

    def test_standing_and_statutory_violations(
        self,
        advisor: LegalAdvisor,
        sample_case: CaseFile,
    ) -> None:
        """Verify legal standing and statutory violations under CPA 2019."""
        standing: LegalStanding = advisor.assess_standing(sample_case, use_llm=False)
        assert standing.is_consumer is True
        assert "Section 2(7)" in standing.consumer_rationale
        assert len(standing.statutory_violations) > 0
        violation_rules = [v.section_or_rule for v in standing.statutory_violations]
        assert any("2(11)" in r or "2(47)" in r or "Rule" in r for r in violation_rules)

    def test_pecuniary_forum_determination(self) -> None:
        """Verify 2021 Pecuniary Rules thresholds."""
        forum_dist, _ = determine_pecuniary_forum(45000.0)
        assert forum_dist == PecuniaryForum.DISTRICT_COMMISSION.value

        forum_dist_50l, _ = determine_pecuniary_forum(5_000_000.0)
        assert forum_dist_50l == PecuniaryForum.DISTRICT_COMMISSION.value

        forum_state, _ = determine_pecuniary_forum(7_500_000.0)
        assert forum_state == PecuniaryForum.STATE_COMMISSION.value

        forum_nat, _ = determine_pecuniary_forum(25_000_000.0)
        assert forum_nat == PecuniaryForum.NATIONAL_COMMISSION.value

    def test_edaakhil_court_fee_slabs(self) -> None:
        """Verify e-Daakhil official fee schedule."""
        assert calculate_edaakhil_fee(45000.0) == 0
        assert calculate_edaakhil_fee(500000.0) == 0
        assert calculate_edaakhil_fee(750000.0) == 200
        assert calculate_edaakhil_fee(1500000.0) == 400
        assert calculate_edaakhil_fee(3500000.0) == 1000

    def test_limitation_status_under_section_69(self) -> None:
        """Verify Section 69 CPA 2019 2-year limitation calculation."""
        is_within_60d, remaining_60d, _ = check_limitation_status(60)
        assert is_within_60d is True
        assert remaining_60d == 670

        is_within_800d, remaining_800d, rationale_800d = check_limitation_status(800)
        assert is_within_800d is False
        assert remaining_800d < 0
        assert "condonation of delay" in rationale_800d.lower()

    def test_four_step_resolution_ladder(
        self,
        advisor: LegalAdvisor,
        sample_case: CaseFile,
    ) -> None:
        """Verify standard 4-step escalation pathway is populated."""
        standing = advisor.assess_standing(sample_case, use_llm=False)
        assert len(standing.resolution_pathway) == 4
        steps = [s.forum_or_action for s in standing.resolution_pathway]
        assert any("Grievance" in s for s in steps)
        assert any("NCH" in s or "1915" in s for s in steps)
        assert any("Legal Notice" in s or "Demand Notice" in s for s in steps)
        assert any("e-Daakhil" in s or "Commission" in s for s in steps)


# ==============================================================================
# Mode 3: Document Drafter Unit Tests
# ==============================================================================


class TestDocumentDrafter:
    """Offline unit test suite for Mode 3 Document Drafter."""

    @pytest.fixture
    def drafter(self) -> DocumentDrafter:
        """Provide a DocumentDrafter instance."""
        return DocumentDrafter()

    @pytest.fixture
    def sample_case(self) -> CaseFile:
        """Provide standard test CaseFile."""
        return CaseFile(
            case_id="case_test_01",
            title="Defective Gaming Laptop Refund Refusal",
            complainant=PartyDetails(name="Amit Sharma", email="amit@example.com", city="Delhi"),
            opposite_parties=[
                OppositeParty(name="Flipkart Internet Pvt Ltd", role="E-Commerce Marketplace")
            ],
            transaction_date="2024-03-10",
            cause_of_action_date="2024-03-16",
            disputed_amount_inr=84999.0,
            compensation_claimed_inr=25000.0,
            facts_summary="Purchased laptop for Rs 84,999. Arrived defective. Refund refused.",
        )

    def test_draft_grievance_email(
        self,
        drafter: DocumentDrafter,
        sample_case: CaseFile,
    ) -> None:
        """Verify Grievance Escalation Email format and E-Commerce Rules citations."""
        doc: DraftedDocument = drafter.draft_document(
            sample_case, doc_type="grievance_email", use_llm=False
        )
        assert doc.document_type == "grievance_email"
        assert "Grievance" in doc.title or "Grievance" in doc.subject
        assert "Rule 4" in doc.body_markdown or "48 hours" in doc.body_markdown
        assert "30 days" in doc.body_markdown or "thirty (30) days" in doc.body_markdown

    def test_draft_15_day_legal_notice(
        self,
        drafter: DocumentDrafter,
        sample_case: CaseFile,
    ) -> None:
        """Verify 15-day formal Legal Notice demand letter format and clauses."""
        doc = drafter.draft_document(sample_case, doc_type="legal_notice", use_llm=False)
        assert doc.document_type == "legal_notice"
        assert "LEGAL NOTICE" in doc.title.upper() or "LEGAL NOTICE" in doc.body_markdown.upper()
        assert (
            "15 days" in doc.body_markdown.lower()
            or "fifteen (15) days" in doc.body_markdown.lower()
        )
        assert "84,999" in doc.body_markdown or "84999" in doc.body_markdown
        assert "e-Daakhil" in doc.body_markdown or "Consumer Commission" in doc.body_markdown

    def test_draft_edaakhil_complaint_petition(
        self,
        drafter: DocumentDrafter,
        sample_case: CaseFile,
    ) -> None:
        """Verify e-Daakhil Complaint conforms to 7-part NCDRC petition layout."""
        doc = drafter.draft_document(sample_case, doc_type="edaakhil_complaint", use_llm=False)
        assert doc.document_type == "edaakhil_complaint"
        body = doc.body_markdown
        assert "BEFORE THE HON'BLE DISTRICT CONSUMER DISPUTES REDRESSAL COMMISSION" in body.upper()
        assert "COMPLAINANT" in body.upper()
        assert "OPPOSITE PARTY" in body.upper()
        assert "STATEMENT OF MATERIAL FACTS" in body.upper() or "FACTS" in body.upper()
        assert "JURISDICTION" in body.upper()
        assert "PRAYER" in body.upper() or "RELIEF" in body.upper()
        assert "VERIFICATION" in body.upper()

    def test_draft_all(
        self,
        drafter: DocumentDrafter,
        sample_case: CaseFile,
    ) -> None:
        """Verify draft_all generates all 3 legal artifacts."""
        docs = drafter.draft_all(sample_case, use_llm=False)
        assert len(docs) == 3
        assert "grievance_email" in docs
        assert "legal_notice" in docs
        assert "edaakhil_complaint" in docs


# ==============================================================================
# Mode 4: Opposing Counsel Simulator Unit Tests
# ==============================================================================


class TestOpposingCounselSimulator:
    """Offline unit test suite for Mode 4 Opposing Counsel Simulator."""

    @pytest.fixture
    def simulator(self) -> OpposingCounselSimulator:
        """Provide an OpposingCounselSimulator instance."""
        return OpposingCounselSimulator()

    @pytest.fixture
    def sample_case(self) -> CaseFile:
        """Provide test CaseFile."""
        return CaseFile(
            case_id="case_sim_01",
            title="Broken TV Screen on Delivery",
            complainant=PartyDetails(name="Rahul Mehta", city="Mumbai"),
            opposite_parties=[
                OppositeParty(name="MegaStore E-Commerce", role="Marketplace Platform")
            ],
            transaction_date="2024-04-01",
            disputed_amount_inr=32000.0,
            facts_summary="TV arrived broken. Platform claims no refund under policy.",
        )

    def test_start_simulation_initializes_state(
        self,
        simulator: OpposingCounselSimulator,
        sample_case: CaseFile,
    ) -> None:
        """Verify start_simulation initializes state with Turn 1 from counsel."""
        state: SimulatorState = simulator.start_simulation(sample_case)
        assert isinstance(state, SimulatorState)
        assert state.case_id == "case_sim_01"
        assert state.turn_count == 1
        assert len(state.turns) == 1
        turn_1 = state.turns[0]
        assert turn_1.speaker == "opposing_counsel"
        assert turn_1.defense_tactic is not None
        assert len(turn_1.content) > 20

    def test_weak_consumer_response_scoring(
        self,
        simulator: OpposingCounselSimulator,
    ) -> None:
        """Verify emotional consumer argument without statutory grounding receives low score."""
        weak_rebuttal = (
            "This is completely unfair! You are a huge company looting common people. "
            "Give me my money back immediately!"
        )
        feedback: ArgumentFeedback = simulator.evaluate_consumer_argument(
            argument=weak_rebuttal,
            active_tactic=DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND,
        )
        assert feedback.score < 50.0
        assert len(feedback.statutory_sections_cited) == 0
        assert len(feedback.missing_statutory_sections) > 0
        assert (
            "Section 2(46)" in feedback.missing_statutory_sections
            or "Rule 6(5)" in feedback.missing_statutory_sections
        )
        assert len(feedback.flaws_in_merchant_defense) > 0
        assert len(feedback.suggested_counter_arguments) > 0

    def test_strong_statutory_consumer_response_scoring(
        self,
        simulator: OpposingCounselSimulator,
    ) -> None:
        """Verify rigorous statutory rebuttal receives high score and praise."""
        strong_rebuttal = (
            "Your 'no refunds under any circumstances' clause constitutes an 'unfair contract' "
            "under Section 2(46)(vi) of the Consumer Protection Act, 2019, which explicitly "
            "voids terms imposing unreasonable conditions putting the consumer at a disadvantage. "
            "Furthermore, Rule 6(5) and Rule 6(3) of the Consumer Protection (E-Commerce) "
            "Rules, 2020 strictly prohibit e-commerce marketplaces and sellers from refusing "
            "refunds for defective goods. Private terms cannot override statutory protections."
        )
        feedback = simulator.evaluate_consumer_argument(
            argument=strong_rebuttal,
            active_tactic=DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND,
        )
        assert feedback.score >= 80.0
        assert "Section 2(46)" in feedback.statutory_sections_cited
        assert any("Rule 6" in s for s in feedback.statutory_sections_cited)
        assert (
            "ready to present this position" in feedback.coaching_tip.lower()
            or "outstanding" in feedback.coaching_tip.lower()
        )

    def test_multi_turn_progression_and_pivot(
        self,
        simulator: OpposingCounselSimulator,
        sample_case: CaseFile,
    ) -> None:
        """Verify simulator steps forward, evaluates consumer, and generates counsel pivot."""
        state = simulator.start_simulation(
            sample_case,
            initial_tactic=DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND,
        )
        assert state.turn_count == 1

        consumer_arg = (
            "Clause 14 is an unfair contract under Section 2(46) of CPA 2019 and "
            "Rule 6(5) of E-Commerce Rules."
        )
        state_turn_2 = simulator.step_simulation(state, consumer_arg)
        # Should now have 3 turns: counsel T1, consumer T2, counsel T3
        assert state_turn_2.turn_count == 3
        assert state_turn_2.turns[1].speaker == "consumer"
        assert state_turn_2.turns[1].feedback is not None
        assert state_turn_2.turns[2].speaker == "opposing_counsel"
        assert (
            state_turn_2.turns[2].defense_tactic != DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND
        )

    def test_conclude_simulation_and_session_conversion(
        self,
        simulator: OpposingCounselSimulator,
        sample_case: CaseFile,
    ) -> None:
        """Verify simulation conclusion computes assessment and converts to SimulationSession."""
        state = simulator.start_simulation(sample_case)
        simulator.step_simulation(
            state,
            "Under Section 2(46) CPA 2019 and Rule 6(5) E-Commerce Rules, your terms are void.",
        )
        concluded_state = simulator.conclude_simulation(state)
        assert concluded_state.is_concluded is True
        assert concluded_state.final_assessment is not None
        assert "READINESS" in concluded_state.final_assessment.upper()

        # Check conversion to canonical schemas.SimulationSession
        session: SimulationSession = concluded_state.to_simulation_session()
        assert isinstance(session, SimulationSession)
        assert session.session_id == concluded_state.session_id
        assert len(session.turns) == len(concluded_state.turns)
        assert session.readiness_score == concluded_state.cumulative_score
