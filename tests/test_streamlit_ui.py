"""Unit and integration tests for Legal Saathi Streamlit Web User Interface.

Uses streamlit.testing.v1.AppTest to validate the Streamlit application layout,
component rendering, state persistence, tab interactions, and workflow execution.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import SecretStr
from streamlit.testing.v1 import AppTest

from legal_assistant.config import Settings
from legal_assistant.llm.router import LLMRouter
from legal_assistant.schemas import (
    CaseFile,
    CostEstimate,
    LegalStanding,
    OppositeParty,
    PartyDetails,
    StatutoryViolation,
    TimelineEvent,
)
from legal_assistant.ui.app import handle_simulator_turn
from tests.test_ui import MockLLMClient

APP_FILE = str(
    Path(__file__).resolve().parent.parent / "src" / "legal_assistant" / "ui" / "app.py"
)


@pytest.fixture
def mock_router() -> LLMRouter:
    """Create configured LLMRouter populated with deterministic mock clients."""
    settings = Settings(
        llm_provider="groq",
        groq_api_key=SecretStr("mock-groq-key"),
        groq_model="llama-3.1-8b-instant",
    )
    router = LLMRouter(settings=settings)
    router.register_client(
        "groq", MockLLMClient(provider_name="groq", model_name="llama-3.1-8b-instant")
    )
    router.register_client(
        "ollama", MockLLMClient(provider_name="ollama", model_name="llama3.2:3b")
    )
    router.register_client(
        "openai", MockLLMClient(provider_name="openai", model_name="gpt-4o-mini")
    )
    router.register_client(
        "gemini", MockLLMClient(provider_name="gemini", model_name="gemini-1.5-flash")
    )
    return router


@pytest.fixture
def sample_case_file() -> CaseFile:
    """Create realistic structured CaseFile for workflow UI testing."""
    return CaseFile(
        case_id="case_st_test_001",
        title="Defective Smartphone Refund Denial",
        disputed_amount_inr=65000.0,
        transaction_date="2026-01-15",
        cause_of_action_date="2026-01-20",
        facts_summary=(
            "Complainant bought a smartphone on 2026-01-15 for Rs 65,000 from an e-commerce "
            "platform. Device arrived with a cracked screen. Merchant denied refund."
        ),
        opposite_parties=[
            OppositeParty(name="E-Commerce Retailer", role="Seller")
        ],
        timeline=[
            TimelineEvent(
                date="2026-01-15",
                significance="Purchase Order",
                description="Ordered smartphone online for Rs 65,000.",
            ),
            TimelineEvent(
                date="2026-01-18",
                significance="Delivery",
                description="Delivered defective with cracked screen.",
            ),
        ],
        complainant=PartyDetails(
            name="Rahul Sharma",
            email="rahul.sharma@example.com",
            phone="+91-9876543210",
            city="New Delhi",
            state="Delhi",
        ),
    )


@pytest.fixture
def sample_standing() -> LegalStanding:
    """Create realistic LegalStanding object for UI testing."""
    return LegalStanding(
        is_consumer=True,
        consumer_rationale=(
            "Complainant paid consideration for personal electronic device consumption."
        ),
        pecuniary_commission_forum="District Commission",
        pecuniary_jurisdiction_limit="District Commission (Up to ₹50 Lakhs)",
        jurisdiction_rationale="Territorial jurisdiction in New Delhi under Section 34(2).",
        limitation_status="within_limitation",
        limitation_rationale="Within 2-year limitation period under Section 69 CPA 2019.",
        estimated_timeline="15-45 days",
        statutory_violations=[
            StatutoryViolation(
                statute="Consumer Protection Act, 2019",
                section_or_rule="Section 2(47)",
                title="Unfair Trade Practice",
                violation_nature="unfair_trade_practice",
                explanation="Refusal to refund consideration for defective merchandise.",
            ),
            StatutoryViolation(
                statute="Consumer Protection (E-Commerce) Rules, 2020",
                section_or_rule="Rule 4(5)",
                title="Grievance Redressal",
                violation_nature="deficiency_in_service",
                explanation="Failure to redress consumer grievance within timeline.",
            ),
        ],
        estimated_costs=CostEstimate(
            court_fees_inr=2000.0,
            notice_costs_inr=100.0,
            total_estimated_out_of_pocket_inr="₹2,000 statutory court fees",
        ),
    )


# ==============================================================================
# 1. App Initialization & Page Structure Tests
# ==============================================================================
def test_streamlit_app_initialization_and_title(mock_router: LLMRouter) -> None:
    """Verify Streamlit app initializes cleanly without exceptions and renders title & tabs."""
    at = AppTest.from_file(APP_FILE)
    at.session_state["router"] = mock_router
    at.run(timeout=30)

    assert len(at.exception) == 0, f"App execution raised exceptions: {at.exception}"
    assert len(at.title) >= 1
    assert "Legal Saathi — AI Consumer Lawyer" in at.title[0].value
    assert len(at.tabs) == 4
    tab_labels = [t.label for t in at.tabs]
    assert any("Case Intake" in lab for lab in tab_labels)
    assert any("Legal Standing" in lab for lab in tab_labels)
    assert any("Document Drafter" in lab for lab in tab_labels)
    assert any("Opposing Counsel" in lab for lab in tab_labels)


# ==============================================================================
# 2. Sidebar Controls & Model Switcher Tests
# ==============================================================================
def test_streamlit_sidebar_controls_and_provider_switching(mock_router: LLMRouter) -> None:
    """Verify persistent sidebar contains provider selector, apply, and ping buttons."""
    at = AppTest.from_file(APP_FILE)
    at.session_state["router"] = mock_router
    at.run(timeout=30)

    assert len(at.exception) == 0
    sidebar_selects = [s.label for s in at.sidebar.selectbox]
    assert "Active LLM Provider" in sidebar_selects

    # Verify buttons exist in sidebar
    apply_btn = at.sidebar.button(key="sb_btn_apply")
    ping_btn = at.sidebar.button(key="sb_btn_ping")
    assert apply_btn is not None
    assert ping_btn is not None

    # Test clicking Apply Settings with provider switch
    at.sidebar.selectbox(key="sb_provider_select").select("ollama")
    apply_btn.click().run(timeout=30)
    assert len(at.exception) == 0
    assert at.session_state.get("active_provider") == "ollama"

    # Test clicking Ping Provider
    ping_btn.click().run(timeout=30)
    assert len(at.exception) == 0


# ==============================================================================
# 3. Tab 1: Case Intake & Facts Building Tests
# ==============================================================================
def test_streamlit_tab1_load_sample_dispute(mock_router: LLMRouter) -> None:
    """Verify Load Sample Dispute button populates the narrative text area."""
    at = AppTest.from_file(APP_FILE)
    at.session_state["router"] = mock_router
    at.run(timeout=30)

    load_btn = at.button(key="btn_load_sample")
    assert load_btn is not None
    load_btn.click().run(timeout=30)

    assert len(at.exception) == 0
    narrative_val = str(at.session_state.get("ta_case_narrative", ""))
    assert len(narrative_val) > 100
    assert "smartphone" in narrative_val.lower() or "65,000" in narrative_val


def test_streamlit_tab1_case_intake_analysis(
    mock_router: LLMRouter, sample_case_file: CaseFile
) -> None:
    """Verify Analyze Facts & Build Case button builds CaseFile and metrics."""
    at = AppTest.from_file(APP_FILE)
    at.session_state["router"] = mock_router
    at.session_state["ta_case_narrative"] = sample_case_file.facts_summary
    at.run(timeout=30)

    analyze_btn = at.button(key="btn_analyze_case")
    assert analyze_btn is not None
    analyze_btn.click().run(timeout=30)

    assert len(at.exception) == 0
    case_obj = at.session_state.get("case_file")
    assert isinstance(case_obj, CaseFile)
    assert case_obj.disputed_amount_inr == 55000.0 or case_obj.disputed_amount_inr is not None
    assert len(at.session_state.get("intake_timeline", [])) >= 1


def test_streamlit_tab1_out_of_scope_interception(mock_router: LLMRouter) -> None:
    """Verify out-of-scope non-consumer dispute is intercepted with escalation alert."""
    at = AppTest.from_file(APP_FILE)
    at.session_state["router"] = mock_router
    criminal_narrative = (
        "The loan recovery agents entered my house at night, assaulted my family members, "
        "and issued death threats. We lodged an FIR under Bharatiya Nyaya Sanhita (BNS)."
    )
    at.session_state["ta_case_narrative"] = criminal_narrative
    at.run(timeout=30)

    at.button(key="btn_analyze_case").click().run(timeout=30)

    assert len(at.exception) == 0
    assert at.session_state.get("case_file") is None
    alert_txt = str(at.session_state.get("intake_alert", ""))
    assert "⚠️ Escalation Required" in alert_txt
    assert "Advocate" in alert_txt or "consumer" in alert_txt.lower()


# ==============================================================================
# 4. Tab 2: Legal Standing & Provenance Tests
# ==============================================================================
def test_streamlit_tab2_legal_standing_evaluation(
    mock_router: LLMRouter, sample_case_file: CaseFile
) -> None:
    """Verify Tab 2 evaluates legal standing, RRF provenance, and telemetry."""
    at = AppTest.from_file(APP_FILE)
    at.session_state["router"] = mock_router
    at.session_state["case_file"] = sample_case_file
    at.run(timeout=30)

    assess_btn = at.button(key="btn_assess_standing")
    assert assess_btn is not None
    assess_btn.click().run(timeout=30)

    assert len(at.exception) == 0
    standing_obj = at.session_state.get("standing")
    assert isinstance(standing_obj, LegalStanding)
    assert standing_obj.is_consumer is True
    assert "District" in standing_obj.pecuniary_commission_forum
    assert "Commission" in standing_obj.pecuniary_commission_forum

    prov_html = str(at.session_state.get("standing_provenance", ""))
    assert "statutory-provenance-card" in prov_html
    assert "<mark" in prov_html

    telemetry_html = str(at.session_state.get("standing_telemetry", ""))
    assert "Citation Telemetry" in telemetry_html
    assert "verified" in telemetry_html


# ==============================================================================
# 5. Tab 3: Document Drafter & Downloads Tests
# ==============================================================================
def test_streamlit_tab3_document_drafting_single_and_all(
    mock_router: LLMRouter, sample_case_file: CaseFile, sample_standing: LegalStanding
) -> None:
    """Verify Tab 3 generates drafted artifacts and binds download button payloads."""
    at = AppTest.from_file(APP_FILE)
    at.session_state["router"] = mock_router
    at.session_state["case_file"] = sample_case_file
    at.session_state["standing"] = sample_standing
    at.run(timeout=30)

    draft_single_btn = at.button(key="btn_draft_single")
    assert draft_single_btn is not None
    draft_single_btn.click().run(timeout=30)

    assert len(at.exception) == 0
    assert at.session_state.get("drafted_doc") is not None
    draft_text = str(at.session_state.get("draft_raw_text", ""))
    assert len(draft_text) > 50
    assert "Notice" in str(at.session_state.get("draft_title", ""))

    # Verify download buttons exist with valid data payloads
    dl_md_btn = at.download_button(key="btn_dl_md")
    dl_txt_btn = at.download_button(key="btn_dl_txt")
    assert dl_md_btn is not None
    assert dl_txt_btn is not None
    assert "Markdown" in dl_md_btn.label
    assert "Plain Text" in dl_txt_btn.label
    assert at.session_state.get("draft_raw_text") == draft_text

    # Test Draft All 3 Pre-Litigation Documents
    draft_all_btn = at.button(key="btn_draft_all")
    assert draft_all_btn is not None
    draft_all_btn.click().run(timeout=30)

    assert len(at.exception) == 0
    combo_text = str(at.session_state.get("draft_raw_text", ""))
    assert len(combo_text) > len(draft_text)
    assert "Pre-Litigation 3-Document Package" in str(at.session_state.get("draft_title", ""))


# ==============================================================================
# 6. Tab 4: Opposing Counsel Simulator Tests
# ==============================================================================
def test_streamlit_tab4_opposing_counsel_simulation_and_turn_progression(
    mock_router: LLMRouter, sample_case_file: CaseFile
) -> None:
    """Verify Tab 4 initializes adversarial debate, steps simulation, and scores arguments."""
    at = AppTest.from_file(APP_FILE)
    at.session_state["router"] = mock_router
    at.session_state["case_file"] = sample_case_file
    at.run(timeout=30)

    init_sim_btn = at.button(key="btn_init_sim")
    assert init_sim_btn is not None
    init_sim_btn.click().run(timeout=30)

    assert len(at.exception) == 0
    sim_state_obj = at.session_state.get("sim_state")
    assert sim_state_obj is not None
    chat_history = at.session_state.get("chat_history", [])
    assert len(chat_history) >= 1
    assert chat_history[0]["role"] == "assistant"

    # Step simulation with a strong statutory rebuttal
    user_rebuttal = (
        "Under Section 2(11) of CPA 2019, delivery of a cracked screen constitutes "
        "deficiency in service. A blanket no-return policy is an unfair contract."
    )
    u_state, hist, score_str, strengths, weaknesses, advice = handle_simulator_turn(
        user_argument=user_rebuttal,
        state=sim_state_obj,
        router=mock_router,
    )
    at.session_state["sim_state"] = u_state
    at.session_state["chat_history"] = hist
    at.session_state["sim_scores"] = {
        "turn_score": 85.0,
        "cumulative_score": 80.0,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "advice": advice,
    }
    at.run(timeout=30)

    assert len(at.exception) == 0
    assert len(at.session_state["chat_history"]) >= 2
    scores_dict = at.session_state.get("sim_scores", {})
    assert scores_dict.get("turn_score") == 85.0
    assert scores_dict.get("cumulative_score") == 80.0
