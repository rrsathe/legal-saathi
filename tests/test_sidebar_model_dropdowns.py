"""Verification tests for Gemini and OpenAI sidebar model dropdowns and CSS formatting."""

from __future__ import annotations

import re
from pathlib import Path

from pydantic import SecretStr
from streamlit.testing.v1 import AppTest

from legal_assistant.config import Settings
from legal_assistant.llm.router import LLMRouter
from legal_assistant.ui.app import LEGAL_SAATHI_CUSTOM_CSS
from tests.test_ui import MockLLMClient

APP_FILE = str(
    Path(__file__).resolve().parent.parent / "src" / "legal_assistant" / "ui" / "app.py"
)


def create_test_router(settings: Settings | None = None) -> LLMRouter:
    """Create configured LLMRouter populated with mock clients."""
    if settings is None:
        settings = Settings(
            llm_provider="groq",
            groq_api_key=SecretStr("mock-key"),
            openai_api_key=SecretStr("sk-mock-key"),
            gemini_api_key=SecretStr("AIza-mock-key"),
        )
    router = LLMRouter(settings=settings)
    for p, m in [
        ("groq", "llama-3.1-8b-instant"),
        ("ollama", "llama3.2:3b"),
        ("openai", "gpt-4o-mini"),
        ("gemini", "gemini-2.5-flash"),
    ]:
        router.register_client(p, MockLLMClient(provider_name=p, model_name=m))
    return router


def test_openai_model_dropdown_options_and_selection() -> None:
    """Verify OpenAI model dropdown exists with options gpt-4o and gpt-4o-mini."""
    settings = Settings(
        llm_provider="groq",
        groq_api_key=SecretStr("mock-key"),
        openai_api_key=SecretStr("sk-mock-key"),
        gemini_api_key=SecretStr("AIza-mock-key"),
    )
    at = AppTest.from_file(APP_FILE)
    at.session_state["settings"] = settings
    at.session_state["router"] = create_test_router(settings)
    at.run(timeout=30)

    oa_sb = at.sidebar.selectbox(key="sb_openai_model")
    assert oa_sb is not None, "OpenAI model dropdown not found in sidebar"
    assert list(oa_sb.options) == ["gpt-4o", "gpt-4o-mini"]
    assert oa_sb.value in ["gpt-4o", "gpt-4o-mini"]

    # Select alternative option and apply
    oa_sb.select("gpt-4o").run(timeout=30)
    assert len(at.exception) == 0

    # Select active provider as openai and click apply
    provider_sb = at.sidebar.selectbox(key="sb_provider_select")
    assert provider_sb is not None
    provider_sb.select("openai")

    apply_btn = at.sidebar.button(key="sb_btn_apply")
    assert apply_btn is not None
    apply_btn.click().run(timeout=30)
    assert len(at.exception) == 0
    assert at.session_state.get("active_provider") == "openai"
    assert at.session_state["settings"].openai_model == "gpt-4o"


def test_gemini_model_dropdown_options_and_selection() -> None:
    """Verify Gemini model dropdown exists with options gemini-2.5-flash and gemini-2.5-pro."""
    settings = Settings(
        llm_provider="groq",
        groq_api_key=SecretStr("mock-key"),
        openai_api_key=SecretStr("sk-mock-key"),
        gemini_api_key=SecretStr("AIza-mock-key"),
    )
    at = AppTest.from_file(APP_FILE)
    at.session_state["settings"] = settings
    at.session_state["router"] = create_test_router(settings)
    at.run(timeout=30)

    gem_sb = at.sidebar.selectbox(key="sb_gemini_model")
    assert gem_sb is not None, "Gemini model dropdown not found in sidebar"
    assert list(gem_sb.options) == ["gemini-2.5-flash", "gemini-2.5-pro"]
    assert gem_sb.value in ["gemini-2.5-flash", "gemini-2.5-pro"]

    # Select alternative option and apply
    gem_sb.select("gemini-2.5-pro").run(timeout=30)
    assert len(at.exception) == 0

    # Select active provider as gemini and click apply
    provider_sb = at.sidebar.selectbox(key="sb_provider_select")
    assert provider_sb is not None
    provider_sb.select("gemini")

    apply_btn = at.sidebar.button(key="sb_btn_apply")
    assert apply_btn is not None
    apply_btn.click().run(timeout=30)
    assert len(at.exception) == 0
    assert at.session_state.get("active_provider") == "gemini"
    assert at.session_state["settings"].gemini_model == "gemini-2.5-pro"


def test_dropdown_initial_index_with_custom_settings() -> None:
    """Verify dropdowns correctly reflect initial settings configurations."""
    # Test OpenAI gpt-4o initial index
    at_oa = AppTest.from_file(APP_FILE)
    at_oa.session_state["settings"] = Settings(openai_model="gpt-4o")
    at_oa.run(timeout=30)
    assert at_oa.sidebar.selectbox(key="sb_openai_model").value == "gpt-4o"

    # Test Gemini gemini-2.5-pro initial index
    at_gem_pro = AppTest.from_file(APP_FILE)
    at_gem_pro.session_state["settings"] = Settings(gemini_model="gemini-2.5-pro")
    at_gem_pro.run(timeout=30)
    assert at_gem_pro.sidebar.selectbox(key="sb_gemini_model").value == "gemini-2.5-pro"

    # Test Gemini default fallback from gemini-1.5-flash to gemini-2.5-flash
    at_gem_def = AppTest.from_file(APP_FILE)
    at_gem_def.session_state["settings"] = Settings(gemini_model="gemini-1.5-flash")
    at_gem_def.run(timeout=30)
    assert at_gem_def.sidebar.selectbox(key="sb_gemini_model").value == "gemini-2.5-flash"


def test_dropdown_robustness_with_legacy_session_state() -> None:
    """Verify that legacy or unexpected model strings in session_state do not crash."""
    at = AppTest.from_file(APP_FILE)
    at.session_state["sb_openai_model"] = "legacy-unknown-model"
    at.session_state["sb_gemini_model"] = "legacy-unknown-gemini"
    at.run(timeout=30)
    assert len(at.exception) == 0
    assert at.sidebar.selectbox(key="sb_openai_model").value in ["gpt-4o", "gpt-4o-mini"]
    assert at.sidebar.selectbox(key="sb_gemini_model").value in [
        "gemini-2.5-flash",
        "gemini-2.5-pro",
    ]


def test_dropdown_switch_round_trip() -> None:
    """Verify round-trip provider and model switching persists all model selections."""
    settings = Settings(
        llm_provider="groq",
        groq_api_key=SecretStr("mock-key"),
        openai_api_key=SecretStr("sk-mock-key"),
        gemini_api_key=SecretStr("AIza-mock-key"),
    )
    at = AppTest.from_file(APP_FILE)
    at.session_state["settings"] = settings
    at.session_state["router"] = create_test_router(settings)
    at.run(timeout=30)

    # 1. Switch to OpenAI gpt-4o
    at.sidebar.selectbox(key="sb_provider_select").select("openai")
    at.sidebar.selectbox(key="sb_openai_model").select("gpt-4o")
    at.sidebar.button(key="sb_btn_apply").click().run(timeout=30)
    assert at.session_state["active_provider"] == "openai"
    assert at.session_state["settings"].openai_model == "gpt-4o"

    # 2. Switch to Gemini gemini-2.5-pro
    at.sidebar.selectbox(key="sb_provider_select").select("gemini")
    at.sidebar.selectbox(key="sb_gemini_model").select("gemini-2.5-pro")
    at.sidebar.button(key="sb_btn_apply").click().run(timeout=30)
    assert at.session_state["active_provider"] == "gemini"
    assert at.session_state["settings"].gemini_model == "gemini-2.5-pro"

    # 3. Switch back to OpenAI gpt-4o-mini
    at.sidebar.selectbox(key="sb_provider_select").select("openai")
    at.sidebar.selectbox(key="sb_openai_model").select("gpt-4o-mini")
    at.sidebar.button(key="sb_btn_apply").click().run(timeout=30)
    assert at.session_state["active_provider"] == "openai"
    assert at.session_state["settings"].openai_model == "gpt-4o-mini"
    # Gemini selection from step 2 should still be preserved in settings
    assert at.session_state["settings"].gemini_model == "gemini-2.5-pro"


def test_dropdown_active_model_header_card_reflection() -> None:
    """Verify sidebar telemetry card reflects selected model after apply and rerun."""
    settings = Settings(
        llm_provider="groq",
        groq_api_key=SecretStr("mock-key"),
        openai_api_key=SecretStr("sk-mock-key"),
        gemini_api_key=SecretStr("AIza-mock-key"),
    )
    at = AppTest.from_file(APP_FILE)
    at.session_state["settings"] = settings
    at.session_state["router"] = create_test_router(settings)
    at.run(timeout=30)

    at.sidebar.selectbox(key="sb_provider_select").select("gemini")
    at.sidebar.selectbox(key="sb_gemini_model").select("gemini-2.5-pro")
    at.sidebar.button(key="sb_btn_apply").click().run(timeout=30)

    # Next rerun cycle reflects gemini-2.5-pro in the top status card
    at.run(timeout=30)
    assert "gemini" in at.sidebar.markdown[0].value
    assert "gemini-2.5-pro" in at.sidebar.markdown[0].value


def test_css_line_length_constraint() -> None:
    """Verify that no line in LEGAL_SAATHI_CUSTOM_CSS definition exceeds 100 characters."""
    app_text = Path(APP_FILE).read_text(encoding="utf-8")
    match = re.search(r"LEGAL_SAATHI_CUSTOM_CSS: str = \(.*?\n\)", app_text, re.DOTALL)
    assert match is not None
    css_code = match.group(0)
    for i, line in enumerate(css_code.splitlines(), 1):
        msg = f"Line {i} exceeds 100 chars ({len(line)}): {line}"
        assert len(line) <= 100, msg


def test_css_string_length_and_tokens() -> None:
    """Verify evaluated LEGAL_SAATHI_CUSTOM_CSS matches expected length and key tokens."""
    assert len(LEGAL_SAATHI_CUSTOM_CSS) == 10515
    # Token checks
    assert "#1F1D1A" in LEGAL_SAATHI_CUSTOM_CSS
    assert "#33312C" in LEGAL_SAATHI_CUSTOM_CSS
    assert "#FAFAF9" in LEGAL_SAATHI_CUSTOM_CSS
    assert "#0F0E0D" in LEGAL_SAATHI_CUSTOM_CSS
    assert "#8F8B85" in LEGAL_SAATHI_CUSTOM_CSS
    assert '[data-testid="stSidebar"] [data-baseweb="input"] > div' in LEGAL_SAATHI_CUSTOM_CSS
    assert '[data-testid="stSidebar"] [data-baseweb="select"] > div' in LEGAL_SAATHI_CUSTOM_CSS


def test_dropdown_empty_and_unknown_model_fallback() -> None:
    """Verify dropdowns fall back safely to valid indices on empty or invalid model strings."""
    settings = Settings(openai_model="", gemini_model="")
    at = AppTest.from_file(APP_FILE)
    at.session_state["settings"] = settings
    at.session_state["router"] = create_test_router(settings)
    at.run(timeout=30)
    assert len(at.exception) == 0
    assert at.sidebar.selectbox(key="sb_openai_model").value == "gpt-4o-mini"
    assert at.sidebar.selectbox(key="sb_gemini_model").value == "gemini-2.5-flash"


def test_rapid_provider_cycling_and_model_persistence() -> None:
    """Verify rapid cycling through all providers maintains session state integrity."""
    settings = Settings(
        llm_provider="groq",
        groq_api_key=SecretStr("mock-key"),
        openai_api_key=SecretStr("sk-mock-key"),
        gemini_api_key=SecretStr("AIza-mock-key"),
    )
    at = AppTest.from_file(APP_FILE)
    at.session_state["settings"] = settings
    at.session_state["router"] = create_test_router(settings)
    at.run(timeout=30)

    for provider in ["ollama", "openai", "gemini", "groq"]:
        at.sidebar.selectbox(key="sb_provider_select").select(provider)
        at.sidebar.button(key="sb_btn_apply").click().run(timeout=30)
        assert len(at.exception) == 0
        assert at.session_state["active_provider"] == provider

