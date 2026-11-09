"""Empirical Challenger 2: Adversarial Stress Test Suite for UI and CSS.

Validates:
1. `LEGAL_SAATHI_CUSTOM_CSS` syntax integrity, brace balancing, and DESIGN.md token mappings.
2. Verified resolution of the 3 reported defects:
   - Sidebar input borders: 1px solid #ADABA5
   - Expander summary: #FAFAF9 background, #0F0E0D text/svg
   - Sidebar labels: #8F8B85 text color
3. Streamlit DOM safety: st.markdown with unsafe_allow_html=True renders without errors.
4. Full operational stress testing of all 4 UI tabs and sidebar controls via AppTest.
5. Re-run stability and endurance under adversarial inputs.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser
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
from legal_assistant.ui.app import LEGAL_SAATHI_CUSTOM_CSS
from tests.test_ui import MockLLMClient

APP_FILE = str(
    Path(__file__).resolve().parent.parent / "src" / "legal_assistant" / "ui" / "app.py"
)


# ==============================================================================
# Deterministic Fixtures
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
    for p, m in [
        ("groq", "llama-3.1-8b-instant"),
        ("ollama", "llama3.2:3b"),
        ("openai", "gpt-4o-mini"),
        ("gemini", "gemini-1.5-flash"),
    ]:
        router.register_client(p, MockLLMClient(provider_name=p, model_name=m))
    return router


@pytest.fixture
def sample_case_file() -> CaseFile:
    """Realistic CaseFile for multi-tab stress testing."""
    return CaseFile(
        case_id="case_css_stress_001",
        title="Laptop Motherboard Defect within Warranty",
        disputed_amount_inr=85000.0,
        transaction_date="2025-11-10",
        cause_of_action_date="2025-12-05",
        facts_summary=(
            "Complainant bought a premium laptop on 2025-11-10 for Rs 85,000. Within 3 weeks, "
            "the motherboard failed completely. Authorized service center refused warranty "
            "replacement citing arbitrary physical damage claims without inspection report."
        ),
        opposite_parties=[
            OppositeParty(name="Apex Computer Electronics", role="Manufacturer"),
            OppositeParty(name="Digital MegaStore", role="Authorized Seller"),
        ],
        timeline=[
            TimelineEvent(
                date="2025-11-10",
                significance="Purchase",
                description="Laptop purchased for Rs 85,000.",
            ),
            TimelineEvent(
                date="2025-12-05",
                significance="Motherboard Failure",
                description="System failed to power on; submitted to service center.",
            ),
        ],
        complainant=PartyDetails(
            name="Pooja Verma",
            email="pooja.verma@example.org",
            phone="+91-9811223344",
            city="Bengaluru",
            state="Karnataka",
        ),
    )


@pytest.fixture
def sample_standing() -> LegalStanding:
    """Realistic LegalStanding for standing and drafter testing."""
    return LegalStanding(
        is_consumer=True,
        consumer_rationale="Complainant purchased computer system for personal consumption.",
        pecuniary_commission_forum="District Commission",
        pecuniary_jurisdiction_limit="District Commission (Up to ₹50 Lakhs)",
        jurisdiction_rationale="Territorial jurisdiction in Bengaluru under Section 34(2).",
        limitation_status="within_limitation",
        limitation_rationale="Within 2 years of cause of action under Section 69 CPA 2019.",
        estimated_timeline="30-60 days",
        statutory_violations=[
            StatutoryViolation(
                statute="Consumer Protection Act, 2019",
                section_or_rule="Section 2(11)",
                title="Deficiency in Service",
                violation_nature="deficiency_in_service",
                explanation="Refusal to service within manufacturer warranty period.",
            ),
            StatutoryViolation(
                statute="Consumer Protection Act, 2019",
                section_or_rule="Section 2(47)",
                title="Unfair Trade Practice",
                violation_nature="unfair_trade_practice",
                explanation="Falsely claiming user damage to evade warranty obligation.",
            ),
        ],
        estimated_costs=CostEstimate(
            court_fees_inr=2000.0,
            notice_costs_inr=150.0,
            total_estimated_out_of_pocket_inr="₹2,150 total out of pocket",
        ),
    )


# ==============================================================================
# Suite 1: CSS Structural & Syntax Integrity
# ==============================================================================
class TestCSSSyntaxAndIntegrity:
    """Rigorous structural and syntax checks for LEGAL_SAATHI_CUSTOM_CSS."""

    def test_css_is_valid_html_style_block(self) -> None:
        """Verify CSS string is wrapped in exactly one <style>...</style> block."""
        assert LEGAL_SAATHI_CUSTOM_CSS.startswith("<style>\n")
        assert LEGAL_SAATHI_CUSTOM_CSS.endswith("</style>\n")

        class TagTracker(HTMLParser):
            def __init__(self) -> None:
                super().__init__()
                self.opened: list[str] = []
                self.closed: list[str] = []

            def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
                self.opened.append(tag)

            def handle_endtag(self, tag: str) -> None:
                self.closed.append(tag)

        tracker = TagTracker()
        tracker.feed(LEGAL_SAATHI_CUSTOM_CSS)
        tracker.close()

        assert tracker.opened == ["style"]
        assert tracker.closed == ["style"]

    def test_css_curly_braces_and_parentheses_balance(self) -> None:
        """Verify all curly braces, parentheses, and brackets in CSS are strictly balanced."""
        css_body = LEGAL_SAATHI_CUSTOM_CSS.replace("<style>\n", "").replace("</style>\n", "")
        clean_css = re.sub(r"/\*.*?\*/", "", css_body, flags=re.DOTALL)

        open_curly = clean_css.count("{")
        close_curly = clean_css.count("}")
        assert open_curly == close_curly, f"Unbalanced braces: {open_curly} vs {close_curly}"
        assert open_curly > 0, "No CSS rules found"

        open_paren = clean_css.count("(")
        close_paren = clean_css.count(")")
        assert open_paren == close_paren, f"Unbalanced parens: {open_paren} vs {close_paren}"

        open_bracket = clean_css.count("[")
        close_bracket = clean_css.count("]")
        assert open_bracket == close_bracket, (
            f"Unbalanced brackets: {open_bracket} vs {close_bracket}"
        )

    def test_css_exact_defect_fixes_verified(self) -> None:
        """Verify the 3 defects from ORIGINAL_REQUEST.md are strictly resolved in CSS."""
        # Defect 1: Input borders must be 1px solid #ADABA5
        assert '[data-testid="stSidebar"] [data-baseweb="input"]' in LEGAL_SAATHI_CUSTOM_CSS
        assert '[data-testid="stSidebar"] [data-baseweb="select"] > div' in LEGAL_SAATHI_CUSTOM_CSS
        assert "border: 1px solid #ADABA5 !important;" in LEGAL_SAATHI_CUSTOM_CSS

        # Defect 2: Expander summary background #FAFAF9, text & icons #0F0E0D
        assert (
            '[data-testid="stSidebar"] [data-testid="stExpander"] details summary'
            in LEGAL_SAATHI_CUSTOM_CSS
        )
        assert "background-color: #FAFAF9 !important;" in LEGAL_SAATHI_CUSTOM_CSS
        assert "color: #0F0E0D !important;" in LEGAL_SAATHI_CUSTOM_CSS
        assert "-webkit-text-fill-color: #0F0E0D !important;" in LEGAL_SAATHI_CUSTOM_CSS
        assert "fill: #0F0E0D !important;" in LEGAL_SAATHI_CUSTOM_CSS

        # Defect 3: Sidebar typography labels #8F8B85
        assert '[data-testid="stSidebar"] label' in LEGAL_SAATHI_CUSTOM_CSS
        assert (
            '[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p'
            in LEGAL_SAATHI_CUSTOM_CSS
        )
        assert "color: #8F8B85 !important;" in LEGAL_SAATHI_CUSTOM_CSS

    def test_css_tokens_alignment_with_design_system(self) -> None:
        """Verify essential DESIGN.md tokens are present in root definition."""
        assert ":root {" in LEGAL_SAATHI_CUSTOM_CSS
        expected_tokens = [
            "--font-serif",
            "--font-sans",
            "--ink: #0F0E0D;",
            "--on-primary: #FFFFFF;",
            "--ink-secondary: #33312C;",
            "--muted: #706D66;",
            "--muted-soft: #8F8B85;",
            "--surface: #FFFFFF;",
            "--surface-warm: #FAFAF9;",
            "--surface-muted: #F2F1F0;",
            "--surface-dark: #1F1D1A;",
            "--surface-black: #000000;",
            "--hairline: #CCCAC6;",
            "--border-strong: #ADABA5;",
            "--border-dark: #33312C;",
            "--highlight: #F6F202;",
            "--focus-ring: #99C8FF;",
        ]
        for token in expected_tokens:
            assert token in LEGAL_SAATHI_CUSTOM_CSS, f"Missing design token: {token}"


# ==============================================================================
# Suite 2: Streamlit Runtime Rendering & CSS Injection
# ==============================================================================
class TestStreamlitCSSRuntimeRendering:
    """Verify Streamlit runtime accepts and renders LEGAL_SAATHI_CUSTOM_CSS cleanly."""

    def test_apptest_renders_custom_css_in_markdown(self, mock_router: LLMRouter) -> None:
        """Verify AppTest executes app.py and injects the CSS markdown node."""
        at = AppTest.from_file(APP_FILE)
        at.session_state["router"] = mock_router
        at.run(timeout=30)

        assert len(at.exception) == 0, f"App execution failed with exceptions: {at.exception}"

        # Find markdown element containing the CSS style block
        css_markdowns = [
            m for m in at.markdown if "<style>" in m.value and "Harvey Editorial" in m.value
        ]
        assert len(css_markdowns) == 1, (
            f"Expected 1 custom CSS markdown node, got {len(css_markdowns)}"
        )
        assert css_markdowns[0].value.strip() == LEGAL_SAATHI_CUSTOM_CSS.strip()

    def test_css_does_not_corrupt_subsequent_markdown_or_titles(
        self, mock_router: LLMRouter
    ) -> None:
        """Verify subsequent Streamlit markdown/title elements are not corrupted or truncated."""
        at = AppTest.from_file(APP_FILE)
        at.session_state["router"] = mock_router
        at.run(timeout=30)

        assert len(at.title) >= 1
        assert "Legal Saathi — AI Consumer Lawyer" in at.title[0].value

        # Tab headers intact
        assert len(at.tabs) == 4
        tab_names = [t.label for t in at.tabs]
        assert any("Case Intake" in name for name in tab_names)
        assert any("Legal Standing" in name for name in tab_names)
        assert any("Document Drafter" in name for name in tab_names)
        assert any("Opposing Counsel" in name for name in tab_names)


# ==============================================================================
# Suite 3: Sidebar Controls Functional Verification
# ==============================================================================
class TestSidebarControlsAndStyling:
    """Stress test sidebar controls with custom CSS active."""

    def test_sidebar_all_provider_switching(self, mock_router: LLMRouter) -> None:
        """Test switching across all 4 supported providers in the styled sidebar selectbox."""
        at = AppTest.from_file(APP_FILE)
        at.session_state["router"] = mock_router
        at.run(timeout=30)

        providers = ["groq", "ollama", "openai", "gemini"]
        for p in providers:
            sb_select = at.sidebar.selectbox(key="sb_provider_select")
            assert sb_select is not None
            sb_select.select(p)

            apply_btn = at.sidebar.button(key="sb_btn_apply")
            assert apply_btn is not None
            apply_btn.click().run(timeout=30)

            assert len(at.exception) == 0
            assert at.session_state.get("active_provider") == p

    def test_sidebar_styled_buttons_ping_execution(self, mock_router: LLMRouter) -> None:
        """Verify sidebar ping button functions cleanly without CSS interference."""
        at = AppTest.from_file(APP_FILE)
        at.session_state["router"] = mock_router
        at.run(timeout=30)

        ping_btn = at.sidebar.button(key="sb_btn_ping")
        assert ping_btn is not None
        ping_btn.click().run(timeout=30)

        assert len(at.exception) == 0
        assert len(at.sidebar.success) >= 1 or len(at.sidebar.error) >= 1

    def test_sidebar_expander_inputs_entry(self, mock_router: LLMRouter) -> None:
        """Test interacting with styled inputs within the sidebar expander."""
        at = AppTest.from_file(APP_FILE)
        at.session_state["router"] = mock_router
        at.run(timeout=30)

        # Groq model selectbox in sidebar expander
        groq_model_sb = at.sidebar.selectbox(key="sb_groq_model")
        assert groq_model_sb is not None
        groq_model_sb.select("llama-3.3-70b-versatile").run(timeout=30)
        assert len(at.exception) == 0

        # Ollama model text input in sidebar expander
        ollama_model_ti = at.sidebar.text_input(key="sb_ollama_model")
        assert ollama_model_ti is not None
        ollama_model_ti.set_value("llama3.2:1b").run(timeout=30)
        assert len(at.exception) == 0


# ==============================================================================
# Suite 4: All 4 UI Tabs End-to-End Stress Verification
# ==============================================================================
class TestAllFourUITabsFunctionality:
    """Stress test all 4 UI tabs end-to-end to ensure zero styling regressions."""

    def test_tab1_case_intake_workflow(
        self, mock_router: LLMRouter, sample_case_file: CaseFile
    ) -> None:
        """Verify Tab 1: Load sample, custom text entry, analyze button, intake parsing."""
        at = AppTest.from_file(APP_FILE)
        at.session_state["router"] = mock_router
        at.run(timeout=30)

        # 1. Load sample dispute
        load_btn = at.button(key="btn_load_sample")
        assert load_btn is not None
        load_btn.click().run(timeout=30)
        assert len(at.exception) == 0
        assert len(str(at.session_state.get("ta_case_narrative", ""))) > 50

        # 2. Enter adversarial / HTML-containing narrative
        adversarial_text = (
            "I bought a refrigerator for Rs 35,000. <script>alert('xss')</script> "
            "It stopped working within 2 days. <b>Compressor is burnt</b>. Merchant refused refund."
        )
        at.text_area(key="ta_case_narrative").set_value(adversarial_text).run(timeout=30)
        assert len(at.exception) == 0

        # 3. Click Analyze
        analyze_btn = at.button(key="btn_analyze_case")
        assert analyze_btn is not None
        analyze_btn.click().run(timeout=30)
        assert len(at.exception) == 0
        assert at.session_state.get("case_file") is not None

    def test_tab2_legal_standing_and_provenance(
        self, mock_router: LLMRouter, sample_case_file: CaseFile
    ) -> None:
        """Verify Tab 2: Assess standing, render provenance cards and telemetry banner."""
        at = AppTest.from_file(APP_FILE)
        at.session_state["router"] = mock_router
        at.session_state["case_file"] = sample_case_file
        at.run(timeout=30)

        assess_btn = at.button(key="btn_assess_standing")
        assert assess_btn is not None
        assess_btn.click().run(timeout=30)

        assert len(at.exception) == 0
        standing = at.session_state.get("standing")
        assert isinstance(standing, LegalStanding)
        assert standing.is_consumer is True

        # Verify provenance HTML and telemetry
        prov = str(at.session_state.get("standing_provenance", ""))
        assert "statutory-provenance-card" in prov
        assert "<mark" in prov

        telemetry = str(at.session_state.get("standing_telemetry", ""))
        assert "Citation Telemetry" in telemetry

    def test_tab3_document_drafter_and_editor(
        self,
        mock_router: LLMRouter,
        sample_case_file: CaseFile,
        sample_standing: LegalStanding,
    ) -> None:
        """Verify Tab 3: Draft single document, radio select, draft all, markdown editor."""
        at = AppTest.from_file(APP_FILE)
        at.session_state["router"] = mock_router
        at.session_state["case_file"] = sample_case_file
        at.session_state["standing"] = sample_standing
        at.run(timeout=30)

        # 1. Draft selected document via radio
        doc_radio = at.radio(key="rad_doc_choice")
        assert doc_radio is not None
        doc_radio.set_value("Legal Demand Notice (15-Day)").run(timeout=30)

        at.button(key="btn_draft_single").click().run(timeout=30)
        assert len(at.exception) == 0
        assert at.session_state.get("drafted_doc") is not None
        notice_text = str(at.session_state.get("draft_raw_text", ""))
        assert len(notice_text) > 50

        # 2. Draft All 3 Documents
        at.button(key="btn_draft_all").click().run(timeout=30)
        assert len(at.exception) == 0
        combo_text = str(at.session_state.get("draft_raw_text", ""))
        assert len(combo_text) > len(notice_text)

        # 3. Edit inside markdown editor
        editor = at.text_area(key="ta_raw_markdown_editor")
        assert editor is not None
        editor.set_value(combo_text + "\n\n<!-- Custom User Amendment -->").run(timeout=30)
        assert len(at.exception) == 0

    def test_tab4_opposing_counsel_simulator_flow(
        self, mock_router: LLMRouter, sample_case_file: CaseFile
    ) -> None:
        """Verify Tab 4: Simulator initialization, multi-turn dialogue, argument evaluation."""
        at = AppTest.from_file(APP_FILE)
        at.session_state["router"] = mock_router
        at.session_state["case_file"] = sample_case_file
        at.run(timeout=30)

        # 1. Initialize Debate
        at.button(key="btn_init_sim").click().run(timeout=30)
        assert len(at.exception) == 0
        assert at.session_state.get("sim_state") is not None
        assert len(at.session_state.get("chat_history", [])) == 1

        # 2. Submit consumer rebuttal via chat_input
        ci = at.chat_input(key="ci_consumer_rebuttal")
        assert ci is not None
        ci.set_value(
            "Under Section 2(47) and Section 84 of CPA 2019, arbitrary disclaimer of warranty "
            "for motherboard hardware defect constitutes unfair trade practice."
        ).run(timeout=30)
        assert len(at.exception) == 0
        assert len(at.session_state.get("chat_history", [])) >= 2
        assert at.session_state.get("sim_scores") is not None


# ==============================================================================
# Suite 5: Endurance & Re-run Stress
# ==============================================================================
class TestEnduranceAndReRunStress:
    """Endurance tests verifying repeated application runs without state leaks."""

    def test_repeated_app_runs_endurance(self, mock_router: LLMRouter) -> None:
        """Run app 5 times sequentially to verify CSS stability under repeated execution."""
        for run_idx in range(5):
            at = AppTest.from_file(APP_FILE)
            at.session_state["router"] = mock_router
            at.run(timeout=30)
            assert len(at.exception) == 0, f"Exception on run #{run_idx}: {at.exception}"
            assert len(at.tabs) == 4
            css_elements = [m for m in at.markdown if "<style>" in m.value]
            assert len(css_elements) == 1
