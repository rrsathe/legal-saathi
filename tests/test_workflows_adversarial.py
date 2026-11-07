"""Adversarial stress-test suite for Milestone 4 Legal Workflows (Modes 1 to 4).

Executed by m4_challenger_2 to challenge edge cases, pecuniary boundary limits,
fee schedule slabs, limitation calculation, multilingual Hinglish narrative intake,
document drafting adaptation, and opposing counsel debate simulations.
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from legal_assistant.guardrails.scope_checker import ScopeChecker
from legal_assistant.schemas import (
    CaseFile,
    OppositeParty,
    PartyDetails,
    PecuniaryForum,
    ScopeCategory,
    SimulationSession,
    calculate_edaakhil_fee,
    check_limitation_status,
    determine_pecuniary_forum,
)
from legal_assistant.workflows.advisor import LegalAdvisor
from legal_assistant.workflows.case_builder import CaseBuilder, OutOfScopeDisputeError
from legal_assistant.workflows.drafter import DocumentDrafter
from legal_assistant.workflows.simulator import (
    TACTIC_CATALOG,
    DefenseTacticType,
    OpposingCounselSimulator,
)

# ==============================================================================
# 1. Mode 1: CaseBuilder Adversarial Suite
# ==============================================================================


class TestMode1CaseBuilderAdversarial:
    """Adversarial challenges for Mode 1 Case Builder."""

    @pytest.fixture
    def builder(self) -> CaseBuilder:
        return CaseBuilder()

    def test_hinglish_phone_soap_narrative(self, builder: CaseBuilder) -> None:
        """Challenge: Hinglish phone-soap scam narrative intake."""
        narrative = "Flipkart se phone mangaya tha, dabbe me sabun nikla, 45,000/- kata"
        case = builder.build_case(narrative, use_llm=False)

        assert case.disputed_amount_inr == 45000.0
        assert any("flipkart" in p.name.lower() for p in case.opposite_parties)
        assert len(case.timeline) >= 1

        missing_names = {m.item_name.lower(): m.importance for m in case.missing_evidence}

        # Unboxing video absence must be tagged as high importance
        assert any("unboxing" in k and imp == "high" for k, imp in missing_names.items())

        # Tax invoice absence must be tagged as critical
        assert any("invoice" in k and imp == "critical" for k, imp in missing_names.items())

    def test_narrative_with_unboxing_video_present(self, builder: CaseBuilder) -> None:
        """Challenge: Consumer states unboxing video IS available."""
        narrative = (
            "I ordered an iPhone from Flipkart for Rs 65,000. Received a stone inside. "
            "I have an unboxing video recorded continuously from courier delivery."
        )
        case = builder.build_case(narrative, use_llm=False)
        assert case.disputed_amount_inr == 65000.0
        available_names = [e.item_name.lower() for e in case.evidence_checklist if e.is_available]
        assert any("unboxing" in name for name in available_names)

        # Should not be listed in missing evidence
        missing_names = [m.item_name.lower() for m in case.missing_evidence]
        assert not any("unboxing" in name for name in missing_names)

    def test_scope_checker_escalation_on_criminal_matter(self) -> None:
        """Challenge: CaseBuilder rejects criminal narrative with ScopeChecker."""
        checker = ScopeChecker()
        builder = CaseBuilder(scope_checker=checker)
        narrative = (
            "Someone broke into my shop at night and stole all inventory worth Rs 10 Lakhs. "
            "I want to file a police FIR under Bharatiya Nyaya Sanhita."
        )
        with pytest.raises(OutOfScopeDisputeError) as exc_info:
            builder.build_case(narrative, use_llm=False)

        res = exc_info.value.scope_result
        assert res is not None
        assert res.out_of_scope_category == ScopeCategory.CRIMINAL_OFFENSE.value
        adv = res.escalation_advice or ""
        assert "Police" in adv or "FIR" in adv

    def test_scope_checker_escalation_on_cheque_bounce(self) -> None:
        """Challenge: CaseBuilder rejects NI Act 138 cheque bounce dispute."""
        checker = ScopeChecker()
        builder = CaseBuilder(scope_checker=checker)
        narrative = (
            "A client issued a cheque of Rs 2,50,000 which bounced due to insufficient funds. "
            "I want to send a statutory notice under Section 138 Negotiable Instruments Act."
        )
        with pytest.raises(OutOfScopeDisputeError) as exc_info:
            builder.build_case(narrative, use_llm=False)

        res = exc_info.value.scope_result
        assert res is not None
        assert res.out_of_scope_category == ScopeCategory.CHEQUE_BOUNCE.value

    def test_whitespace_and_empty_narrative_rejection(self, builder: CaseBuilder) -> None:
        """Challenge: Whitespace, tabs, and newlines must raise ValueError."""
        with pytest.raises(ValueError, match="narrative cannot be empty"):
            builder.build_case("   \t\n   ", use_llm=False)


# ==============================================================================
# 2. Mode 2: LegalAdvisor Adversarial Suite
# ==============================================================================


class TestMode2LegalAdvisorAdversarial:
    """Adversarial challenges for Mode 2 Legal Advisor."""

    @pytest.fixture
    def advisor(self) -> LegalAdvisor:
        return LegalAdvisor()

    @pytest.mark.parametrize(
        ("amount", "expected_forum"),
        [
            (0.0, PecuniaryForum.DISTRICT_COMMISSION.value),
            (100.0, PecuniaryForum.DISTRICT_COMMISSION.value),
            (4_999_999.0, PecuniaryForum.DISTRICT_COMMISSION.value),
            (5_000_000.0, PecuniaryForum.DISTRICT_COMMISSION.value),
            (5_000_001.0, PecuniaryForum.STATE_COMMISSION.value),
            (19_999_999.0, PecuniaryForum.STATE_COMMISSION.value),
            (20_000_000.0, PecuniaryForum.STATE_COMMISSION.value),
            (20_000_001.0, PecuniaryForum.NATIONAL_COMMISSION.value),
            (100_000_000.0, PecuniaryForum.NATIONAL_COMMISSION.value),
        ],
    )
    def test_pecuniary_boundaries_2021_rules(self, amount: float, expected_forum: str) -> None:
        """Challenge: 2021 Pecuniary Rules exact boundary stress testing."""
        forum, rationale = determine_pecuniary_forum(amount)
        assert forum == expected_forum
        assert "2021" in rationale

    @pytest.mark.parametrize(
        ("amount", "expected_fee"),
        [
            (0.0, 0),
            (500_000.0, 0),
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
            (50_000_000.0, 4000),
            (70_000_000.0, 5000),
            (90_000_000.0, 6000),
            (150_000_000.0, 7500),
        ],
    )
    def test_edaakhil_fee_schedule_slabs(self, amount: float, expected_fee: int) -> None:
        """Challenge: e-Daakhil court fee calculations across all slabs."""
        assert calculate_edaakhil_fee(amount) == expected_fee

    def test_section_69_limitation_boundaries(self) -> None:
        """Challenge: Exact 730-day Section 69 limitation period boundaries."""
        # 729 days: within limitation, 1 day left
        is_in, rem, _ = check_limitation_status(729)
        assert is_in is True
        assert rem == 1

        # 730 days: exactly on deadline, 0 days left
        is_in, rem, rat = check_limitation_status(730)
        assert is_in is True
        assert rem == 0
        assert "URGENT" in rat or "expiring soon" in rat

        # 731 days: barred by limitation, requires condonation of delay
        is_in, rem, rat = check_limitation_status(731)
        assert is_in is False
        assert rem == -1
        assert "condonation of delay" in rat.lower()
        assert "Section 69(2)" in rat

    def test_section_69_iso_date_calculation(self) -> None:
        """Challenge: ISO date string limitation checking against current date."""
        today = date.today()
        coa_valid = (today - timedelta(days=200)).isoformat()
        coa_expired = (today - timedelta(days=750)).isoformat()

        is_valid, rem_valid, _ = check_limitation_status(coa_valid)
        assert is_valid is True
        assert rem_valid == 530

        is_expired, rem_expired, _ = check_limitation_status(coa_expired)
        assert is_expired is False
        assert rem_expired == -20

    def test_four_step_resolution_ladder_structure(self, advisor: LegalAdvisor) -> None:
        """Challenge: Verify exact 4-step sequence (Grievance -> NCH -> Notice -> Court)."""
        case = CaseFile(
            title="E-Commerce Dispute",
            complainant=PartyDetails(name="Sunita"),
            opposite_parties=[OppositeParty(name="Amazon", role="Marketplace")],
            transaction_date="2024-01-01",
            disputed_amount_inr=15000.0,
            facts_summary="Defective product received.",
        )
        standing = advisor.assess_standing(case, use_llm=False)
        assert len(standing.resolution_pathway) == 4

        step1, step2, step3, step4 = standing.resolution_pathway
        assert step1.step_number == 1 and "Grievance" in step1.forum_or_action
        assert step2.step_number == 2 and (
            "NCH" in step2.forum_or_action or "1915" in step2.forum_or_action
        )
        assert step3.step_number == 3 and "Legal Notice" in step3.forum_or_action
        assert step4.step_number == 4 and "e-Daakhil" in step4.forum_or_action


# ==============================================================================
# 3. Mode 3: DocumentDrafter Adversarial Suite
# ==============================================================================


class TestMode3DocumentDrafterAdversarial:
    """Adversarial challenges for Mode 3 Document Drafter."""

    @pytest.fixture
    def drafter(self) -> DocumentDrafter:
        return DocumentDrafter()

    @pytest.fixture
    def high_value_case(self) -> CaseFile:
        return CaseFile(
            case_id="case_high_val",
            title="Luxury Vehicle Defect Dispute",
            complainant=PartyDetails(
                name="Vikramaditya Singhania",
                email="vikram@example.com",
                phone="9811122233",
                city="Mumbai",
                state="Maharashtra",
            ),
            opposite_parties=[
                OppositeParty(
                    name="Apex Motors Ltd", role="Seller", entity_type="authorized_seller"
                ),
                OppositeParty(
                    name="AutoGlobal Marketplace",
                    role="E-Commerce Marketplace",
                    entity_type="marketplace",
                ),
            ],
            transaction_date="2024-01-10",
            cause_of_action_date="2024-01-20",
            disputed_amount_inr=7_500_000.0,  # 75 Lakhs -> State Commission
            compensation_claimed_inr=500_000.0,
            facts_summary=(
                "Delivered vehicle with catastrophic transmission failure. Refund denied."
            ),
        )

    def test_grievance_email_statutory_mandates(
        self, drafter: DocumentDrafter, high_value_case: CaseFile
    ) -> None:
        """Challenge: Grievance email must strictly cite Rule 4(4), Rule 4(5), 48h, 30d."""
        doc = drafter.draft_document(high_value_case, "grievance_email", use_llm=False)
        body = doc.body_markdown

        assert "Rule 4(4)" in body or "Rule 4" in body
        assert "Rule 4(5)" in body or "4(5)" in body
        assert "48 hours" in body.lower() or "forty-eight (48) hours" in body.lower()
        assert "30 days" in body.lower() or "thirty (30) days" in body.lower()
        assert "7,500,000" in body or "75,00,000" in body or "7500000" in body

    def test_legal_notice_15_day_speed_post_mandates(
        self, drafter: DocumentDrafter, high_value_case: CaseFile
    ) -> None:
        """Challenge: 15-day Legal Notice must cite Speed Post/RPAD, 15 days, e-Daakhil."""
        doc = drafter.draft_document(high_value_case, "legal_notice", use_llm=False)
        body = doc.body_markdown

        assert "speed post" in body.lower()
        has_ad = (
            "acknowledgment due" in body.lower()
            or "acknowledgement due" in body.lower()
            or "rpad" in body.lower()
        )
        assert has_ad
        assert "15 days" in body.lower() or "fifteen (15) days" in body.lower()
        assert "e-daakhil" in body.lower()
        assert "Apex Motors" in body
        assert "AutoGlobal" in body

    def test_edaakhil_complaint_7_part_structure(
        self, drafter: DocumentDrafter, high_value_case: CaseFile
    ) -> None:
        """Challenge: e-Daakhil complaint must strictly exhibit 7 formal parts and verification."""
        doc = drafter.draft_document(high_value_case, "edaakhil_complaint", use_llm=False)
        body = doc.body_markdown

        required_parts = [
            "PART I: MEMO OF PARTIES",
            "PART II: INDEX OF DOCUMENTS",
            "PART III: STATEMENT OF MATERIAL FACTS",
            "PART IV: STATUTORY GROUNDS OF CLAIM",
            "PART V: PECUNIARY & TERRITORIAL JURISDICTION",
            "PART VI: LIMITATION STATEMENT (SECTION 69)",
            "PART VII: PRAYER / RELIEF SOUGHT",
        ]
        for part in required_parts:
            assert part in body, f"Missing required petition structure: {part}"

        assert "VERIFICATION" in body or "SOLEMN AFFIDAVIT" in body
        assert doc.verification_statement is not None
        assert "Vikramaditya Singhania" in doc.verification_statement

    def test_unsupported_document_type_raises_value_error(
        self, drafter: DocumentDrafter, high_value_case: CaseFile
    ) -> None:
        """Challenge: Invalid document type raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported document type"):
            drafter.draft_document(high_value_case, "criminal_bail_application", use_llm=False)


# ==============================================================================
# 4. Mode 4: OpposingCounselSimulator Adversarial Suite
# ==============================================================================


class TestMode4OpposingCounselSimulatorAdversarial:
    """Adversarial challenges for Mode 4 Opposing Counsel Simulator."""

    @pytest.fixture
    def simulator(self) -> OpposingCounselSimulator:
        return OpposingCounselSimulator()

    @pytest.fixture
    def test_case(self) -> CaseFile:
        return CaseFile(
            case_id="case_sim_adv",
            title="Defective Air Conditioner",
            complainant=PartyDetails(name="Ananya Roy", city="Kolkata"),
            opposite_parties=[
                OppositeParty(name="CoolMart E-Commerce", role="Marketplace Platform")
            ],
            transaction_date="2024-05-01",
            disputed_amount_inr=42000.0,
            facts_summary=(
                "AC compressor failed within 24 hours of delivery. Platform refuses refund."
            ),
        )

    def test_all_four_corporate_defenses_present(self) -> None:
        """Challenge: Ensure all 4 mandatory merchant defenses are defined with arguments."""
        expected = [
            DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND,
            DefenseTacticType.UNBOXING_VIDEO_ABSENCE,
            DefenseTacticType.IT_ACT_SECTION_79_SAFE_HARBOR,
            DefenseTacticType.THIRD_PARTY_LOGISTICS_MANUFACTURER,
        ]
        for tactic in expected:
            assert tactic in TACTIC_CATALOG
            profile = TACTIC_CATALOG[tactic]
            assert len(profile.sample_arguments) >= 1
            assert len(profile.essential_statutes) >= 2
            assert len(profile.defense_flaws) >= 2
            assert len(profile.winning_counter_points) >= 2

    def test_weak_colloquial_argument_scoring(self, simulator: OpposingCounselSimulator) -> None:
        """Challenge: Emotional argument without statutes must score < 40."""
        weak_arg = (
            "You fraudster platform looting common consumers! Give my 42000 back immediately!"
        )
        fb = simulator.evaluate_consumer_argument(
            argument=weak_arg,
            active_tactic=DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND,
        )
        assert fb.score < 40.0
        assert len(fb.statutory_sections_cited) == 0
        assert len(fb.missing_statutory_sections) > 0
        tip = fb.coaching_tip.lower()
        assert "avoid emotional pleas" in tip or "weak" in tip

    def test_strong_statutory_rebuttal_scoring(self, simulator: OpposingCounselSimulator) -> None:
        """Challenge: Rigorous rebuttal citing Rule 6(5) and Section 2(46) must score >= 75."""
        strong_arg = (
            "Clause 14 of your policy is an unfair contract under Section 2(46) of the Consumer "
            "Protection Act, 2019, which explicitly voids one-sided terms imposing unreasonable "
            "disadvantages on consumers. Moreover, Rule 6(5) and Rule 6(3) of the Consumer "
            "Protection (E-Commerce) Rules, 2020 strictly prohibit e-commerce platforms and "
            "sellers from refusing refund for defective goods."
        )
        fb = simulator.evaluate_consumer_argument(
            argument=strong_arg,
            active_tactic=DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND,
        )
        assert fb.score >= 75.0
        assert "Section 2(46)" in fb.statutory_sections_cited
        assert any("Rule 6" in s for s in fb.statutory_sections_cited)

    def test_safe_harbor_rebuttal_scoring(self, simulator: OpposingCounselSimulator) -> None:
        """Challenge: Rebuttal against IT Act Section 79 safe harbor invoking Section 86."""
        safe_harbor_rebuttal = (
            "Under Section 86 of the Consumer Protection Act, 2019, an e-commerce platform that "
            "exercises control over payments and order fulfilment is directly subject to product "
            "liability. Intermediary safe harbor under Section 79 of the Information Technology "
            "Act, 2000 does not grant immunity from affirmative duties under the E-Commerce Rules."
        )
        fb = simulator.evaluate_consumer_argument(
            argument=safe_harbor_rebuttal,
            active_tactic=DefenseTacticType.IT_ACT_SECTION_79_SAFE_HARBOR,
        )
        assert fb.score >= 75.0
        assert any("Section 86" in s or "86" in s for s in fb.statutory_sections_cited)

    def test_multi_turn_progression_and_session_export(
        self, simulator: OpposingCounselSimulator, test_case: CaseFile
    ) -> None:
        """Challenge: Multi-turn debate progression and export to SimulationSession."""
        state = simulator.start_simulation(
            test_case, initial_tactic=DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND
        )
        assert state.turn_count == 1
        assert state.turns[0].defense_tactic == DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND

        # Turn 2: Consumer answers
        consumer_reply = (
            "Under Section 2(46) CPA 2019 and Rule 6(5) of E-Commerce Rules, "
            "no-refund policies are void."
        )
        state_t2 = simulator.step_simulation(state, consumer_reply)
        assert state_t2.turn_count == 3
        assert state_t2.turns[1].speaker == "consumer"
        assert state_t2.turns[1].feedback is not None
        assert state_t2.turns[2].speaker == "opposing_counsel"
        # Opponent should pivot to another tactic
        assert state_t2.turns[2].defense_tactic != DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND

        # Conclude and verify session export
        concluded_state = simulator.conclude_simulation(state_t2)
        assert concluded_state.is_concluded is True
        session: SimulationSession = concluded_state.to_simulation_session()
        assert isinstance(session, SimulationSession)
        assert session.session_id == concluded_state.session_id
        assert len(session.turns) == 3
        assert session.readiness_score == concluded_state.cumulative_score
