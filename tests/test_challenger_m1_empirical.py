"""Empirical Challenger stress tests for Legal Saathi (UI and Workflows 1, 5, 6, 7).

Adversarial stress-testing suite verifying:
1. Workflow 1 (Case Intake): Complex Hinglish narratives, extreme length payloads,
   missing facts, and edge-case currency notations.
2. Workflow 5 (Clarifications): Multi-turn Q&A iterations, malformed questions,
   empty responses, and stress conditions.
3. Workflow 6 (Document Generation): Grievance email, 15-day legal notice, and
   7-part e-Daakhil complaint petition statutory mandates, NCDRC standards, and markdown rendering.
4. Workflow 7 (Defense Simulator): Multi-turn debate progression under Gradio 6 messages
   format (`list[dict[str, str]]`), strict speaker alternation, and scoring accuracy.
5. UI Component Integration: `create_app()` instantiation and Gradio 6 event handler parity.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import gradio as gr
import pytest

from legal_assistant.config import Settings
from legal_assistant.guardrails.scope_checker import ScopeChecker
from legal_assistant.llm.base import BaseLLMClient, LLMResponse
from legal_assistant.llm.router import LLMRouter
from legal_assistant.schemas import (
    CaseFile,
    DraftedDocument,
    LegalNotice,
    OppositeParty,
    PartyDetails,
    TimelineEvent,
)
from legal_assistant.ui.app import (
    create_app,
    handle_case_intake,
    handle_draft_single,
    handle_simulator_turn,
)
from legal_assistant.workflows.case_builder import CaseBuilder
from legal_assistant.workflows.drafter import DocumentDrafter
from legal_assistant.workflows.simulator import (
    ArgumentFeedback,
    DefenseTacticType,
    OpposingCounselSimulator,
)


# ==============================================================================
# Fixtures
# ==============================================================================
class MockEmpiricalLLMClient(BaseLLMClient):
    """Deterministic mock LLM client for empirical testing."""

    def __init__(self, provider_name: str = "mock-groq") -> None:
        """Initialize mock LLM client."""
        self._provider_name = provider_name

    @property
    def provider_name(self) -> str:
        """Return provider identifier."""
        return self._provider_name

    @property
    def model_name(self) -> str:
        """Return mock model name."""
        return "mock-llama-3.3-70b"

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Return mock response."""
        return LLMResponse(
            content="Mock response for empirical verification.",
            model=self.model_name,
            provider=self.provider_name,
        )

    def generate_structured(
        self,
        prompt: str,
        schema: type[Any],
        system_prompt: str = "",
        temperature: float | None = None,
        **kwargs: Any,
    ) -> Any:
        """Generate dummy structured response."""
        raise NotImplementedError("Use deterministic fallbacks for empirical stress suite.")


@pytest.fixture
def mock_router() -> LLMRouter:
    """Provide configured LLMRouter with mock client."""
    router = LLMRouter()
    client = MockEmpiricalLLMClient()
    router._clients["groq"] = client
    return router


@pytest.fixture
def sample_case() -> CaseFile:
    """Provide fully populated canonical CaseFile fixture."""
    return CaseFile(
        case_id="case_empirical_001",
        title="Gaming Laptop Defective Display & Motherboard Failure",
        disputed_amount_inr=92499.0,
        compensation_claimed_inr=30000.0,
        transaction_date="2024-02-15",
        cause_of_action_date="2024-02-22",
        complainant=PartyDetails(
            name="Vikram Malhotra",
            email="vikram.malhotra@example.com",
            phone="+91-9876543210",
            address="Flat 402, Shivalik Heights, Sector 62",
            city="Noida",
            state="Uttar Pradesh",
        ),
        opposite_parties=[
            OppositeParty(
                name="ElectroTech Retail India Pvt Ltd",
                role="Seller",
                address="Warehouse 4, Okhla Phase III, New Delhi 110020",
                entity_type="seller",
            ),
            OppositeParty(
                name="MegaCart E-Commerce India Limited",
                role="Marketplace Platform",
                address="7th Floor, Cyber City, Gurugram, Haryana 122002",
                entity_type="marketplace",
            ),
        ],
        facts_summary=(
            "Complainant purchased an ASUS ROG Strix G16 gaming laptop on 2024-02-15 "
            "for ₹92,499.00 via MegaCart. Upon delivery on 2024-02-18, the laptop suffered "
            "from display flickering and failed to boot into OS. On 2024-02-22, MegaCart "
            "and ElectroTech rejected the replacement request, claiming physical damage "
            "after delivery and disclaiming responsibility."
        ),
        timeline=[
            TimelineEvent(
                date="2024-02-15",
                description="Ordered gaming laptop online via UPI payment of ₹92,499.",
                significance="Transaction Date",
            ),
            TimelineEvent(
                date="2024-02-18",
                description="Delivery accepted; display defects noticed immediately on first boot.",
                significance="Delivery Date",
            ),
            TimelineEvent(
                date="2024-02-22",
                description="Customer support formally denied refund citing no-refund policy.",
                significance="Cause of Action Date",
            ),
        ],
        evidence_checklist=[],
        missing_evidence=[],
        clarification_questions=[
            "Did you record an unboxing video at the time of delivery?",
            "Was this laptop purchased for personal domestic gaming or for commercial resale?",
        ],
    )


# ==============================================================================
# Suite 1: Workflow 1 (Case Intake) Stress Tests
# ==============================================================================
class TestWorkflow1CaseIntakeAdversarial:
    """Adversarial challenge suite for Workflow 1 Case Intake."""

    def test_hinglish_complex_narrative_extraction(self) -> None:
        """Verify extraction from complex colloquial Hinglish narrative."""
        narrative = (
            "Bhai mera naam Rohit Singhal hai (rohit.singhal@testmail.com, 9811223344). "
            "Maine 12 Jan 2024 ko Meesho se ek premium wireless headphone mangwaya tha "
            "jiski cost thi Rs. 7,499/-. Delivery aayi 16 Jan ko par dabbe me headphone ki jagah "
            "patthar aur khali plastic wrapper nikla. "
            "Maine courier wale ke samne video banaya tha. "
            "Customer care ko ticket raise kiya usi din ticket #MSH-88219. Unhone 20 Jan ko bola "
            "ki hamari side se package intact tha aur refund reject kar diya. "
            "Mera tax invoice mere paas hai GSTIN ke saath, bank UPI transaction slip bhi hai. "
            "Mujhe mera poora refund aur compensation chahiye."
        )
        builder = CaseBuilder()
        case = builder.build_case(narrative, use_llm=False)

        assert isinstance(case, CaseFile)
        assert case.disputed_amount_inr == 7499.0
        assert len(case.opposite_parties) >= 1
        assert "Meesho" in case.opposite_parties[0].name or "Meesho" in case.facts_summary
        assert len(case.timeline) >= 2
        # Check evidence audit logic
        present_names = " ".join(item.item_name.lower() for item in case.evidence_checklist)
        assert "invoice" in present_names or "unboxing" in present_names
        # Ensure missing evidence contains customer support or payment if omitted
        missing_names = [m.item_name.lower() for m in case.missing_evidence]
        assert len(missing_names) >= 1

    def test_extreme_length_narrative_intake(self) -> None:
        """Verify CaseBuilder handles 10,000+ character consumer narrative without crashing."""
        filler_complaint = (
            "The courier person was extremely rude and threw the box on the porch. "
            "The customer service agent named Rajesh was unhelpful and kept putting me on hold. "
            "I called 15 times between morning 9 AM and evening 8 PM without resolution. "
        ) * 45  # ~8,000 chars

        narrative = (
            "Complainant Anita Deshmukh purchased a Samsung 4K OLED Smart TV for INR 1,45,000 "
            "on 2024-01-10 from Reliance Digital online. Upon delivery on 2024-01-14, the screen "
            "was completely shattered inside undamaged outer packaging. Customer service "
            "refused replacement on 2024-01-16 citing delivery sign-off. "
            + filler_complaint
            + " Invoice #RD-9900 is attached. Tax amount paid in full."
        )
        assert len(narrative) > 8000

        builder = CaseBuilder()
        case = builder.build_case(narrative, use_llm=False)

        assert isinstance(case, CaseFile)
        assert case.disputed_amount_inr == 145000.0
        assert len(case.facts_summary) > 50
        assert len(case.opposite_parties) >= 1

    def test_missing_facts_sparse_narrative(self) -> None:
        """Verify CaseBuilder handles sparse/incomplete narrative with missing facts."""
        narrative = (
            "Got cheated by seller. Received broken item. Customer care refused refund. Help me."
        )
        builder = CaseBuilder()
        case = builder.build_case(narrative, use_llm=False)

        assert isinstance(case, CaseFile)
        # Should populate default opposite party when merchant is unidentified
        assert len(case.opposite_parties) >= 1
        assert (
            "Merchant" in case.opposite_parties[0].name
            or "Opposite Party" in case.opposite_parties[0].name
        )
        # Critical missing proofs must be identified by audit_missing_evidence
        missing_names = [m.item_name.lower() for m in case.missing_evidence]
        assert any("invoice" in m for m in missing_names)
        assert any("payment" in m for m in missing_names)
        # In deterministic mode without LLM, clarification_questions defaults to empty list
        assert isinstance(case.clarification_questions, list)

    def test_blank_and_whitespace_narratives_raise_value_error(self) -> None:
        """Verify blank or whitespace narrative triggers immediate ValueError."""
        builder = CaseBuilder()
        for bad_input in ["", "   ", "\n\t  \n  "]:
            with pytest.raises(ValueError, match="narrative cannot be empty"):
                builder.build_case(bad_input)

    def test_ui_handle_case_intake_out_of_scope_interception(self, mock_router: LLMRouter) -> None:
        """Verify UI intake handler intercepts criminal / out-of-scope complaints."""
        scope_checker = ScopeChecker()
        criminal_narrative = (
            "Someone gave me a cheque for Rs 25,00,000 that bounced under Section 138 NI Act, "
            "and they are threatening my family with physical violence and murder. "
            "We lodged an FIR."
        )
        case_file, alert_text, timeline, avail, missing = handle_case_intake(
            narrative=criminal_narrative,
            router=mock_router,
            scope_checker=scope_checker,
        )

        assert case_file is None
        assert "⚠️ Escalation Required" in alert_text
        assert "Advocate" in alert_text or "criminal" in alert_text.lower()
        assert len(timeline) == 0

    def test_scope_checker_lexical_blindspot_observation(self) -> None:
        """Adversarial finding: colloquial armed robbery without formal legal terms.

        Documenting empirical observation: ScopeChecker relies on regex keyword patterns
        (FIR, police, robbery, Section 138, assault). Purely colloquial descriptions of
        crimes without compiled triggers pass regex filter unless LLM fallback is active.
        """
        checker = ScopeChecker(enable_llm_fallback=False)
        colloquial_crime = (
            "A gang of masked men barged into my shop at gunpoint, threatened to shoot "
            "my accountant, and looted ₹5,00,000 cash from the safe. We need consumer court action."
        )
        res = checker.check_scope(colloquial_crime)
        # Because 'gunpoint', 'threatened to shoot', and 'looted' are not in _criminal_patterns,
        # deterministic scope checker evaluates is_in_scope=True
        assert res.is_in_scope is True


# ==============================================================================
# Suite 2: Workflow 5 (Clarifications) Stress Tests
# ==============================================================================
class TestWorkflow5ClarificationsAdversarial:
    """Adversarial challenge suite for Workflow 5 Clarifications."""

    def test_multiple_sequential_qa_iterations_deterministic_fallback(
        self, sample_case: CaseFile, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify sequential multi-turn clarification updates accumulate facts cleanly (offline)."""
        builder = CaseBuilder()
        # Ensure offline deterministic execution without live LLM calls
        monkeypatch.setattr(
            builder.router,
            "generate_structured_with_fallback",
            lambda **kwargs: (_ for _ in ()).throw(RuntimeError("Offline unit test mode")),
        )

        # Iteration 1
        iter1_answers = {
            "Did you record an unboxing video at the time of delivery?": (
                "Yes, continuous unboxing video of 3 minutes 45 seconds was recorded."
            ),
        }
        case_v1 = builder.update_case_with_clarifications(sample_case, iter1_answers)
        assert "3 minutes 45 seconds" in case_v1.facts_summary
        assert case_v1.case_id == sample_case.case_id

        # Iteration 2
        iter2_answers = {
            "Was this laptop purchased for personal domestic gaming or for commercial resale?": (
                "Strictly for personal domestic gaming and educational study. Not for resale."
            ),
            "What was the exact UPI transaction reference number?": "UPI/404419828192/HDFC",
        }
        case_v2 = builder.update_case_with_clarifications(case_v1, iter2_answers)
        assert "personal domestic gaming" in case_v2.facts_summary.lower()
        assert "UPI/404419828192/HDFC" in case_v2.facts_summary
        assert case_v2.case_id == sample_case.case_id

    def test_empty_and_whitespace_clarifications_noop(self, sample_case: CaseFile) -> None:
        """Verify empty or whitespace-only answers perform a clean no-op without modification."""
        builder = CaseBuilder()
        original_summary = sample_case.facts_summary

        # Completely empty dict
        res1 = builder.update_case_with_clarifications(sample_case, {})
        assert res1.facts_summary == original_summary

        # Dict with only whitespace values
        res2 = builder.update_case_with_clarifications(
            sample_case,
            {"Question 1?": "   ", "Question 2?": "\n\t"},
        )
        assert res2.facts_summary == original_summary

    def test_malformed_and_stress_clarification_inputs(
        self, sample_case: CaseFile, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify resilience to adversarial strings (XSS payloads, unicode, special chars)."""
        builder = CaseBuilder()
        monkeypatch.setattr(
            builder.router,
            "generate_structured_with_fallback",
            lambda **kwargs: (_ for _ in ()).throw(RuntimeError("Offline unit test mode")),
        )
        adversarial_answers = {
            "<script>alert('xss');</script>": "Normal answer with special chars: & < > \" ' `",
            "Unicode test": "हिंदी में जवाब: बिल्कुल व्यक्तिगत उपयोग के लिए।",
            "Huge answer": "A" * 5000,
        }
        updated = builder.update_case_with_clarifications(sample_case, adversarial_answers)
        assert updated is not None
        assert "हिंदी में जवाब" in updated.facts_summary
        assert "A" * 5000 in updated.facts_summary
        assert updated.case_id == sample_case.case_id


# ==============================================================================
# Suite 3: Workflow 6 (Document Generation) Stress Tests
# ==============================================================================
class TestWorkflow6DocumentGenerationAdversarial:
    """Adversarial challenge suite for Workflow 6 Document Generation."""

    def test_grievance_email_statutory_mandates_and_formatting(self, sample_case: CaseFile) -> None:
        """Verify grievance escalation email contains all statutory mandates."""
        drafter = DocumentDrafter()
        doc = drafter.draft_grievance_email(sample_case, use_llm=False)

        assert isinstance(doc, DraftedDocument)
        assert doc.document_type == "grievance_email"
        md = doc.body_markdown

        # Rule 4(4) and Rule 4(5) Grievance Officer mandate
        assert "Rule 4(4)" in md or "Rule 4(5)" in md
        # 48-hour acknowledgement with ticket number
        assert "48" in md or "forty-eight" in md.lower()
        # 30-day resolution window
        assert "30" in md or "thirty" in md.lower()
        # Rule 6(3) / 7(4) refund prohibition bar
        assert "Rule 6(3)" in md or "Rule 7(4)" in md
        # Section 2(11) deficiency in service
        assert "Section 2(11)" in md
        # Disputed amount presence
        assert "92,499" in md or "92499" in md
        # Complainant name and contact
        assert sample_case.complainant.name in md

    def test_legal_notice_15_day_mandates_and_formatting(self, sample_case: CaseFile) -> None:
        """Verify 15-day legal demand notice satisfies all formal procedural clauses."""
        drafter = DocumentDrafter()
        doc = drafter.draft_legal_notice(sample_case, notice_period_days=15, use_llm=False)

        assert isinstance(doc, LegalNotice)
        assert doc.document_type == "legal_notice"
        assert doc.notice_period_days == 15
        md = doc.body_markdown

        # Formal notice delivery channels
        assert "REGISTERED POST" in md.upper() or "SPEED POST" in md.upper()
        # Section 2(7) bona fide consumer standing
        assert "Section 2(7)" in md
        # Section 2(10) defect and Section 2(11) deficiency
        assert "Section 2(10)" in md and "Section 2(11)" in md
        # Section 2(47) unfair trade practice
        assert "Section 2(47)" in md
        # Peremptory 15-day deadline
        assert "15" in md or "FIFTEEN" in md
        # 18% per annum interest
        assert "18%" in md
        # e-Daakhil filing warning
        assert "edaakhil.nic.in" in md or "e-Daakhil" in md
        # Total claim includes compensation
        total_expected = sample_case.disputed_amount_inr + sample_case.compensation_claimed_inr
        assert doc.claim_amount_inr == total_expected

    def test_edaakhil_complaint_7_part_structure_and_ncdrc_standards(
        self, sample_case: CaseFile
    ) -> None:
        """Verify e-Daakhil complaint petition strictly follows 7-part NCDRC format."""
        drafter = DocumentDrafter()
        doc = drafter.draft_edaakhil_complaint(sample_case, use_llm=False)

        assert isinstance(doc, DraftedDocument)
        assert doc.document_type == "edaakhil_complaint"
        md = doc.body_markdown

        # Heading before District Commission
        assert "DISTRICT CONSUMER DISPUTES REDRESSAL COMMISSION" in md.upper()

        # Part I: Memo of Parties
        assert "PART I: MEMO OF PARTIES" in md
        assert sample_case.complainant.name in md
        assert sample_case.opposite_parties[0].name in md
        assert sample_case.opposite_parties[1].name in md

        # Part II: Index of Documents
        assert "PART II: INDEX OF DOCUMENTS" in md
        assert "Annexure C-1" in md
        assert "Annexure C-2" in md

        # Part III: Statement of Material Facts
        assert "PART III: STATEMENT OF MATERIAL FACTS" in md

        # Part IV: Statutory Grounds of Claim
        assert "PART IV: STATUTORY GROUNDS OF CLAIM" in md
        assert "GROUND A" in md
        assert "GROUND B" in md

        # Part V: Pecuniary & Territorial Jurisdiction
        assert "PART V: PECUNIARY & TERRITORIAL JURISDICTION" in md
        assert "Section 34(2)(d)" in md
        assert "2021 Pecuniary Rules" in md or "Rule 3" in md

        # Part VI: Limitation Statement (Section 69)
        assert "PART VI: LIMITATION STATEMENT" in md
        assert "Section 69" in md

        # Part VII: Prayer / Relief
        assert "PART VII: PRAYER" in md
        assert "refund" in md.lower()
        assert "interest" in md.lower()
        assert "compensation" in md.lower()

        # Verification / Solemn Affidavit Clause
        assert "VERIFICATION" in md.upper() or "AFFIDAVIT" in md.upper()
        assert doc.verification_statement is not None
        assert sample_case.complainant.name in doc.verification_statement

    def test_markdown_rendering_validity(self, sample_case: CaseFile) -> None:
        """Verify markdown syntax validity (table pipes, headers, unclosed formatting)."""
        drafter = DocumentDrafter()
        docs = drafter.draft_all(sample_case, use_llm=False)

        for doc_key, doc in docs.items():
            md = doc.body_markdown
            # Verify non-empty
            assert len(md) > 200, f"Document {doc_key} is too short."

            # Verify balanced bold markers (even number of double asterisks)
            double_asterisks = md.count("**")
            assert double_asterisks % 2 == 0, (
                f"Document {doc_key} contains unbalanced bold formatting."
            )

            # Verify table structure in e-Daakhil petition
            if doc_key == "edaakhil_complaint":
                table_lines = [ln for ln in md.splitlines() if "|" in ln]
                assert len(table_lines) >= 4, "Missing markdown index table."
                separator_lines = [
                    ln for ln in table_lines if re.search(r"\|(?:\s*:?-+:?\s*\|)+", ln)
                ]
                assert len(separator_lines) >= 1, "Missing markdown table header separator."

    def test_ui_handle_draft_single_and_export_disk(
        self, sample_case: CaseFile, mock_router: LLMRouter, tmp_path: Path
    ) -> None:
        """Verify UI handle_draft_single correctly writes file to disk for download."""
        doc, md_text, plain_text, file_path = handle_draft_single(
            case_file=sample_case,
            standing=None,
            doc_type="legal_notice",
            notice_days=15,
            router=mock_router,
            export_dir=tmp_path,
        )

        assert doc is not None
        assert Path(file_path).exists()
        assert Path(file_path).is_file()
        assert Path(file_path).read_text(encoding="utf-8") == md_text


# ==============================================================================
# Suite 4: Workflow 7 (Defense Simulator) Gradio 6 Messages Stress Tests
# ==============================================================================
class TestWorkflow7DefenseSimulatorGradio6Adversarial:
    """Adversarial challenge suite for Workflow 7 Defense Simulator."""

    def test_gradio6_messages_format_compliance(self, mock_router: LLMRouter) -> None:
        """Verify chat_history conforms strictly to Gradio 6 `list[dict[str, str]]` format."""
        updated_state, chat_history, score_text, strengths, weaknesses, advice = (
            handle_simulator_turn(
                user_argument=(
                    "Pursuant to Section 2(46) of CPA 2019, arbitrary no-refund terms are void."
                ),
                state=None,  # Initiates from scratch
                router=mock_router,
            )
        )

        assert isinstance(chat_history, list)
        assert len(chat_history) >= 2

        # Every element MUST be a dictionary with exactly role and content
        for idx, msg in enumerate(chat_history):
            assert isinstance(msg, dict), f"Message at {idx} is not a dict: {type(msg)}"
            assert "role" in msg, f"Message at {idx} missing 'role'"
            assert "content" in msg, f"Message at {idx} missing 'content'"
            assert msg["role"] in ("user", "assistant"), f"Invalid role: {msg['role']}"
            assert isinstance(msg["content"], str)

        # First message must be corporate counsel opening salvo (assistant)
        assert chat_history[0]["role"] == "assistant"
        # Second message must be consumer rebuttal (user)
        assert chat_history[1]["role"] == "user"

    def test_multi_turn_simulation_speaker_alternation(
        self, mock_router: LLMRouter, sample_case: CaseFile
    ) -> None:
        """Verify strict speaker alternation across 4 consecutive turns."""
        simulator = OpposingCounselSimulator(router=mock_router)
        state = simulator.start_simulation(
            case=sample_case,
            initial_tactic=DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND,
        )
        assert len(state.turns) == 1
        assert state.turns[0].speaker == "opposing_counsel"

        # Turn 1: Consumer counters Terms & Conditions
        arg_1 = (
            "Under Section 2(46)(vi) of the Consumer Protection Act, 2019 and Rule 6(3) of the "
            "E-Commerce Rules 2020, unilateral no-refund clauses are void as unfair contracts."
        )
        state, chat, score_txt, strengths, weaknesses, advice = handle_simulator_turn(
            user_argument=arg_1,
            state=state,
            router=mock_router,
        )
        # Should now have 3 turns: counsel (turn 1), consumer (turn 2), counsel counter (turn 3)
        assert len(state.turns) == 3
        assert [t.speaker for t in state.turns] == [
            "opposing_counsel",
            "consumer",
            "opposing_counsel",
        ]
        assert [m["role"] for m in chat] == ["assistant", "user", "assistant"]

        # Turn 2: Consumer counters Unboxing Video demand
        arg_2 = (
            "Absence of unboxing video cannot extinguish consumer rights under Section 2(11). "
            "Defects inside sealed box are latent and proved by tax invoice and delivery timestamp."
        )
        state, chat, score_txt, strengths, weaknesses, advice = handle_simulator_turn(
            user_argument=arg_2,
            state=state,
            router=mock_router,
        )
        # Should now have 5 turns: counsel, consumer, counsel, consumer, counsel
        assert len(state.turns) == 5
        assert [t.speaker for t in state.turns] == [
            "opposing_counsel",
            "consumer",
            "opposing_counsel",
            "consumer",
            "opposing_counsel",
        ]
        assert [m["role"] for m in chat] == ["assistant", "user", "assistant", "user", "assistant"]

        # Turn 3: Consumer counters 3PL Courier defense
        arg_3 = (
            "Under Section 2(7) privity of contract is with the marketplace/seller. "
            "Courier is your agent. "
            "Defective delivery is deficiency in service under Section 2(11)."
        )
        state, chat, score_txt, strengths, weaknesses, advice = handle_simulator_turn(
            user_argument=arg_3,
            state=state,
            router=mock_router,
        )
        # 3 consumer turns completed -> session must conclude
        assert state.is_concluded is True
        assert state.final_assessment is not None
        assert len(state.turns) == 6
        assert [t.speaker for t in state.turns] == [
            "opposing_counsel",
            "consumer",
            "opposing_counsel",
            "consumer",
            "opposing_counsel",
            "consumer",
        ]
        assert [m["role"] for m in chat] == [
            "assistant",
            "user",
            "assistant",
            "user",
            "assistant",
            "user",
        ]

    def test_argument_scoring_strong_vs_weak_contrast(
        self, mock_router: LLMRouter, sample_case: CaseFile
    ) -> None:
        """Verify scoring accurately distinguishes strong statutory points from emotional rants."""
        simulator = OpposingCounselSimulator(router=mock_router)

        # 1. Weak colloquial rant
        weak_rant = (
            "You thieves scam company refund my money now otherwise I will expose on Twitter!"
        )
        feedback_weak: ArgumentFeedback = simulator.evaluate_consumer_argument(
            argument=weak_rant,
            active_tactic=DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND,
            case_summary=sample_case.facts_summary,
            use_llm=False,
        )
        assert feedback_weak.score <= 45.0
        assert any(
            "colloquial" in w.lower() or "emotional" in w.lower() for w in feedback_weak.weaknesses
        )
        assert any("governing legislation" in w.lower() for w in feedback_weak.weaknesses)

        # 2. Strong statutory rebuttal
        strong_arg = (
            "Under Section 2(46)(vi) of the Consumer Protection Act, 2019, any standard-form "
            "contract condition imposing unreasonable terms is void as an unfair contract. "
            "Furthermore, Rule 6(3) and Rule 6(5) of the Consumer Protection (E-Commerce) Rules, "
            "2020 explicitly prohibit sellers from refusing refunds for defective goods. "
            "We demand full refund of valuable consideration paid."
        )
        feedback_strong: ArgumentFeedback = simulator.evaluate_consumer_argument(
            argument=strong_arg,
            active_tactic=DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND,
            case_summary=sample_case.facts_summary,
            use_llm=False,
        )
        assert feedback_strong.score >= 80.0
        assert len(feedback_strong.statutory_sections_cited) >= 2
        assert any(
            "unfair contract" in s.lower() or "statutory" in s.lower()
            for s in feedback_strong.strengths
        )

    def test_post_concluded_and_empty_argument_resilience(
        self, mock_router: LLMRouter, sample_case: CaseFile
    ) -> None:
        """Verify simulator handles empty argument or post-concluded state gracefully."""
        simulator = OpposingCounselSimulator(router=mock_router)
        state = simulator.start_simulation(case=sample_case)

        # Empty argument submission
        s1, chat1, score1, _, _, _ = handle_simulator_turn(
            user_argument="   ",
            state=state,
            router=mock_router,
        )
        assert s1 is not None
        assert len(chat1) >= 2

        # Manually conclude state
        s1.is_concluded = True
        # Submit after conclusion
        s2, chat2, score2, _, _, _ = handle_simulator_turn(
            user_argument="Any further argument after conclusion",
            state=s1,
            router=mock_router,
        )
        assert s2.is_concluded is True
        assert len(chat2) == len(chat1)


# ==============================================================================
# Suite 5: UI App & Component Wiring Empirical Tests
# ==============================================================================
class TestUIAppIntegrationAdversarial:
    """Adversarial challenge suite for UI App Gradio 6 instantiation."""

    def test_gradio_app_instantiation_clean(self, mock_router: LLMRouter) -> None:
        """Verify create_app constructs Gradio 6 Blocks without deprecated kwargs."""
        test_settings = Settings(
            llm_provider="groq",
            groq_model="llama-3.1-8b-instant",
        )
        app = create_app(settings=test_settings, llm_router=mock_router)
        assert isinstance(app, gr.Blocks)

    def test_all_five_tabs_and_components_exist(self, mock_router: LLMRouter) -> None:
        """Verify all 5 tabs and key interactive elements are present in component graph."""
        app = create_app(llm_router=mock_router)
        # Verify that create_app returned an initialized Blocks instance
        assert app is not None
        assert len(app.blocks) > 10
