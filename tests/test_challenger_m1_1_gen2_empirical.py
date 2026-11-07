"""Empirical Challenger 1 Gen 2 Stress Testing Suite for Legal Saathi.

Modernized Package Environment Verification:
- Gradio 6.15.1 (Chatbot messages format dicts: `[{"role": "user" | "assistant", "content": ...}]`)
- Pydantic 2.14.3 (Model validation, serialization, parse_inr_amount)
- FastAPI 0.162.1 / Starlette 1.10.0 / LiteLLM 1.108.2 / OpenAI 3.46.0

Workflows Under Stress Test:
1. Workflow 1 (Case Intake):
   - Currency parsing edge cases (complex formatting, zero, large amounts, invalid inputs)
   - Hinglish, Devanagari, and mixed-language colloquial consumer complaints
   - Extreme narrative text lengths (25k - 50k characters)
   - Missing party names, default entity population, and evidentiary sufficiency auditing
   - Empirical findings on Devanagari lexical currency tokens and Hindi SOV word order
2. Workflow 5 (Clarifications):
   - Empty, whitespace, and no-op clarification answers
   - Malformed Q&A payloads (HTML, script tags, unicode, long answers)
   - Structured timeline updates via mock structured generator
   - Offline fallback integrity under simulated network/API failures
3. Workflow 6 (Document Generation):
   - Legal notice 15-day peremptory notice, statutory compliance, 18% p.a. interest, claim sums
   - Grievance email under Consumer Protection (E-Commerce) Rules, 2020 (48h/30d mandates)
   - e-Daakhil complaint 7-part statutory structure, verification affidavit, NCDRC standards
   - Multi-party Memo of Parties (Seller + Marketplace + Manufacturer)
   - Markdown structure validation (balanced bolding, markdown tables)
   - UI disk export via handle_draft_single
4. Workflow 7 (Defense Simulator & Gradio 6 Chatbot):
   - Strict Gradio 6 `messages` format compliance (`list[dict[str, str]]`)
   - Multi-turn debate simulation with speaker alternation across all canonical defense tactics
   - Scoring differentiation: strong statutory citations vs emotional colloquial rants
   - Turn advancement, conclusion triggers, and handle_simulator_turn edge conditions
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

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
    handle_draft_single,
    handle_simulator_turn,
)
from legal_assistant.workflows.case_builder import CaseBuilder
from legal_assistant.workflows.drafter import DocumentDrafter
from legal_assistant.workflows.simulator import (
    ArgumentFeedback,
    DefenseTacticType,
    OpposingCounselSimulator,
    SimulatorState,
)


# ==============================================================================
# Deterministic Test Fixtures
# ==============================================================================
class MockOfflineEmpiricalLLMClient(BaseLLMClient):
    """Deterministic offline mock LLM client."""

    def __init__(self, provider_name: str = "mock-groq") -> None:
        """Initialize mock client."""
        self._provider_name = provider_name

    @property
    def provider_name(self) -> str:
        """Return provider identifier."""
        return self._provider_name

    @property
    def model_name(self) -> str:
        """Return mock model name."""
        return "mock-llama-3.3-70b-versatile"

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Return deterministic mock response."""
        return LLMResponse(
            content="Mock offline response for empirical verification.",
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
        """Raise error to trigger deterministic fallback unless explicitly monkeypatched."""
        raise NotImplementedError("Empirical suite uses deterministic offline fallbacks.")


@pytest.fixture
def offline_router() -> LLMRouter:
    """Provide configured offline LLMRouter."""
    router = LLMRouter()
    client = MockOfflineEmpiricalLLMClient()
    router._clients["groq"] = client
    return router


@pytest.fixture
def canonical_multi_party_case() -> CaseFile:
    """Provide fully populated CaseFile with multiple opposite parties."""
    return CaseFile(
        case_id="case_emp_multi_001",
        title="Smart Television Display Panel Failure & Warranty Disowning",
        disputed_amount_inr=64999.0,
        compensation_claimed_inr=25000.0,
        transaction_date="2024-01-15",
        cause_of_action_date="2024-01-25",
        complainant=PartyDetails(
            name="Ananya Sharma",
            email="ananya.sharma@example.com",
            phone="+91-9810123456",
            address="Apartment 304, Palm Grove, Koramangala",
            city="Bengaluru",
            state="Karnataka",
        ),
        opposite_parties=[
            OppositeParty(
                name="QuickRetail Electronics LLP",
                role="Authorized Merchant / Seller",
                address="Industrial Area Phase 2, Peenya, Bengaluru, Karnataka 560058",
                entity_type="seller",
            ),
            OppositeParty(
                name="BharatCart E-Commerce Private Limited",
                role="E-Commerce Marketplace Platform",
                address="Outer Ring Road, Bellandur, Bengaluru, Karnataka 560103",
                entity_type="marketplace",
            ),
            OppositeParty(
                name="VisionTech Consumer Electronics India Ltd",
                role="Original Equipment Manufacturer",
                address="Plot 12, Electronic City Phase 1, Bengaluru 560100",
                entity_type="manufacturer",
            ),
        ],
        facts_summary=(
            "Complainant purchased a 55-inch VisionTech 4K OLED Smart TV on 2024-01-15 "
            "for INR 64,999.00 via BharatCart online platform. Upon unboxing and installation "
            "on 2024-01-18, the screen showed horizontal black lines and flickering. An authorized "
            "service inspection on 2024-01-22 confirmed internal panel manufacturing defect. "
            "On 2024-01-25, BharatCart and QuickRetail rejected refund claiming 7-day return "
            "policy had expired, and VisionTech refused warranty claiming physical damage."
        ),
        timeline=[
            TimelineEvent(
                date="2024-01-15",
                description="Ordered Smart TV via BharatCart marketplace for ₹64,999.00.",
                significance="Transaction Date under Section 2(7)",
            ),
            TimelineEvent(
                date="2024-01-18",
                description="Delivered and unboxed; screen flickering noticed immediately.",
                significance="Delivery Date",
            ),
            TimelineEvent(
                date="2024-01-22",
                description="Authorized technician issued Job Sheet confirming internal defect.",
                significance="Manufacturing Defect Proof",
            ),
            TimelineEvent(
                date="2024-01-25",
                description="Formal refund and replacement rejected by merchant and platform.",
                significance="Cause of Action Date under Section 69",
            ),
        ],
        evidence_checklist=[],
        missing_evidence=[],
        clarification_questions=[
            "Did the technician provide an official stamped copy of the job sheet?",
            "Was this TV purchased strictly for personal domestic use?",
        ],
    )


# ==============================================================================
# Suite 1: Workflow 1 (Case Intake) Stress Tests
# ==============================================================================
class TestWorkflow1CaseIntakeEmpiricalGen2:
    """Empirical stress tests for Workflow 1 Case Intake."""

    @pytest.mark.parametrize(
        ("input_val", "expected_float"),
        [
            ("₹ 50,000", 50000.0),
            ("₹50000/-", 50000.0),
            ("Rs. 1,45,000.50", 145000.5),
            ("INR 99,999", 99999.0),
            ("75000/-", 75000.0),
            ("Rs 25000", 25000.0),
            ("  INR  3,25,000.00  /- ", 325000.0),
            ("₹ 0", 0.0),
            ("0.0", 0.0),
            ("10000000.00", 10000000.0),
            ("Free of charge", 0.0),
            ("N/A", 0.0),
            ("", 0.0),
            ("   ", 0.0),
            (12500, 12500.0),
            (89999.75, 89999.75),
        ],
    )
    def test_parse_inr_amount_edge_cases(self, input_val: Any, expected_float: float) -> None:
        """Verify robust sanitization across diverse currency notations and edge cases."""
        parsed = CaseFile.parse_inr_amount(input_val)
        assert parsed == expected_float
        assert isinstance(parsed, float)

    def test_deterministic_currency_extraction_multi_amount_narrative(self) -> None:
        """Verify amount extraction handles narratives containing item price and shipping."""
        narrative = (
            "I ordered an air conditioner for Rs. 38,500/- on Flipkart on 2024-03-01. "
            "Delivery was made on 2024-03-05 but compressor does not cool. "
            "Seller refused refund on 2024-03-08."
        )
        builder = CaseBuilder()
        case = builder.build_case(narrative, use_llm=False)
        assert case.disputed_amount_inr == 38500.0

    def test_pure_devanagari_consumer_complaint_with_rupee_symbol(self) -> None:
        """Verify intake of grievance in Devanagari Hindi with rupee symbol."""
        devanagari_narrative = (
            "मैंने Amazon से ₹15,000 का मोबाइल फोन खरीदा था। 12 फरवरी 2024 को डिलीवरी मिली "
            "लेकिन डिब्बे के अंदर मोबाइल की स्क्रीन पूरी तरह से टूटी हुई थी। "
            "ग्राहक सेवा ने वापसी और रिफंड से साफ इनकार कर दिया। "
            "कर चालान और unboxing video मेरे पास उपलब्ध है।"
        )
        builder = CaseBuilder()
        case = builder.build_case(devanagari_narrative, use_llm=False)

        assert isinstance(case, CaseFile)
        assert case.disputed_amount_inr == 15000.0
        assert len(case.opposite_parties) >= 1
        assert "amazon" in case.opposite_parties[0].name.lower()
        # Verify evidence detection
        present_evidence = " ".join(item.item_name.lower() for item in case.evidence_checklist)
        assert "unboxing" in present_evidence

    def test_empirical_observation_devanagari_currency_word_blindspot(self) -> None:
        """Adversarial observation: deterministic regex does not match Devanagari रुपये token.

        Documenting empirical boundary: in offline deterministic mode, if narrative spells
        currency using Devanagari word 'रुपये' without ASCII '₹', 'Rs', or 'INR',
        the deterministic regex extractor defaults disputed_amount_inr to 0.0.
        """
        narrative = "मैंने 15000 रुपये का उत्पाद खरीदा जो खराब निकला। कंपनी ने रिफंड नहीं दिया।"
        builder = CaseBuilder()
        case = builder.build_case(narrative, use_llm=False)
        # Empirical finding: evaluates to 0.0 without LLM
        assert case.disputed_amount_inr == 0.0
        assert isinstance(case, CaseFile)

    def test_mixed_hinglish_slang_with_emojis(self) -> None:
        """Verify colloquial Hinglish with emojis, abbreviations, and informal speech."""
        hinglish_narrative = (
            "Hey team, mera naam hai Aarav Verma (aarav.v@test.org, 9876501234). "
            "Maine Zomato se dinner order kiya tha for Rs. 1,850/- 🍕. "
            "Food bilkul stale aur contaminated nikla, jisse food poisoning ho gayi 🤮. "
            "Hospital bill of Rs. 4,500/- bhi attach kar raha hoon. "
            "Zomato CC agent refused compensation saying 'restaurant issue, not our problem'. "
            "Need justice and full refund plus medical reimbursement."
        )
        builder = CaseBuilder()
        case = builder.build_case(hinglish_narrative, use_llm=False)

        assert isinstance(case, CaseFile)
        assert case.disputed_amount_inr == 1850.0
        assert case.complainant.name == "Aarav Verma"
        assert case.complainant.email == "aarav.v@test.org"
        assert case.complainant.phone == "9876501234"
        assert any("Zomato" in op.name for op in case.opposite_parties)

    def test_empirical_observation_hindi_sov_name_word_order(self) -> None:
        """Adversarial observation: Hindi SOV 'Mera naam X hai' word order vs SVO regex.

        Documenting empirical boundary: regex `(?:name is|naam hai|i am) Name` expects SVO order.
        Colloquial Hindi SOV 'Mera naam Rahul Verma hai' places 'hai' after the name, causing
        the deterministic fallback to retain default 'Complainant' unless pre-supplied.
        """
        narrative = "Bhai mera naam Rahul Verma hai. Maine Rs. 5000 ka headphone liya Swiggy se."
        builder = CaseBuilder()
        case = builder.build_case(narrative, use_llm=False)
        # Empirical finding: defaults to 'Complainant' because 'hai' follows name
        assert case.complainant.name == "Complainant"
        assert case.disputed_amount_inr == 5000.0

    def test_extreme_narrative_length_scalability(self) -> None:
        """Verify handling of extreme text payload (30,000+ characters) without TLE or OOM."""
        filler_unit = (
            "The customer service executives kept transferring my call from one dept to another. "
            "I waited on hold for more than 45 minutes each time. Nobody answered my emails. "
        )
        filler = filler_unit * 180  # ~25,000 chars

        narrative = (
            "Complainant Rajesh Khanna purchased a coffee machine for INR 85,000 "
            "on 2024-01-10 from Flipkart. The boiler leaked steam immediately on 2024-01-12. "
            "Support refused replacement citing unboxing policy. "
            + filler
            + " Invoice #FK-8819 is available. Payment made via debit card."
        )
        assert len(narrative) > 25000

        builder = CaseBuilder()
        case = builder.build_case(narrative, use_llm=False)

        assert isinstance(case, CaseFile)
        assert case.disputed_amount_inr == 85000.0
        assert len(case.facts_summary) > 50
        assert len(case.opposite_parties) >= 1

    def test_missing_party_names_defaults_gracefully(self) -> None:
        """Verify narrative with anonymous merchant defaults safely without crashing."""
        narrative = (
            "Bought defective wireless earbuds for Rs. 2,999/- on 2024-02-10 from an unknown "
            "online store. Sound cuts off every 2 minutes. Seller ghosted me and refused refund."
        )
        builder = CaseBuilder()
        case = builder.build_case(narrative, use_llm=False)

        assert isinstance(case, CaseFile)
        assert case.disputed_amount_inr == 2999.0
        assert len(case.opposite_parties) == 1
        assert "Opposite Party" in case.opposite_parties[0].name
        # Critical proofs must be flagged as missing
        missing_names = [m.item_name.lower() for m in case.missing_evidence]
        assert any("invoice" in m for m in missing_names)
        assert any("payment" in m for m in missing_names)


# ==============================================================================
# Suite 2: Workflow 5 (Clarifications) Stress Tests
# ==============================================================================
class TestWorkflow5ClarificationsEmpiricalGen2:
    """Empirical stress tests for Workflow 5 Clarifications."""

    def test_empty_and_whitespace_only_clarification_answers(
        self, canonical_multi_party_case: CaseFile
    ) -> None:
        """Verify empty dictionaries and whitespace-only responses leave case pristine."""
        builder = CaseBuilder()
        initial_summary = canonical_multi_party_case.facts_summary
        initial_timeline_len = len(canonical_multi_party_case.timeline)

        # 1. Empty dictionary
        c1 = builder.update_case_with_clarifications(canonical_multi_party_case, {})
        assert c1.facts_summary == initial_summary
        assert len(c1.timeline) == initial_timeline_len

        # 2. Whitespace-only values
        c2 = builder.update_case_with_clarifications(
            canonical_multi_party_case,
            {
                "Question 1?": "   ",
                "Question 2?": "\n\t  \r ",
                "Question 3?": "",
            },
        )
        assert c2.facts_summary == initial_summary
        assert len(c2.timeline) == initial_timeline_len

    def test_structured_timeline_update_via_mocked_llm(
        self, canonical_multi_party_case: CaseFile, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify structured clarification update enriches timeline and facts when LLM succeeds."""
        builder = CaseBuilder()

        # Build expected updated CaseFile
        updated_mock = canonical_multi_party_case.model_copy(deep=True)
        updated_mock.facts_summary += (
            " Clarified: Official job sheet #JS-9021 issued on 2024-01-22 confirms panel defect."
        )
        updated_mock.timeline.append(
            TimelineEvent(
                date="2024-01-22",
                description="Authorized technician issued physical job sheet #JS-9021.",
                significance="Documentary Proof of Defect",
            )
        )
        # Mock structured LLM call
        monkeypatch.setattr(
            builder.router,
            "generate_structured_with_fallback",
            lambda **kwargs: updated_mock,
        )

        answers = {
            "Did the technician provide an official stamped copy of the job sheet?": (
                "Yes, Job sheet #JS-9021 was physically handed over with stamp on 2024-01-22."
            )
        }
        res = builder.update_case_with_clarifications(canonical_multi_party_case, answers)

        assert res.case_id == canonical_multi_party_case.case_id
        assert "job sheet #JS-9021" in res.facts_summary
        assert len(res.timeline) == len(canonical_multi_party_case.timeline) + 1
        assert any("JS-9021" in t.description for t in res.timeline)

    def test_offline_fallback_integrity_on_api_error(
        self, canonical_multi_party_case: CaseFile, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify robust offline fallback when LLM router raises network or rate limit errors."""
        builder = CaseBuilder()

        def _raising_generate(**kwargs: Any) -> Any:
            raise ConnectionError("Mock network connection severed or HTTP 429 rate limit")

        monkeypatch.setattr(
            builder.router,
            "generate_structured_with_fallback",
            _raising_generate,
        )

        answers = {
            "Was this TV purchased strictly for personal domestic use?": (
                "Strictly for personal domestic family use in home, zero commercial use."
            )
        }
        res = builder.update_case_with_clarifications(canonical_multi_party_case, answers)

        # Integrity guarantees: CaseFile preserved, facts appended deterministically
        assert res.case_id == canonical_multi_party_case.case_id
        assert "Additional Clarifications:" in res.facts_summary
        assert "personal domestic family use" in res.facts_summary
        assert len(res.opposite_parties) == 3
        assert len(res.timeline) == 4

    def test_malformed_and_extreme_clarification_payloads(
        self, canonical_multi_party_case: CaseFile, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify adversarial payloads (XSS, SQL, markdown injection, unicode) do not crash."""
        builder = CaseBuilder()
        monkeypatch.setattr(
            builder.router,
            "generate_structured_with_fallback",
            lambda **kwargs: (_ for _ in ()).throw(RuntimeError("Offline unit test")),
        )

        adversarial_answers = {
            "<b>Question with HTML</b>": "<script>document.cookie='leak'</script>",
            "SQL Injection Question": "'; DROP TABLE cases; --",
            "Unicode & Emoji Question 🚀": "उपयोग: व्यक्तिगत उपयोग के लिए। 전혀 상업적이지 않음.",
            "Giant string": "X" * 4000,
        }
        updated = builder.update_case_with_clarifications(
            canonical_multi_party_case, adversarial_answers
        )

        assert updated is not None
        assert "DROP TABLE" in updated.facts_summary
        assert "व्यक्तिगत उपयोग" in updated.facts_summary
        assert "X" * 4000 in updated.facts_summary


# ==============================================================================
# Suite 3: Workflow 6 (Document Generation) Stress Tests
# ==============================================================================
class TestWorkflow6DocumentGenerationEmpiricalGen2:
    """Empirical stress tests for Workflow 6 Document Generation."""

    def test_legal_notice_statutory_clauses_and_financial_calculations(
        self, canonical_multi_party_case: CaseFile
    ) -> None:
        """Verify legal notice incorporates 15-day deadline, 18% interest, and claim sums."""
        drafter = DocumentDrafter()
        doc = drafter.draft_legal_notice(
            canonical_multi_party_case,
            notice_period_days=15,
            use_llm=False,
        )

        assert isinstance(doc, LegalNotice)
        assert doc.document_type == "legal_notice"
        assert doc.notice_period_days == 15
        expected_total = (
            canonical_multi_party_case.disputed_amount_inr
            + canonical_multi_party_case.compensation_claimed_inr
        )
        assert doc.claim_amount_inr == expected_total

        md = doc.body_markdown
        # Delivery method
        assert "SPEED POST" in md.upper() or "REGISTERED POST" in md.upper()
        # Statutory Sections
        assert "Section 2(7)" in md
        assert "Section 2(10)" in md
        assert "Section 2(11)" in md
        assert "Section 2(47)" in md
        # Interest and deadline
        assert "18%" in md
        assert "15" in md
        # E-Daakhil warning
        assert "edaakhil.nic.in" in md or "e-Daakhil" in md

    def test_grievance_email_statutory_e_commerce_mandates(
        self, canonical_multi_party_case: CaseFile
    ) -> None:
        """Verify grievance email statutory compliance under E-Commerce Rules 2020."""
        drafter = DocumentDrafter()
        doc = drafter.draft_grievance_email(canonical_multi_party_case, use_llm=False)

        assert isinstance(doc, DraftedDocument)
        assert doc.document_type == "grievance_email"
        md = doc.body_markdown

        # Rule 4(4)/4(5) Grievance Officer mandates
        assert "Rule 4(4)" in md or "Rule 4(5)" in md
        assert "48" in md  # 48-hour acknowledgment
        assert "30" in md  # 30-day resolution
        # Rule 6(3) / 7(4) refund prohibition bar
        assert "Rule 6(3)" in md or "Rule 7(4)" in md
        # Defect / deficiency
        assert "Section 2(11)" in md

    def test_edaakhil_consumer_complaint_7_part_structure_and_ncdrc_standards(
        self, canonical_multi_party_case: CaseFile
    ) -> None:
        """Verify e-Daakhil petition conforms strictly to 7-part NCDRC court format."""
        drafter = DocumentDrafter()
        doc = drafter.draft_edaakhil_complaint(canonical_multi_party_case, use_llm=False)

        assert isinstance(doc, DraftedDocument)
        assert doc.document_type == "edaakhil_complaint"
        md = doc.body_markdown

        # Commission heading
        assert "DISTRICT CONSUMER DISPUTES REDRESSAL COMMISSION" in md.upper()

        # Part I: Memo of Parties - must include all 3 opposite parties
        assert "PART I: MEMO OF PARTIES" in md
        assert canonical_multi_party_case.complainant.name in md
        assert "QuickRetail" in md
        assert "BharatCart" in md
        assert "VisionTech" in md

        # Part II: Index of Documents
        assert "PART II: INDEX OF DOCUMENTS" in md
        assert "Annexure C-1" in md
        assert "Annexure C-2" in md

        # Part III: Statement of Material Facts
        assert "PART III: STATEMENT OF MATERIAL FACTS" in md

        # Part IV: Statutory Grounds of Claim
        assert "PART IV: STATUTORY GROUNDS OF CLAIM" in md
        assert "GROUND A" in md

        # Part V: Pecuniary & Territorial Jurisdiction
        assert "PART V: PECUNIARY & TERRITORIAL JURISDICTION" in md
        assert "Section 34(2)(d)" in md

        # Part VI: Limitation Statement (Section 69)
        assert "PART VI: LIMITATION STATEMENT" in md
        assert "Section 69" in md

        # Part VII: Prayer / Relief
        assert "PART VII: PRAYER" in md
        assert "refund" in md.lower()

        # Verification Affidavit
        assert "VERIFICATION" in md.upper()
        assert doc.verification_statement is not None
        assert canonical_multi_party_case.complainant.name in doc.verification_statement

    def test_markdown_structural_integrity_and_formatting(
        self, canonical_multi_party_case: CaseFile
    ) -> None:
        """Verify all generated documents have balanced markdown formatting and valid headers."""
        drafter = DocumentDrafter()
        all_docs = drafter.draft_all(canonical_multi_party_case, use_llm=False)

        assert len(all_docs) == 3
        for doc_type, doc in all_docs.items():
            md = doc.body_markdown
            assert len(md) > 200, f"Document {doc_type} too short"
            # Balanced double asterisks
            assert md.count("**") % 2 == 0, f"Unbalanced bold markdown in {doc_type}"

        # Complaint and Notice have formal document headers
        assert all_docs["legal_notice"].body_markdown.startswith("#")
        assert all_docs["edaakhil_complaint"].body_markdown.startswith("#")
        # Grievance email starts with formal email headers
        assert all_docs["grievance_email"].body_markdown.startswith("**TO**:")

    def test_ui_handle_draft_single_export_to_disk(
        self, canonical_multi_party_case: CaseFile, offline_router: LLMRouter, tmp_path: Path
    ) -> None:
        """Verify handle_draft_single exports valid downloadable UTF-8 file to disk."""
        doc, md_text, plain_text, file_path = handle_draft_single(
            case_file=canonical_multi_party_case,
            standing=None,
            doc_type="edaakhil_complaint",
            notice_days=15,
            router=offline_router,
            export_dir=tmp_path,
        )

        assert doc is not None
        saved_file = Path(file_path)
        assert saved_file.exists()
        assert saved_file.is_file()
        assert saved_file.suffix == ".md"
        assert saved_file.read_text(encoding="utf-8") == md_text


# ==============================================================================
# Suite 4: Workflow 7 (Defense Simulator & Gradio 6 Chatbot) Stress Tests
# ==============================================================================
class TestWorkflow7DefenseSimulatorGradio6EmpiricalGen2:
    """Empirical stress tests for Workflow 7 Defense Simulator and Gradio 6 Chatbot."""

    def test_gradio6_messages_format_strict_compliance(
        self, offline_router: LLMRouter, canonical_multi_party_case: CaseFile
    ) -> None:
        """Verify chat_history conforms strictly to Gradio 6 `list[dict[str, str]]`."""
        simulator = OpposingCounselSimulator(router=offline_router)
        state = simulator.start_simulation(case=canonical_multi_party_case)

        user_arg = (
            "Under Section 2(46)(vi) of CPA 2019, unreasonable boilerplate terms "
            "denying refund for defective goods are void as unfair contracts."
        )
        updated_state, chat_history, score_txt, strengths, weaknesses, advice = (
            handle_simulator_turn(
                user_argument=user_arg,
                state=state,
                router=offline_router,
            )
        )

        assert isinstance(chat_history, list)
        assert len(chat_history) == 3

        # Validate message structure against Gradio 6 MessageDict schema
        for i, msg in enumerate(chat_history):
            assert isinstance(msg, dict), f"Message {i} is not dict: {type(msg)}"
            assert set(msg.keys()) == {"role", "content"}, (
                f"Unexpected keys in message {i}: {msg.keys()}"
            )
            assert msg["role"] in ("user", "assistant"), f"Invalid role: {msg['role']}"
            assert isinstance(msg["content"], str)
            assert len(msg["content"]) > 0

        # Transcript alternation: counsel (turn 1), consumer (turn 2), counsel rebuttal (turn 3)
        assert chat_history[0]["role"] == "assistant"
        assert chat_history[1]["role"] == "user"
        assert chat_history[2]["role"] == "assistant"

    def test_full_multi_turn_debate_progression_to_conclusion(
        self, offline_router: LLMRouter, canonical_multi_party_case: CaseFile
    ) -> None:
        """Verify multi-turn progression advances turns, scores, and concludes cleanly."""
        simulator = OpposingCounselSimulator(router=offline_router)
        state = simulator.start_simulation(
            case=canonical_multi_party_case,
            initial_tactic=DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND,
        )
        assert len(state.turns) == 1
        assert state.is_concluded is False

        # Turn 1
        state, chat, _, _, _, _ = handle_simulator_turn(
            user_argument="CPA 2019 Section 2(46) invalidates unfair unilateral terms.",
            state=state,
            router=offline_router,
        )
        assert len(state.turns) == 3
        assert state.is_concluded is False

        # Turn 2
        state, chat, _, _, _, _ = handle_simulator_turn(
            user_argument="Section 2(11) manufacturing defect in TV screen is deficiency.",
            state=state,
            router=offline_router,
        )
        assert len(state.turns) == 5
        assert state.is_concluded is False

        # Turn 3 - Final turn concluding session
        state, chat, score_txt, strengths, weaknesses, advice = handle_simulator_turn(
            user_argument=(
                "Section 86 product liability holds manufacturer VisionTech and seller QuickRetail "
                "strictly liable for defective product delivery."
            ),
            state=state,
            router=offline_router,
        )
        assert len(state.turns) == 6
        assert state.is_concluded is True
        assert state.final_assessment is not None
        assert "READINESS" in state.final_assessment or "Score:" in state.final_assessment
        assert len(chat) == 6
        assert [m["role"] for m in chat] == [
            "assistant",
            "user",
            "assistant",
            "user",
            "assistant",
            "user",
        ]

    def test_scoring_contrast_strong_statutory_vs_colloquial_rant(
        self, offline_router: LLMRouter, canonical_multi_party_case: CaseFile
    ) -> None:
        """Verify argument evaluation separates legally grounded points from emotional rants."""
        simulator = OpposingCounselSimulator(router=offline_router)

        # 1. Emotional rant without legal basis
        weak_rant = "You are a scam company! Give my money back right now or I will post on Reddit!"
        feedback_weak: ArgumentFeedback = simulator.evaluate_consumer_argument(
            argument=weak_rant,
            active_tactic=DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND,
            case_summary=canonical_multi_party_case.facts_summary,
            use_llm=False,
        )
        assert feedback_weak.score <= 45.0
        assert any("colloquial" in w.lower() for w in feedback_weak.weaknesses)

        # 2. Strong statutory rebuttal
        strong_rebuttal = (
            "Under Section 2(46)(vi) of the Consumer Protection Act, 2019, any boilerplate clause "
            "imposing unreasonable charge or terms is void as an unfair contract. "
            "Furthermore, Rule 6(3) and Rule 7(4) of E-Commerce Rules, 2020 prohibit sellers "
            "from refusing refunds for defective goods. The job sheet proves the panel defect."
        )
        feedback_strong: ArgumentFeedback = simulator.evaluate_consumer_argument(
            argument=strong_rebuttal,
            active_tactic=DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND,
            case_summary=canonical_multi_party_case.facts_summary,
            use_llm=False,
        )
        assert feedback_strong.score >= 80.0
        assert len(feedback_strong.statutory_sections_cited) >= 2
        assert any(
            "unfair contract" in s.lower() or "statutory" in s.lower()
            for s in feedback_strong.strengths
        )

    def test_handle_simulator_turn_with_none_state_initializes_cleanly(
        self, offline_router: LLMRouter
    ) -> None:
        """Verify handle_simulator_turn with state=None initializes without throwing exceptions."""
        updated_state, chat_history, score_text, strengths, weaknesses, advice = (
            handle_simulator_turn(
                user_argument="Defective item was received and refund was denied.",
                state=None,
                router=offline_router,
            )
        )
        assert isinstance(updated_state, SimulatorState)
        assert len(chat_history) >= 2
        assert chat_history[0]["role"] == "assistant"
        assert chat_history[1]["role"] == "user"

    def test_handle_simulator_turn_post_concluded_resilience(
        self, offline_router: LLMRouter, canonical_multi_party_case: CaseFile
    ) -> None:
        """Verify submitting argument after conclusion does not error and keeps concluded status."""
        simulator = OpposingCounselSimulator(router=offline_router)
        state = simulator.start_simulation(case=canonical_multi_party_case)
        state.is_concluded = True
        state.final_assessment = "Practice Concluded. Grade: A."

        post_state, chat, score_txt, strengths, weaknesses, advice = handle_simulator_turn(
            user_argument="One more argument after debate has ended.",
            state=state,
            router=offline_router,
        )
        assert post_state.is_concluded is True
        assert post_state.final_assessment == "Practice Concluded. Grade: A."

    @pytest.mark.parametrize(
        "tactic",
        [
            DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND,
            DefenseTacticType.UNBOXING_VIDEO_ABSENCE,
            DefenseTacticType.IT_ACT_SECTION_79_SAFE_HARBOR,
            DefenseTacticType.THIRD_PARTY_LOGISTICS_MANUFACTURER,
            DefenseTacticType.OTP_VERIFICATION_ACCEPTANCE,
            DefenseTacticType.CUSTOM_TACTIC,
        ],
    )
    def test_simulator_all_canonical_tactics_opening_salvos(
        self,
        tactic: DefenseTacticType,
        offline_router: LLMRouter,
        canonical_multi_party_case: CaseFile,
    ) -> None:
        """Verify simulator generates authoritative opening argument across all 6 tactics."""
        simulator = OpposingCounselSimulator(router=offline_router)
        state = simulator.start_simulation(
            case=canonical_multi_party_case,
            initial_tactic=tactic,
        )
        assert len(state.turns) == 1
        opening_turn = state.turns[0]
        assert opening_turn.speaker == "opposing_counsel"
        assert len(opening_turn.content) > 50
        assert opening_turn.defense_tactic == tactic
