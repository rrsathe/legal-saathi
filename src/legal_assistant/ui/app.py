"""Web user interface for Legal Saathi AI Consumer Lawyer.

Provides dual-entrypoint user interfaces:
1. Streamlit web application (`render_streamlit_app`): Modern, high-contrast LegalTech
   aesthetic inspired by Harvey AI and Kotaemon, equipped with hot-swappable LLM runtime
   controls in a persistent sidebar, session state persistence, 4 core workflow tabs,
   collapsible statutory provenance cards with amber visual marks, and courtroom defense
   adversarial practice simulator.
2. Gradio Blocks factory (`create_app`): Retained lightweight compatibility builder
   supporting existing automated integration, regression, and adversarial test suites.
"""

from __future__ import annotations

import contextlib
import html
import logging
import re
import time
from collections.abc import Sequence
from pathlib import Path
from typing import Any, cast

import gradio as gr
import streamlit as st
from pydantic import SecretStr

from legal_assistant.config import Settings, get_settings
from legal_assistant.guardrails.scope_checker import ScopeChecker
from legal_assistant.guardrails.verifier import CitationVerifier
from legal_assistant.llm.base import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMRateLimitError,
)
from legal_assistant.llm.router import LLMRouter
from legal_assistant.rag.chunker import StatutoryChunker
from legal_assistant.rag.hybrid_retriever import (
    InMemoryDenseRetriever,
    RetrievedChunk,
    StatutoryHybridRetriever,
)
from legal_assistant.schemas import (
    CaseFile,
    DraftedDocument,
    LegalStanding,
    OppositeParty,
    PartyDetails,
    TimelineEvent,
)
from legal_assistant.workflows.advisor import LegalAdvisor
from legal_assistant.workflows.case_builder import CaseBuilder, OutOfScopeDisputeError
from legal_assistant.workflows.drafter import DocumentDrafter
from legal_assistant.workflows.simulator import (
    DefenseTacticType,
    OpposingCounselSimulator,
    SimulatorState,
)

logger = logging.getLogger("legal_assistant.ui.app")

CORE_HIGHLIGHT_TERMS: tuple[str, ...] = (
    "unfair trade practice",
    "deficiency in service",
    "defect",
    "deficiency",
    "consumer",
    "consideration",
    "forty-eight hours",
    "thirty days",
    "grievance officer",
    "refund",
    "return",
    "misleading advertisement",
    "unfair contract",
    "product liability",
    "district commission",
    "state commission",
    "limitation period",
    "condonation of delay",
)

LEGAL_SAATHI_CUSTOM_CSS: str = (
    "<style>\n"
    "/* " + "=" * 74 + "\n"
    "   Legal Saathi Design System: Harvey Editorial Aesthetic (DESIGN.md)\n"
    "   " + "=" * 74 + " */\n\n"
    "@import url('https://fonts.googleapis.com/css2?"
    "family=Inter:wght@400;500&"
    "family=Newsreader:opsz,wght@6..72,400&display=swap');\n\n"
    ":root {\n"
    "    --ink: #0F0E0D;\n"
    "    --on-primary: #FFFFFF;\n"
    "    --surface-warm: #FAFAF9;\n"
    "    --ink-secondary: #33312C;\n"
    "    --muted: #706D66;\n"
    "    --muted-soft: #8F8B85;\n"
    "    --surface: #FFFFFF;\n"
    "    --surface-muted: #F2F1F0;\n"
    "    --surface-dark: #1F1D1A;\n"
    "    --surface-black: #000000;\n"
    "    --hairline: #CCCAC6;\n"
    "    --border-strong: #ADABA5;\n"
    "    --border-dark: #33312C;\n"
    "    --highlight: #F6F202;\n"
    "    --focus-ring: #99C8FF;\n"
    "    --focus-ring-strong: #005FCC;\n"
    "}\n\n"
    "/* Chrome Cleanup */\n"
    "#MainMenu, footer, header {\n"
    "    visibility: hidden !important;\n"
    "}\n"
    "[data-testid=\"stDeployButton\"] {\n"
    "    display: none !important;\n"
    "}\n\n"
    "/* Layout & Container Padding */\n"
    ".block-container {\n"
    "    padding-top: 2rem !important;\n"
    "    padding-bottom: 3rem !important;\n"
    "    max-width: 1400px !important;\n"
    "    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "
    "\"Segoe UI\", Roboto, sans-serif !important;\n"
    "    background-color: var(--surface-warm) !important;\n"
    "    color: var(--ink) !important;\n"
    "}\n\n"
    "html, body, [data-testid=\"stAppViewContainer\"] {\n"
    "    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "
    "\"Segoe UI\", Roboto, sans-serif !important;\n"
    "    background-color: var(--surface-warm) !important;\n"
    "    color: var(--ink) !important;\n"
    "}\n\n"
    "/* Typography Hierarchy - STRICTLY weights 400 and 500. ZERO 600/700. */\n"
    "h1, h2, [data-testid=\"stTitle\"] {\n"
    "    font-family: 'Newsreader', Georgia, serif !important;\n"
    "    font-weight: 400 !important;\n"
    "    line-height: 1.05 !important;\n"
    "    letter-spacing: -0.015em !important;\n"
    "    color: var(--ink) !important;\n"
    "}\n\n"
    "h3, h4, h5, h6 {\n"
    "    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "
    "\"Segoe UI\", Roboto, sans-serif !important;\n"
    "    font-weight: 500 !important;\n"
    "    color: var(--ink) !important;\n"
    "    letter-spacing: -0.01em !important;\n"
    "}\n\n"
    "p, div, li, span {\n"
    "    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "
    "\"Segoe UI\", Roboto, sans-serif;\n"
    "    font-weight: 400;\n"
    "}\n\n"
    ".stMarkdown p, .stMarkdown div, .stMarkdown li {\n"
    "    line-height: 1.5;\n"
    "    color: var(--ink);\n"
    "}\n\n"
    "/* Statutory Provenance Collapsible Cards */\n"
    "details.statutory-provenance-card {\n"
    "    transition: all 0.15s ease-in-out;\n"
    "    box-shadow: none !important;\n"
    "}\n"
    "details.statutory-provenance-card summary::-webkit-details-marker {\n"
    "    display: none;\n"
    "}\n"
    "details.statutory-provenance-card summary {\n"
    "    list-style: none;\n"
    "    outline: none;\n"
    "}\n"
    "details.statutory-provenance-card summary:hover {\n"
    "    background-color: var(--surface-muted) !important;\n"
    "}\n\n"
    "/* Electric Yellow Highlighter */\n"
    "mark {\n"
    "    background-color: #F6F202 !important;\n"
    "    color: #0F0E0D !important;\n"
    "    font-weight: 500 !important;\n"
    "    padding: 1px 4px !important;\n"
    "    border-radius: 3px !important;\n"
    "}\n\n"
    "/* Controls: Buttons, Inputs, Selects - 4px radius, zero shadow */\n"
    "button, input, textarea, select, [data-baseweb=\"select\"] {\n"
    "    border-radius: 4px !important;\n"
    "    box-shadow: none !important;\n"
    "}\n\n"
    "/* Primary CTA Button */\n"
    "button[kind=\"primary\"], .stButton > button[kind=\"primary\"] {\n"
    "    background-color: #0F0E0D !important;\n"
    "    color: #FAFAF9 !important;\n"
    "    border: 1px solid #0F0E0D !important;\n"
    "    border-radius: 4px !important;\n"
    "    height: 48px !important;\n"
    "    padding: 0 20px !important;\n"
    "    font-size: 16px !important;\n"
    "    font-weight: 500 !important;\n"
    "    transition: background-color 0.15s ease !important;\n"
    "}\n"
    "button[kind=\"primary\"]:hover, .stButton > button[kind=\"primary\"]:hover {\n"
    "    background-color: #33312C !important;\n"
    "    border-color: #33312C !important;\n"
    "    color: #FAFAF9 !important;\n"
    "}\n"
    "button[kind=\"primary\"]:focus, .stButton > button[kind=\"primary\"]:focus {\n"
    "    box-shadow: #8F8B85 0px 0px 0px 2px, #8F8B85 0px 0px 0px 4px !important;\n"
    "    outline: none !important;\n"
    "}\n\n"
    "/* Secondary / Standard Buttons */\n"
    "button[kind=\"secondary\"], .stButton > button:not([kind=\"primary\"]) {\n"
    "    background-color: transparent !important;\n"
    "    color: #0F0E0D !important;\n"
    "    border: 1px solid #0F0E0D !important;\n"
    "    border-radius: 4px !important;\n"
    "    height: 40px !important;\n"
    "    padding: 0 16px !important;\n"
    "    font-size: 14px !important;\n"
    "    font-weight: 500 !important;\n"
    "    transition: all 0.15s ease !important;\n"
    "}\n"
    "button[kind=\"secondary\"]:hover,\n"
    ".stButton > button:not([kind=\"primary\"]):hover {\n"
    "    background-color: #0F0E0D !important;\n"
    "    color: #FAFAF9 !important;\n"
    "}\n\n"
    "/* Download Buttons */\n"
    "[data-testid=\"stDownloadButton\"] > button {\n"
    "    background-color: transparent !important;\n"
    "    color: #0F0E0D !important;\n"
    "    border: 1px solid #0F0E0D !important;\n"
    "    border-radius: 4px !important;\n"
    "    height: 40px !important;\n"
    "    font-size: 14px !important;\n"
    "    font-weight: 500 !important;\n"
    "}\n"
    "[data-testid=\"stDownloadButton\"] > button:hover {\n"
    "    background-color: #0F0E0D !important;\n"
    "    color: #FAFAF9 !important;\n"
    "}\n\n"
    "/* Form Inputs & Textareas */\n"
    "input[type=\"text\"], input[type=\"password\"], textarea, [data-baseweb=\"input\"] {\n"
    "    background-color: #FFFFFF !important;\n"
    "    color: #0F0E0D !important;\n"
    "    border: 1px solid #ADABA5 !important;\n"
    "    border-radius: 4px !important;\n"
    "    font-size: 14px !important;\n"
    "    font-weight: 400 !important;\n"
    "}\n"
    "input[type=\"text\"]:focus, input[type=\"password\"]:focus, textarea:focus {\n"
    "    border-color: #0F0E0D !important;\n"
    "    box-shadow: none !important;\n"
    "    outline: none !important;\n"
    "}\n\n"
    "/* Tab Headers */\n"
    "button[data-baseweb=\"tab\"] {\n"
    "    font-size: 14px !important;\n"
    "    font-weight: 500 !important;\n"
    "    color: #706D66 !important;\n"
    "    padding: 14px 20px !important;\n"
    "    border-bottom: 2px solid transparent !important;\n"
    "}\n"
    "button[data-baseweb=\"tab\"][aria-selected=\"true\"] {\n"
    "    color: #0F0E0D !important;\n"
    "    border-bottom: 2px solid #0F0E0D !important;\n"
    "    background-color: transparent !important;\n"
    "}\n"
    "[data-baseweb=\"tab-highlight\"] {\n"
    "    background-color: #0F0E0D !important;\n"
    "}\n"
    "[data-baseweb=\"tab-border\"] {\n"
    "    background-color: #CCCAC6 !important;\n"
    "}\n\n"
    "/* Inverted Dark Sidebar */\n"
    "[data-testid=\"stSidebar\"],\n"
    "[data-testid=\"stSidebar\"] > div:first-child,\n"
    "[data-testid=\"stSidebarContent\"],\n"
    "[data-testid=\"stSidebarUserContent\"],\n"
    "[data-testid=\"stSidebarHeader\"] {\n"
    "    background-color: #0F0E0D !important;\n"
    "    color: #FAFAF9 !important;\n"
    "    border-right: 1px solid #33312C !important;\n"
    "}\n"
    "[data-testid=\"stSidebarCollapseButton\"] {\n"
    "    background-color: transparent !important;\n"
    "    color: #FAFAF9 !important;\n"
    "}\n"
    "[data-testid=\"stSidebarCollapseButton\"] button {\n"
    "    background-color: transparent !important;\n"
    "    color: #FAFAF9 !important;\n"
    "    border: none !important;\n"
    "}\n"
    "[data-testid=\"stSidebarCollapseButton\"] svg {\n"
    "    fill: #FAFAF9 !important;\n"
    "    stroke: #FAFAF9 !important;\n"
    "    color: #FAFAF9 !important;\n"
    "}\n"
    "[data-testid=\"stSidebarCollapsedControl\"] svg {\n"
    "    fill: #0F0E0D !important;\n"
    "    stroke: #0F0E0D !important;\n"
    "    color: #0F0E0D !important;\n"
    "}\n"
    "[data-testid=\"stSidebar\"] p,\n"
    "[data-testid=\"stSidebar\"] span,\n"
    "[data-testid=\"stSidebar\"] div {\n"
    "    color: #FAFAF9 !important;\n"
    "}\n"
    "[data-testid=\"stSidebar\"] label,\n"
    "[data-testid=\"stSidebar\"] [data-testid=\"stWidgetLabel\"] p,\n"
    "[data-testid=\"stSidebar\"] [data-testid=\"stWidgetLabel\"] span {\n"
    "    color: #CCCAC6 !important;\n"
    "    font-size: 14px !important;\n"
    "    font-weight: 500 !important;\n"
    "}\n"
    "[data-testid=\"stSidebar\"] h1,\n"
    "[data-testid=\"stSidebar\"] h2,\n"
    "[data-testid=\"stSidebar\"] h3,\n"
    "[data-testid=\"stSidebar\"] h4,\n"
    "[data-testid=\"stSidebar\"] h5,\n"
    "[data-testid=\"stSidebar\"] h6 {\n"
    "    color: #FAFAF9 !important;\n"
    "    font-weight: 500 !important;\n"
    "}\n"
    "[data-testid=\"stSidebar\"] [data-baseweb=\"select\"],\n"
    "[data-testid=\"stSidebar\"] [data-baseweb=\"select\"] > div {\n"
    "    background-color: #1F1D1A !important;\n"
    "    color: #FAFAF9 !important;\n"
    "    border: 1px solid #33312C !important;\n"
    "    border-radius: 4px !important;\n"
    "}\n"
    "[data-testid=\"stSidebar\"] [data-baseweb=\"select\"] span,\n"
    "[data-testid=\"stSidebar\"] [data-baseweb=\"select\"] div {\n"
    "    color: #FAFAF9 !important;\n"
    "}\n"
    "[data-testid=\"stSidebar\"] [data-baseweb=\"select\"] svg {\n"
    "    fill: #FAFAF9 !important;\n"
    "    stroke: #FAFAF9 !important;\n"
    "    color: #FAFAF9 !important;\n"
    "}\n"
    "[data-testid=\"stSidebar\"] [data-baseweb=\"input\"],\n"
    "[data-testid=\"stSidebar\"] [data-baseweb=\"base-input\"],\n"
    "[data-testid=\"stSidebar\"] input[type=\"text\"],\n"
    "[data-testid=\"stSidebar\"] input[type=\"password\"] {\n"
    "    background-color: #1F1D1A !important;\n"
    "    color: #FAFAF9 !important;\n"
    "    border: 1px solid #33312C !important;\n"
    "    border-radius: 4px !important;\n"
    "}\n"
    "[data-testid=\"stSidebar\"] [data-baseweb=\"input\"] > div {\n"
    "    background-color: #1F1D1A !important;\n"
    "}\n"
    "[data-testid=\"stSidebar\"] input[type=\"text\"]:focus,\n"
    "[data-testid=\"stSidebar\"] input[type=\"password\"]:focus,\n"
    "[data-testid=\"stSidebar\"] [data-baseweb=\"input\"]:focus-within {\n"
    "    border-color: #FAFAF9 !important;\n"
    "    box-shadow: none !important;\n"
    "    outline: none !important;\n"
    "}\n"
    "[data-testid=\"stSidebar\"] input::placeholder {\n"
    "    color: #8F8B85 !important;\n"
    "}\n"
    "[data-testid=\"stSidebar\"] [data-baseweb=\"input\"] button,\n"
    "[data-testid=\"stSidebar\"] [data-baseweb=\"input\"] button svg,\n"
    "[data-testid=\"stSidebar\"] [data-baseweb=\"input\"] svg {\n"
    "    background: transparent !important;\n"
    "    fill: #8F8B85 !important;\n"
    "    stroke: #8F8B85 !important;\n"
    "    color: #8F8B85 !important;\n"
    "}\n"
    "[data-testid=\"stSidebar\"] [data-baseweb=\"input\"] button:hover svg {\n"
    "    fill: #FAFAF9 !important;\n"
    "    stroke: #FAFAF9 !important;\n"
    "    color: #FAFAF9 !important;\n"
    "}\n"
    "[data-testid=\"stSidebar\"] button[kind=\"primary\"],\n"
    "[data-testid=\"stSidebar\"] .stButton > button[kind=\"primary\"] {\n"
    "    background-color: #FAFAF9 !important;\n"
    "    color: #0F0E0D !important;\n"
    "    border: 1px solid #FAFAF9 !important;\n"
    "    border-radius: 4px !important;\n"
    "    height: 44px !important;\n"
    "    font-weight: 500 !important;\n"
    "}\n"
    "[data-testid=\"stSidebar\"] button[kind=\"primary\"]:hover,\n"
    "[data-testid=\"stSidebar\"] .stButton > button[kind=\"primary\"]:hover {\n"
    "    background-color: #CCCAC6 !important;\n"
    "    color: #0F0E0D !important;\n"
    "}\n"
    "[data-testid=\"stSidebar\"] button:not([kind=\"primary\"]),\n"
    "[data-testid=\"stSidebar\"] .stButton > button:not([kind=\"primary\"]) {\n"
    "    background-color: transparent !important;\n"
    "    color: #FAFAF9 !important;\n"
    "    border: 1px solid #33312C !important;\n"
    "    border-radius: 4px !important;\n"
    "    height: 40px !important;\n"
    "    font-weight: 500 !important;\n"
    "}\n"
    "[data-testid=\"stSidebar\"] button:not([kind=\"primary\"]):hover,\n"
    "[data-testid=\"stSidebar\"] .stButton > button:not([kind=\"primary\"]):hover {\n"
    "    background-color: #1F1D1A !important;\n"
    "    border-color: #FAFAF9 !important;\n"
    "    color: #FAFAF9 !important;\n"
    "}\n"
    "[data-testid=\"stSidebar\"] [data-testid=\"stExpander\"],\n"
    "[data-testid=\"stSidebar\"] [data-testid=\"stExpander\"] details,\n"
    "[data-testid=\"stSidebar\"] [data-testid=\"stExpander\"] summary,\n"
    "[data-testid=\"stSidebar\"] [data-testid=\"stExpanderDetails\"] {\n"
    "    background-color: #1F1D1A !important;\n"
    "    border: 1px solid #33312C !important;\n"
    "    border-radius: 4px !important;\n"
    "    color: #FAFAF9 !important;\n"
    "}\n"
    "[data-testid=\"stSidebar\"] [data-testid=\"stExpander\"] summary:hover {\n"
    "    background-color: #282522 !important;\n"
    "}\n"
    "[data-testid=\"stSidebar\"] [data-testid=\"stExpander\"] summary p,\n"
    "[data-testid=\"stSidebar\"] [data-testid=\"stExpander\"] summary span,\n"
    "[data-testid=\"stSidebar\"] [data-testid=\"stExpander\"] summary div {\n"
    "    color: #FAFAF9 !important;\n"
    "    font-weight: 500 !important;\n"
    "}\n"
    "[data-testid=\"stSidebar\"] [data-testid=\"stExpanderToggleIcon\"] svg,\n"
    "[data-testid=\"stSidebar\"] [data-testid=\"stExpander\"] summary svg {\n"
    "    fill: #FAFAF9 !important;\n"
    "    stroke: #FAFAF9 !important;\n"
    "    color: #FAFAF9 !important;\n"
    "}\n"
    "[data-testid=\"stSidebar\"] [data-testid=\"stAlert\"],\n"
    "[data-testid=\"stSidebar\"] [data-testid=\"stNotification\"] {\n"
    "    background-color: #1F1D1A !important;\n"
    "    border: 1px solid #33312C !important;\n"
    "    border-left: 3px solid #FAFAF9 !important;\n"
    "    border-radius: 4px !important;\n"
    "    color: #FAFAF9 !important;\n"
    "    padding: 10px 14px !important;\n"
    "    box-shadow: none !important;\n"
    "}\n"
    "[data-testid=\"stSidebar\"] [data-testid=\"stAlert\"] p,\n"
    "[data-testid=\"stSidebar\"] [data-testid=\"stAlert\"] span,\n"
    "[data-testid=\"stSidebar\"] [data-testid=\"stAlert\"] div {\n"
    "    color: #FAFAF9 !important;\n"
    "}\n"
    "[data-testid=\"stSidebar\"] [data-testid=\"stAlert\"] svg {\n"
    "    fill: #FAFAF9 !important;\n"
    "    stroke: #FAFAF9 !important;\n"
    "    color: #FAFAF9 !important;\n"
    "}\n"
    "[data-testid=\"stSidebar\"] svg {\n"
    "    fill: currentColor !important;\n"
    "    stroke: currentColor !important;\n"
    "    color: #FAFAF9 !important;\n"
    "}\n\n"
    "/* BaseWeb Dropdown Menus (Rendered in Portal) */\n"
    "[data-baseweb=\"popover\"],\n"
    "[data-baseweb=\"menu\"],\n"
    "ul[role=\"listbox\"] {\n"
    "    background-color: #FFFFFF !important;\n"
    "    border: 1px solid #CCCAC6 !important;\n"
    "    border-radius: 4px !important;\n"
    "    box-shadow: none !important;\n"
    "}\n"
    "[data-baseweb=\"popover\"] li,\n"
    "[data-baseweb=\"popover\"] [role=\"option\"] {\n"
    "    background-color: #FFFFFF !important;\n"
    "    color: #0F0E0D !important;\n"
    "    font-size: 14px !important;\n"
    "    font-weight: 400 !important;\n"
    "}\n"
    "[data-baseweb=\"popover\"] li:hover,\n"
    "[data-baseweb=\"popover\"] [role=\"option\"]:hover,\n"
    "[data-baseweb=\"popover\"] [aria-selected=\"true\"] {\n"
    "    background-color: #F2F1F0 !important;\n"
    "    color: #0F0E0D !important;\n"
    "    font-weight: 500 !important;\n"
    "}\n\n"
    "/* Chat Message Styling */\n"
    "[data-testid=\"stChatMessage\"] {\n"
    "    padding: 12px 16px;\n"
    "    border-radius: 4px;\n"
    "    margin-bottom: 10px;\n"
    "    background-color: #FFFFFF;\n"
    "    border: 1px solid #CCCAC6;\n"
    "    box-shadow: none !important;\n"
    "}\n\n"
    "/* Containers with Border */\n"
    "[data-testid=\"stVerticalBlockBorderWrapper\"] {\n"
    "    border-radius: 4px !important;\n"
    "    border-color: #CCCAC6 !important;\n"
    "    background-color: #FFFFFF !important;\n"
    "    box-shadow: none !important;\n"
    "}\n\n"
    "/* Custom Scrollbars */\n"
    "::-webkit-scrollbar {\n"
    "    width: 6px;\n"
    "    height: 6px;\n"
    "}\n"
    "::-webkit-scrollbar-track {\n"
    "    background: transparent;\n"
    "}\n"
    "::-webkit-scrollbar-thumb {\n"
    "    background: #CCCAC6;\n"
    "    border-radius: 3px;\n"
    "}\n"
    "::-webkit-scrollbar-thumb:hover {\n"
    "    background: #ADABA5;\n"
    "}\n"
    "</style>\n"
)


# ==============================================================================
# Helper Functions: Provenance Highlighting & Model Switching
# ==============================================================================
def format_citation_telemetry_banner(verified_count: int, flagged_count: int) -> str:
    """Format Citation Telemetry banner with high contrast colors.

    Args:
        verified_count: Number of verified statutory citations.
        flagged_count: Number of ungrounded or hallucinated citations.

    Returns:
        HTML string with high-contrast emerald or crimson styling.
    """
    if flagged_count == 0:
        b_style = (
            "display: flex; align-items: center; gap: 8px; padding: 10px 14px; "
            "background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; border-radius: 4px; "
            "color: #0F0E0D; font-size: 14px; font-weight: 500; margin-bottom: 16px;"
        )
        return (
            f"<div style='{b_style}'>\n"
            "  <span><strong>Citation Telemetry:</strong> "
            "<strong style='color: #10b981; font-weight: 500;'>"
            f"{verified_count} verified</strong>, "
            "<span style='color: #34d399;'>0 ungrounded citations</span>.</span>\n"
            "</div>"
        )
    b_style = (
        "display: flex; align-items: center; gap: 8px; padding: 10px 14px; "
        "background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; border-radius: 4px; "
        "color: #0F0E0D; font-size: 14px; font-weight: 500; margin-bottom: 16px;"
    )
    return (
        f"<div style='{b_style}'>\n"
        "  <span><strong>Citation Telemetry:</strong> "
        f"<span>{verified_count} verified</span>, "
        f"<strong style='color: #ef4444; font-weight: 500;'>{flagged_count} ungrounded citations"
        "</strong><span style='color: #f87171;'> (warning)</span>.</span>\n"
        "</div>"
    )


def format_ui_provenance_with_marks(
    chunks: Sequence[RetrievedChunk],
    cited_sections: Sequence[str] | None = None,
    highlight_terms: Sequence[str] | None = None,
) -> str:
    """Format interactive HTML statutory cards with visual <mark> highlighting.

    Args:
        chunks: List of retrieved statutory chunks with RRF scores.
        cited_sections: Optional list of sections specifically cited in generated response.
        highlight_terms: Optional list of legal keywords to highlight in chunk text.

    Returns:
        Safe HTML string containing styled collapsible statutory cards with
        yellow/amber <mark> visual highlighting.
    """
    if not chunks:
        return (
            "<div style='padding: 14px 16px; color: #706D66; font-style: italic; "
            "background-color: #F2F1F0; border-radius: 4px; border: 1px solid #CCCAC6; "
            "font-size: 14px;'>No statutory grounds retrieved. "
            "Enter case facts in Tab 1 to retrieve provisions.</div>"
        )

    cards: list[str] = [
        "<div class='legal-provenance-container' "
        "style='font-family: Inter, -apple-system, sans-serif;'>"
    ]

    all_terms: set[str] = {t.strip() for t in (highlight_terms or []) if t and t.strip()}
    all_terms.update(CORE_HIGHLIGHT_TERMS)
    sorted_terms = sorted(all_terms, key=len, reverse=True)

    combined_pattern: re.Pattern[str] | None = None
    if sorted_terms:
        term_patterns: list[str] = []
        for term in sorted_terms:
            escaped = re.escape(term)
            prefix = r"\b" if re.match(r"^\w", term) else r"(?<!\w)"
            suffix = r"\b" if re.search(r"\w$", term) else r"(?!\w)"
            term_patterns.append(f"{prefix}{escaped}{suffix}")
        combined_pattern = re.compile(f"({'|'.join(term_patterns)})", re.IGNORECASE)

    mark_replacement = (
        r"<mark style='background-color: #F6F202; color: #0F0E0D; font-weight: 500; "
        r"padding: 1px 4px; border-radius: 3px; --mark-amber: #fde68a; --mark-fg: #78350f;'>"
        r"\1</mark>"
    )

    first_cited_opened = False
    any_cited = False
    if cited_sections:
        for chunk in chunks:
            for cs in cited_sections:
                if (
                    cs
                    and chunk.section
                    and (cs.lower() in chunk.section.lower() or chunk.section.lower() in cs.lower())
                ):
                    any_cited = True
                    break
            if any_cited:
                break

    for idx, chunk in enumerate(chunks):
        is_cited = False
        if cited_sections:
            for cs in cited_sections:
                if (
                    cs
                    and chunk.section
                    and (cs.lower() in chunk.section.lower() or chunk.section.lower() in cs.lower())
                ):
                    is_cited = True
                    break

        is_open = False
        if any_cited:
            if is_cited and not first_cited_opened:
                is_open = True
                first_cited_opened = True
        else:
            if idx == 0:
                is_open = True

        open_attr = " open" if is_open else ""
        border_left = "3px solid #0F0E0D" if is_cited else "1px solid #CCCAC6"
        badge_style = (
            "background-color: #0F0E0D; color: #FAFAF9; padding: 2px 8px; "
            "border-radius: 3px; font-size: 11px; font-weight: 500; letter-spacing: 0.02em; "
            "margin-left: 8px;"
        )
        cited_badge = (
            f"<span style='{badge_style}'>CITED IN ADVICE</span>"
            if is_cited
            else ""
        )

        safe_content = html.escape(chunk.content)
        if combined_pattern is not None:
            safe_content = combined_pattern.sub(mark_replacement, safe_content)

        sec_style = (
            "background-color: #F2F1F0; color: #0F0E0D; border: 1px solid #CCCAC6; "
            "border-radius: 3px; padding: 2px 7px; font-size: 13px; font-weight: 500; "
            "margin-right: 6px;"
        )
        rrf_style = (
            "background-color: #F2F1F0; color: #706D66; border: 1px solid #CCCAC6; "
            "padding: 2px 8px; border-radius: 3px; font-size: 12px; font-weight: 500; "
            "white-space: nowrap;"
        )
        body_style = (
            "margin-top: 10px; padding: 14px 16px; background-color: #FAFAF9; "
            "border-top: 1px solid #CCCAC6; font-size: 15px; line-height: 1.5; color: #0F0E0D; "
            "white-space: pre-wrap;"
        )

        card_html = (
            f"<details class='statutory-provenance-card'{open_attr} style='margin-bottom: 12px; "
            f"border-top: 1px solid #CCCAC6; border-bottom: 1px solid #CCCAC6; "
            f"border-left: {border_left}; border-right: 1px solid #CCCAC6; border-radius: 4px; "
            f"background-color: #FFFFFF; padding: 12px 16px; box-shadow: none;'>\n"
            f"<summary style='cursor: pointer; font-weight: 500; color: #0F0E0D; "
            f"display: flex; justify-content: space-between; align-items: center; "
            f"list-style: none;'>\n"
            f"<span>\n"
            f"<strong style='color: #706D66; font-weight: 500; margin-right: 4px;'>"
            f"#{chunk.rank}:</strong>\n"
            f"<span style='{sec_style}'>"
            f"[{html.escape(chunk.statute)} | Sec {html.escape(chunk.section)}]</span>\n"
            f"<span style='color: #0F0E0D; font-weight: 500;'>{html.escape(chunk.title)}</span>"
            f"{cited_badge}\n"
            f"</span>\n"
            f"<span style='{rrf_style}'>RRF: {chunk.score:.4f}</span>\n"
            f"</summary>\n"
            f"<div style='{body_style}'>\n"
            f"{safe_content}\n"
            f"</div>\n"
            f"</details>"
        )
        cards.append(card_html)

    cards.append("</div>")
    return "\n".join(cards)


def render_editorial_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    """Render a responsive, text-wrapping HTML table following Harvey design tokens.

    Args:
        headers: Column header strings.
        rows: Rows of string values.

    Returns:
        Responsive HTML string for Streamlit markdown rendering.
    """
    if not rows:
        return (
            "<p style='color: #706D66; font-size: 14px; font-style: italic; "
            "padding: 12px 0; border-top: 1px solid #CCCAC6;'>No records available.</p>"
        )

    th_style = (
        "text-align: left; padding: 10px 12px; font-size: 14px; font-weight: 500; "
        "color: #706D66; border-bottom: 1px solid #CCCAC6; background-color: transparent;"
    )
    th_cells = "".join(f"<th style='{th_style}'>{html.escape(str(h))}</th>" for h in headers)

    td_style = (
        "padding: 12px; font-size: 15px; font-weight: 400; line-height: 1.45; "
        "color: #0F0E0D; border-bottom: 1px solid #CCCAC6; vertical-align: top; "
        "white-space: normal; word-break: break-word;"
    )
    tr_rows: list[str] = []
    for row in rows:
        td_cells = "".join(
            f"<td style='{td_style}'>{html.escape(str(cell))}</td>" for cell in row
        )
        tr_rows.append(f"<tr>{td_cells}</tr>")

    tbody_html = "\n".join(tr_rows)
    tbl_style = (
        "width: 100%; border-collapse: collapse; border-top: 2px solid #0F0E0D; "
        "border-bottom: 1px solid #CCCAC6;"
    )
    return (
        "<div style='width: 100%; overflow-x: auto; margin-bottom: 24px;'>\n"
        f"<table style='{tbl_style}'>\n"
        f"<thead><tr>{th_cells}</tr></thead>\n"
        f"<tbody>\n{tbody_html}\n</tbody>\n"
        "</table>\n"
        "</div>"
    )


def apply_runtime_provider(
    provider: str,
    model_name: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    settings: Settings | None = None,
    router: LLMRouter | None = None,
) -> str:
    """Switch or update active LLM provider configuration at runtime.

    Args:
        provider: Target provider name ('groq', 'ollama', 'openai', 'gemini').
        model_name: Optional model identifier override.
        api_key: Optional API key override.
        base_url: Optional base URL for Ollama.
        settings: Application Settings instance. Defaults to get_settings().
        router: Active LLMRouter instance whose client cache to invalidate.

    Returns:
        Status message confirming the provider switch.
    """
    cfg = settings or get_settings()
    clean_provider = provider.lower().strip()
    if clean_provider == "ollama":
        cfg.llm_provider = "ollama"
    elif clean_provider == "openai":
        cfg.llm_provider = "openai"
    elif clean_provider == "gemini":
        cfg.llm_provider = "gemini"
    else:
        cfg.llm_provider = "groq"

    if model_name:
        clean_model = model_name.strip()
        setattr(cfg, f"{clean_provider}_model", clean_model)
        cfg.default_model_name = clean_model
    else:
        provider_model = getattr(cfg, f"{clean_provider}_model", None)
        if provider_model and isinstance(provider_model, str):
            cfg.default_model_name = provider_model

    if api_key:
        setattr(cfg, f"{clean_provider}_api_key", SecretStr(api_key.strip()))
    if base_url and clean_provider == "ollama":
        cfg.ollama_base_url = base_url.strip()

    if router is not None:
        router._clients.pop(clean_provider, None)

    active_model = cfg.get_active_model(clean_provider)
    return f"Active provider successfully switched to: {clean_provider} (Model: {active_model})"


def ping_provider(
    provider: str,
    router: LLMRouter,
) -> str:
    """Execute health check ping against active provider.

    Args:
        provider: Provider identifier to test.
        router: Configured LLMRouter instance.

    Returns:
        Status message with latency measurement or error diagnosis.
    """
    start_time = time.perf_counter()
    try:
        response = router.generate(
            prompt="Ping test. Respond with 'PONG'.",
            provider=provider,
            system_prompt="You are a ping test assistant.",
        )
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        return (
            f"✅ Provider '{provider}' operational! Model: '{response.model}' | "
            f"Latency: {latency_ms:.1f}ms"
        )
    except (LLMConnectionError, LLMAuthenticationError, LLMRateLimitError) as exc:
        return f"❌ Connection failed for provider '{provider}': {exc}"
    except Exception as exc:
        return f"❌ Unexpected error connecting to '{provider}': {exc}"


# ==============================================================================
# Workflow Callback Handlers
# ==============================================================================
def handle_case_intake(
    narrative: str,
    router: LLMRouter | None = None,
    scope_checker: ScopeChecker | None = None,
    complainant_name: str = "",
    complainant_email: str = "",
    complainant_phone: str = "",
    complainant_city: str = "",
    complainant_state: str = "",
) -> tuple[CaseFile | None, str, list[list[str]], list[list[str]], list[list[str]]]:
    """Process unstructured narrative into structured CaseFile and audit evidence.

    Args:
        narrative: Verbatim consumer narrative input.
        router: Optional active LLMRouter instance.
        scope_checker: Optional pre-retrieval scope checker instance.
        complainant_name: Optional complainant full name.
        complainant_email: Optional complainant email address.
        complainant_phone: Optional complainant phone number.
        complainant_city: Optional complainant city.
        complainant_state: Optional complainant state.

    Returns:
        Tuple containing:
            - Populated CaseFile or None if invalid/out-of-scope.
            - Alert or status message banner.
            - Timeline table data (date, significance, description).
            - Available evidence table data (type, description, status).
            - Missing evidence table data (type, reason, how_to_procure).
    """
    if not narrative or not narrative.strip():
        return None, "Please enter your dispute facts in the text area above.", [], [], []

    effective_router = router or LLMRouter()
    effective_scope_checker = scope_checker or ScopeChecker()

    # Pre-retrieval scope validation check
    scope_result = effective_scope_checker.check_scope(narrative)
    if not scope_result.is_in_scope:
        reason = scope_result.out_of_scope_category or "Non-consumer dispute"
        action = scope_result.escalation_advice or "Consult a registered Advocate."
        alert = (
            f"⚠️ Escalation Required: Dispute is out of consumer forum scope "
            f"({reason}). Suggested Action: {action}. "
            "Please consult an Advocate registered with the Bar Council of India."
        )
        return None, alert, [], [], []

    complainant: PartyDetails | None = None
    if complainant_name or complainant_email or complainant_phone:
        complainant = PartyDetails(
            name=complainant_name.strip() or "Consumer Complainant",
            email=complainant_email.strip() or None,
            phone=complainant_phone.strip() or None,
            city=complainant_city.strip() or "Unknown City",
            state=complainant_state.strip() or "Unknown State",
        )

    builder = CaseBuilder(llm_router=effective_router, scope_checker=effective_scope_checker)
    try:
        case_file = builder.build_case(
            narrative=narrative,
            complainant_details=complainant,
            use_llm=True,
        )
    except OutOfScopeDisputeError as err:
        err_reason = (
            err.scope_result.out_of_scope_category
            if (err.scope_result and err.scope_result.out_of_scope_category)
            else str(err)
        )
        err_action = (
            err.scope_result.escalation_advice
            if (err.scope_result and err.scope_result.escalation_advice)
            else "Consult a registered Advocate."
        )
        alert = f"⚠️ Escalation Required: {err_reason}. Suggested Action: {err_action}"
        return None, alert, [], [], []
    except Exception as exc:
        logger.warning("LLM case building encountered error: %s. Using heuristic intake.", exc)
        case_file = builder.build_case(
            narrative=narrative,
            complainant_details=complainant,
            use_llm=False,
        )

    timeline_data = [[e.date, e.significance, e.description] for e in case_file.timeline]
    evidence_avail = [
        [
            item.item_name,
            item.description,
            "Available" if item.is_available else "Pending",
        ]
        for item in case_file.evidence_checklist
    ]

    missing_items = builder.audit_missing_evidence(case_file)
    missing_ev = [[m.item_name, m.why_needed, m.where_to_obtain] for m in missing_items]

    in_scope_banner = "Dispute is within Consumer Forum jurisdiction."
    return (
        case_file,
        in_scope_banner,
        timeline_data,
        evidence_avail,
        missing_ev,
    )


def handle_evaluate_standing(
    case_file: CaseFile | None,
    router: LLMRouter,
    retriever: StatutoryHybridRetriever,
) -> tuple[LegalStanding | None, str, list[list[str]], list[list[str]], str]:
    """Analyze consumer legal standing, statutory breaches, and retrieval provenance.

    Args:
        case_file: Structured CaseFile from Tab 1.
        router: Active LLMRouter instance.
        retriever: StatutoryHybridRetriever instance.

    Returns:
        Tuple containing:
            - Computed LegalStanding instance.
            - Overview markdown summary.
            - Statutory violations table rows.
            - 4-Step resolution pathway table rows.
            - HTML provenance string with visual <mark> tags.
    """
    if case_file is None:
        empty_msg = "Please complete Case Intake in Tab 1 first to establish facts before analysis."
        return (
            None,
            empty_msg,
            [],
            [],
            "<div style='color: #757575; font-style: italic;'>No case facts available.</div>",
        )

    advisor = LegalAdvisor(llm_router=router, retriever=retriever)
    standing = advisor.analyze_standing(case_file=case_file, use_llm=True)
    pathway = advisor.build_resolution_pathway(
        case_file=case_file,
        forum_name=standing.pecuniary_commission_forum,
        court_fee=int(standing.estimated_costs.court_fees_inr),
    )

    c_status = "Eligible Consumer" if standing.is_consumer else "Ineligible"
    lim_status = standing.limitation_status.replace("_", " ").title()
    fee_val = standing.estimated_costs.court_fees_inr
    overview_md = (
        "### Legal Standing Assessment\n"
        f"- **Consumer Standing:** {c_status} (Under CPA 2019 Section 2(7))\n"
        f"- **Pecuniary Jurisdiction:** {standing.pecuniary_commission_forum}\n"
        f"- **Limitation Status:** {lim_status} (Section 69 CPA 2019)\n"
        f"- **Estimated Filing Fee:** ₹{fee_val:,.0f}\n\n"
        f"{standing.consumer_rationale}"
    )

    violations_df = [
        [
            v.statute,
            v.section_or_rule,
            v.violation_nature.replace("_", " ").title(),
            v.explanation,
        ]
        for v in standing.statutory_violations
    ]

    pathway_df = [
        [
            str(p.step_number),
            p.forum_or_action,
            p.action_owner,
            p.expected_duration,
            f"₹{p.cost_inr:.0f}",
        ]
        for p in pathway
    ]

    # Retrieve statutory provenance chunks for visual display
    query_text = f"{case_file.title} {case_file.facts_summary}"
    chunks, _ = retriever.retrieve_with_confidence(query_text, top_k=5)
    cited_sections = [v.section_or_rule for v in standing.statutory_violations]
    provenance_html = format_ui_provenance_with_marks(chunks, cited_sections=cited_sections)

    return standing, overview_md, violations_df, pathway_df, provenance_html


def handle_draft_single(
    case_file: CaseFile | None,
    standing: LegalStanding | None,
    doc_type: str,
    notice_days: int = 15,
    router: LLMRouter | None = None,
    retriever: StatutoryHybridRetriever | None = None,
    export_dir: Path | None = None,
) -> tuple[DraftedDocument | None, str, str, str]:
    """Generate a requested legal artifact, save to disk, and prepare download.

    Args:
        case_file: Structured CaseFile from Tab 1.
        standing: LegalStanding from Tab 2.
        doc_type: Requested document type ('legal_notice', 'grievance_email', 'edaakhil').
        notice_days: Notice period deadline in days (default: 15).
        router: Active LLMRouter instance.
        retriever: StatutoryHybridRetriever instance.
        export_dir: Optional filesystem directory for exporting files.

    Returns:
        Tuple containing:
            - Instantiated DraftedDocument or None if input missing.
            - Markdown formatted document text.
            - Plain text formatted document.
            - Absolute filesystem path to generated file for download.
    """
    if case_file is None:
        return None, "Please complete Case Intake in Tab 1 first.", "", ""

    effective_router = router or LLMRouter()
    drafter = DocumentDrafter(llm_router=effective_router, retriever=retriever)
    clean_type = doc_type.lower().strip()

    doc: DraftedDocument
    if "notice" in clean_type:
        doc = drafter.draft_legal_notice(
            case_file=case_file,
            standing=standing,
            notice_period_days=notice_days,
            use_llm=True,
        )
    elif "grievance" in clean_type or "email" in clean_type:
        doc = drafter.draft_grievance_email(
            case_file=case_file,
            standing=standing,
            use_llm=True,
        )
    else:
        doc = drafter.draft_edaakhil_complaint(
            case_file=case_file,
            standing=standing,
            use_llm=True,
        )

    md_text = doc.body_markdown
    plain_text = doc.body_markdown

    target_dir = export_dir or Path("data/exports")
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{case_file.case_id}_{doc.document_type}.md"
    file_path = target_dir / filename
    file_path.write_text(md_text, encoding="utf-8")

    return doc, md_text, plain_text, str(file_path.resolve())


def handle_simulator_turn(
    user_argument: str,
    state: SimulatorState | None,
    router: LLMRouter,
    tactic: str = "auto",
    opponent_name: str = "Corporate Defense Counsel",
    opponent_entity: str = "Merchant / Platform Legal Team",
) -> tuple[SimulatorState, list[dict[str, str]], str, str, str, str]:
    """Advance Opposing Counsel practice session by evaluating user's rebuttal.

    Args:
        user_argument: Verbatim consumer rebuttal argument.
        state: Current SimulatorState. If None, initiates new session.
        router: Active LLMRouter instance.
        tactic: Defense tactic identifier or 'auto'.
        opponent_name: Display name for corporate opposing counsel.
        opponent_entity: Corporate entity represented.

    Returns:
        Tuple containing:
            - Updated SimulatorState.
            - Chatbot transcript list of message dicts with role and content.
            - Score display string.
            - Strengths markdown.
            - Weaknesses markdown.
            - Tactical advice markdown.
    """
    simulator = OpposingCounselSimulator(router=router)

    current_state = state
    if current_state is None or not current_state.turns:
        dummy_case = CaseFile(
            case_id="sim_practice_001",
            title="Consumer Product Dispute",
            disputed_amount_inr=25000.0,
            transaction_date="2026-01-01",
            facts_summary=user_argument or "Consumer dispute regarding refund denial.",
            opposite_parties=[
                OppositeParty(
                    name="Corporate Merchant",
                    role="Seller",
                )
            ],
            timeline=[
                TimelineEvent(
                    date="2026-01-01",
                    description="Order placed and delivered defective.",
                    significance="Dispute origin",
                )
            ],
            complainant=PartyDetails(name="Consumer", city="Delhi", state="Delhi"),
        )
        current_state = simulator.start_simulation(
            case=dummy_case,
            opponent_name=opponent_name,
            opponent_entity=opponent_entity,
        )

    updated_state = simulator.step_simulation(
        state=current_state,
        consumer_response=user_argument,
        use_llm=False,
    )

    # Build chat transcript messages
    chat_history: list[dict[str, str]] = []
    for turn in updated_state.turns:
        role = "assistant" if turn.speaker == "opposing_counsel" else "user"
        chat_history.append({"role": role, "content": turn.content})

    # Extract feedback from latest consumer turn
    latest_feedback = None
    for turn in reversed(updated_state.turns):
        if turn.speaker == "consumer" and turn.feedback is not None:
            latest_feedback = turn.feedback
            break

    if latest_feedback:
        score_text = (
            f"Turn Score: {latest_feedback.score:.1f}/100 | "
            f"Readiness Score: {updated_state.cumulative_score:.1f}/100"
        )
        strengths_md = (
            "\n".join(f"- {s}" for s in latest_feedback.strengths)
            if latest_feedback.strengths
            else "No prominent statutory strengths identified."
        )
        weaknesses_md = (
            "\n".join(f"- {w}" for w in latest_feedback.weaknesses)
            if latest_feedback.weaknesses
            else "No notable vulnerabilities detected."
        )
        cited_str = ", ".join(latest_feedback.statutory_sections_cited) or "None"
        missing_str = ", ".join(latest_feedback.missing_statutory_sections) or "None"
        flaws_formatted = "\n".join(
            f"- {flaw}" for flaw in latest_feedback.flaws_in_merchant_defense
        )
        advice_md = (
            f"**Statutory Sections Correctly Cited:** {cited_str}\n\n"
            f"**Essential Sections Missing:** {missing_str}\n\n"
            f"**Coach's Tactical Tip:**\n{latest_feedback.coaching_tip}\n\n"
            f"**Opponent Defense Flaws to Exploit:**\n{flaws_formatted}"
        )
    else:
        score_text = "Score: N/A"
        strengths_md = "Submit your argument to receive coach feedback."
        weaknesses_md = "Submit your argument to identify gaps."
        advice_md = "Practice articulating your statutory claims."

    return updated_state, chat_history, score_text, strengths_md, weaknesses_md, advice_md


# ==============================================================================
# Streamlit Cached Resources & UI Application Entrypoint
# ==============================================================================
@st.cache_resource
def get_cached_retriever() -> StatutoryHybridRetriever:
    """Instantiate and cache statutory hybrid retriever across reruns.

    Returns:
        StatutoryHybridRetriever indexed with statutory corpus chunks.
    """
    corpus_dir = Path("data/statutes")
    stat_chunks: list[RetrievedChunk] = []
    if corpus_dir.exists():
        chunker = StatutoryChunker()
        for f in sorted(corpus_dir.glob("*.txt")):
            parsed = chunker.split_text(f.read_text(encoding="utf-8"))
            for sc in parsed:
                stat_chunks.append(
                    RetrievedChunk(
                        chunk_id=sc.metadata.chunk_id,
                        content=sc.content,
                        statute=sc.metadata.statute,
                        chapter=sc.metadata.chapter,
                        section=sc.metadata.section,
                        title=sc.metadata.section_title,
                        score=0.025,
                        rank=len(stat_chunks) + 1,
                    )
                )
    return StatutoryHybridRetriever(
        chunks=stat_chunks,
        dense_retriever=InMemoryDenseRetriever(),
    )


def render_streamlit_app(
    settings: Settings | None = None,
    router: LLMRouter | None = None,
    retriever: StatutoryHybridRetriever | None = None,
    scope_checker: ScopeChecker | None = None,
) -> None:
    """Render the primary Legal Saathi Streamlit Web Interface.

    Args:
        settings: Optional application Settings override.
        router: Optional LLMRouter instance override.
        retriever: Optional StatutoryHybridRetriever instance override.
        scope_checker: Optional ScopeChecker instance override.
    """
    with contextlib.suppress(Exception):
        st.set_page_config(
            page_title="Legal Saathi — AI Consumer Lawyer",
            page_icon="⚖️",
            layout="wide",
            initial_sidebar_state="expanded",
        )

    st.markdown(LEGAL_SAATHI_CUSTOM_CSS, unsafe_allow_html=True)

    if "settings" not in st.session_state:
        st.session_state["settings"] = settings or get_settings()
    app_settings = cast(Settings, st.session_state["settings"])

    if "router" not in st.session_state:
        st.session_state["router"] = router or LLMRouter(settings=app_settings)
    active_router = cast(LLMRouter, st.session_state["router"])

    if "retriever" not in st.session_state:
        st.session_state["retriever"] = retriever or get_cached_retriever()
    active_retriever = cast(StatutoryHybridRetriever, st.session_state["retriever"])

    if "scope_checker" not in st.session_state:
        st.session_state["scope_checker"] = scope_checker or ScopeChecker()
    active_scope_checker = cast(ScopeChecker, st.session_state["scope_checker"])

    # Session State Initialization
    if "case_file" not in st.session_state:
        st.session_state["case_file"] = None
    if "standing" not in st.session_state:
        st.session_state["standing"] = None
    if "sim_state" not in st.session_state:
        st.session_state["sim_state"] = None
    if "drafted_doc" not in st.session_state:
        st.session_state["drafted_doc"] = None
    if "draft_raw_text" not in st.session_state:
        st.session_state["draft_raw_text"] = ""
    if "active_provider" not in st.session_state:
        st.session_state["active_provider"] = app_settings.llm_provider
    if "ta_case_narrative" not in st.session_state:
        st.session_state["ta_case_narrative"] = ""
    if "ta_raw_markdown_editor" not in st.session_state:
        st.session_state["ta_raw_markdown_editor"] = ""
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "sim_scores" not in st.session_state:
        st.session_state["sim_scores"] = {
            "turn_score": 0.0,
            "cumulative_score": 0.0,
            "strengths": "Submit your argument to receive coach feedback.",
            "weaknesses": "Submit your argument to identify gaps.",
            "advice": "Practice articulating your statutory claims.",
        }

    # --------------------------------------------------------------------------
    # PERSISTENT SIDEBAR: Live Model Switcher & Telemetry
    # --------------------------------------------------------------------------
    cur_provider = str(st.session_state.get("active_provider", app_settings.llm_provider))
    cur_model = app_settings.get_active_model(cur_provider)

    st.sidebar.markdown(
        f"<div style='background-color: #1F1D1A; border: 1px solid #33312C; border-radius: 4px; "
        f"padding: 14px 16px; margin-bottom: 16px;'>\n"
        f"<div style='font-size: 12px; font-weight: 500; color: #8F8B85; letter-spacing: 0.05em; "
        f"text-transform: uppercase;'>Current Provider</div>\n"
        f"<div style='font-size: 15px; font-weight: 500; color: #FAFAF9; margin-bottom: 8px;'>"
        f"{cur_provider}</div>\n"
        f"<div style='font-size: 12px; font-weight: 500; color: #8F8B85; letter-spacing: 0.05em; "
        f"text-transform: uppercase;'>Active Model</div>\n"
        f"<div style='font-size: 15px; font-weight: 500; color: #FAFAF9;'>{cur_model}</div>\n"
        f"</div>",
        unsafe_allow_html=True,
    )

    provider_options = ["groq", "ollama", "openai", "gemini"]
    p_idx = provider_options.index(cur_provider) if cur_provider in provider_options else 0
    selected_provider = st.sidebar.selectbox(
        "Active LLM Provider",
        options=provider_options,
        index=p_idx,
        key="sb_provider_select",
    )

    with st.sidebar.expander("Provider API & Model Config", expanded=True):
        st.markdown("##### Groq Cloud")
        groq_choices = [
            "openai/gpt-oss-20b",
            "openai/gpt-oss-120b",
            "qwen/qwen3.8-27b",
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
        ]
        g_idx = (
            groq_choices.index(app_settings.groq_model)
            if app_settings.groq_model in groq_choices
            else 3
        )
        sb_groq_model = st.selectbox(
            "Groq Model",
            options=groq_choices,
            index=g_idx,
            key="sb_groq_model",
        )
        g_key_val = (
            app_settings.groq_api_key.get_secret_value() if app_settings.groq_api_key else ""
        )
        sb_groq_key = st.text_input(
            "Groq API Key",
            value=g_key_val,
            type="password",
            placeholder="gsk_...",
            key="sb_groq_key",
        )

        st.markdown("##### Local Ollama")
        sb_ollama_model = st.text_input(
            "Ollama Model (<= 8B params)",
            value=app_settings.ollama_model,
            key="sb_ollama_model",
        )
        sb_ollama_url = st.text_input(
            "Ollama Base URL",
            value=app_settings.ollama_base_url,
            key="sb_ollama_url",
        )

        st.markdown("##### OpenAI")
        sb_openai_model = st.text_input(
            "OpenAI Model",
            value=app_settings.openai_model,
            key="sb_openai_model",
        )
        oa_key_val = (
            app_settings.openai_api_key.get_secret_value() if app_settings.openai_api_key else ""
        )
        sb_openai_key = st.text_input(
            "OpenAI API Key",
            value=oa_key_val,
            type="password",
            placeholder="sk-...",
            key="sb_openai_key",
        )

        st.markdown("##### Google Gemini")
        sb_gemini_model = st.text_input(
            "Gemini Model",
            value=app_settings.gemini_model,
            key="sb_gemini_model",
        )
        gem_key_val = (
            app_settings.gemini_api_key.get_secret_value() if app_settings.gemini_api_key else ""
        )
        sb_gemini_key = st.text_input(
            "Gemini API Key",
            value=gem_key_val,
            type="password",
            placeholder="AIza...",
            key="sb_gemini_key",
        )

    if st.sidebar.button(
        "Apply Settings", key="sb_btn_apply", use_container_width=True, type="primary"
    ):
        model_overrides: dict[str, str] = {
            "groq": sb_groq_model,
            "ollama": sb_ollama_model,
            "openai": sb_openai_model,
            "gemini": sb_gemini_model,
        }
        chosen_model = model_overrides.get(selected_provider)
        key_overrides: dict[str, str] = {
            "groq": sb_groq_key,
            "openai": sb_openai_key,
            "gemini": sb_gemini_key,
        }
        chosen_key = key_overrides.get(selected_provider)
        chosen_url = sb_ollama_url if selected_provider == "ollama" else None

        msg = apply_runtime_provider(
            provider=selected_provider,
            model_name=chosen_model,
            api_key=chosen_key,
            base_url=chosen_url,
            settings=app_settings,
            router=active_router,
        )
        st.session_state["active_provider"] = selected_provider
        st.toast(f"Settings Applied: {msg}")
        st.sidebar.success(f"Configured: {selected_provider}")

    if st.sidebar.button("Ping Provider", key="sb_btn_ping", use_container_width=True):
        ping_res = ping_provider(provider=selected_provider, router=active_router)
        if "✅" in ping_res:
            st.sidebar.success(ping_res)
        else:
            st.sidebar.error(ping_res)

    st.sidebar.markdown(
        "<div style='border-top: 1px solid #33312C; padding-top: 16px; margin-top: 16px; "
        "color: #8F8B85; font-size: 14px; line-height: 1.4;'>\n"
        "<strong style='color: #FAFAF9;'>Statutory Disclaimer:</strong> This tool provides "
        "automated legal information and self-help document drafts under CPA 2019. It does "
        "not constitute formal legal representation. Disputes involving criminal offenses "
        "(BNS), Section 138 NI Act cheque bounce, or corporate B2B disputes require a "
        "registered Advocate.\n"
        "</div>",
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------------------------
    # MAIN APP HEADER & 4 CORE WORKFLOW TABS
    # --------------------------------------------------------------------------
    st.title("Legal Saathi — AI Consumer Lawyer")
    st.caption(
        "Statutory Consumer Dispute Resolution Platform under the Consumer Protection Act, 2019 "
        "& Consumer Protection (E-Commerce) Rules, 2020."
    )
    st.markdown(
        "<hr style='border: none; border-top: 1px solid #CCCAC6; margin: 16px 0 24px 0;' />",
        unsafe_allow_html=True,
    )

    tab_intake, tab_standing, tab_drafter, tab_simulator = st.tabs(
        [
            "1. Case Intake & Facts",
            "2. Legal Standing & Provenance",
            "3. Document Drafter",
            "4. Opposing Counsel Simulator",
        ]
    )

    # ==========================================================================
    # TAB 1: Case Intake & Facts
    # ==========================================================================
    with tab_intake:
        col_in_left, col_in_right = st.columns([1.2, 1])

        sample_narrative = (
            "I ordered a high-end smartphone for ₹65,000 on 2026-01-15 from an online e-commerce "
            "marketplace (Order ID: INV-2026-8812). It was delivered on 2026-01-18 with a "
            "shattered OLED screen and swollen battery. I contacted support within 24 hours "
            "attaching unboxing photos. Customer support rejected the refund/replacement "
            "citing their 'No Return on Electronics' policy and redirected me to manufacturer. "
            "The manufacturer stated physical transit damage voided the warranty."
        )

        with col_in_left:
            if st.button("Load Sample Dispute", key="btn_load_sample"):
                st.session_state["ta_case_narrative"] = sample_narrative

            narrative_text = st.text_area(
                "Consumer Dispute Narrative (English, Hindi, or Hinglish)",
                height=180,
                placeholder="Describe your purchase, defect/deficiency, merchant responses...",
                key="ta_case_narrative",
            )

            with st.expander("Complainant Contact Details (Optional)", expanded=False):
                cc1, cc2 = st.columns(2)
                c_name = cc1.text_input("Complainant Name", value="Rahul Sharma", key="c_name_in")
                c_email = cc2.text_input(
                    "Email Address", value="rahul.sharma@example.com", key="c_email_in"
                )
                c_phone = cc1.text_input(
                    "Phone Number", value="+91-9876543210", key="c_phone_in"
                )
                c_city = cc2.text_input("City", value="New Delhi", key="c_city_in")
                c_state = cc1.text_input("State", value="Delhi", key="c_state_in")

            analyze_clicked = st.button(
                "Analyze Facts & Build Case",
                type="primary",
                key="btn_analyze_case",
            )

        if analyze_clicked:
            st.session_state["narrative_input"] = narrative_text
            c_file, alert_msg, timeline, avail, missing = handle_case_intake(
                narrative=narrative_text,
                router=active_router,
                scope_checker=active_scope_checker,
                complainant_name=c_name,
                complainant_email=c_email,
                complainant_phone=c_phone,
                complainant_city=c_city,
                complainant_state=c_state,
            )
            st.session_state["case_file"] = c_file
            st.session_state["intake_alert"] = alert_msg
            st.session_state["intake_timeline"] = timeline
            st.session_state["intake_avail"] = avail
            st.session_state["intake_missing"] = missing

        case_file_obj = cast(CaseFile | None, st.session_state.get("case_file"))
        intake_alert_str = str(st.session_state.get("intake_alert", ""))

        with col_in_right:
            if intake_alert_str:
                if case_file_obj is not None:
                    st.success(intake_alert_str)
                else:
                    st.error(intake_alert_str)
            else:
                st.info("Status: Ready to ingest dispute narrative.")

            if case_file_obj is not None:
                amt_disp = (
                    f"₹{case_file_obj.disputed_amount_inr:,.2f}"
                    if case_file_obj.disputed_amount_inr
                    else "N/A"
                )
                c_title_esc = html.escape(case_file_obj.title)
                c_tx_esc = html.escape(case_file_obj.transaction_date or "Unknown")
                c_coa_esc = html.escape(case_file_obj.cause_of_action_date or "Unknown")
                c_facts_esc = html.escape(case_file_obj.facts_summary)
                strip_html = (
                    "<div style='background-color: #FFFFFF; border: 1px solid #CCCAC6; "
                    "border-radius: 4px; padding: 18px 20px; margin-bottom: 20px;'>\n"
                    "<div style='font-family: Newsreader, Georgia, serif; font-size: 24px; "
                    f"font-weight: 400; color: #0F0E0D; margin-bottom: 16px; line-height: 1.2;'>"
                    f"{c_title_esc}</div>\n"
                    "<div style='display: grid; grid-template-columns: repeat(3, 1fr); "
                    "gap: 16px; border-top: 2px solid #CCCAC6; padding-top: 14px; "
                    "padding-bottom: 14px;'>\n"
                    "  <div>\n"
                    "    <div style='font-size: 13px; font-weight: 500; color: #706D66; "
                    "text-transform: uppercase;'>Disputed Amount</div>\n"
                    "    <div style='font-family: Newsreader, Georgia, serif; font-size: 22px; "
                    f"font-weight: 400; color: #0F0E0D;'>{amt_disp}</div>\n"
                    "  </div>\n"
                    "  <div>\n"
                    "    <div style='font-size: 13px; font-weight: 500; color: #706D66; "
                    "text-transform: uppercase;'>Transaction Date</div>\n"
                    "    <div style='font-size: 16px; font-weight: 500; color: #0F0E0D; "
                    f"margin-top: 4px; font-variant-numeric: tabular-nums;'>{c_tx_esc}</div>\n"
                    "  </div>\n"
                    "  <div>\n"
                    "    <div style='font-size: 13px; font-weight: 500; color: #706D66; "
                    "text-transform: uppercase;'>Cause of Action</div>\n"
                    "    <div style='font-size: 16px; font-weight: 500; color: #0F0E0D; "
                    f"margin-top: 4px; font-variant-numeric: tabular-nums;'>{c_coa_esc}</div>\n"
                    "  </div>\n"
                    "</div>\n"
                    "<div style='border-top: 1px solid #CCCAC6; padding-top: 14px;'>\n"
                    "  <div style='font-size: 13px; font-weight: 500; color: #706D66; "
                    "text-transform: uppercase; margin-bottom: 6px;'>"
                    "Consolidated Statement of Facts</div>\n"
                    f"  <div style='font-size: 15px; line-height: 1.5; color: #33312C;'>"
                    f"{c_facts_esc}</div>\n"
                    "</div>\n"
                    "</div>"
                )
                st.markdown(strip_html, unsafe_allow_html=True)

        # Bottom Section: Timeline, Evidence Checklist & Clarifications
        if case_file_obj is not None:
            st.markdown(
                "<hr style='border: none; border-top: 1px solid #CCCAC6; margin: 24px 0;' />",
                unsafe_allow_html=True,
            )
            st.subheader("Chronological Dispute Timeline")
            t_data = cast(list[list[str]], st.session_state.get("intake_timeline", []))
            if t_data:
                st.markdown(
                    render_editorial_table(["Date", "Significance", "Event Description"], t_data),
                    unsafe_allow_html=True,
                )

            ev1, ev2 = st.columns(2)
            with ev1:
                st.subheader("Available Documentary Proof")
                av_data = cast(list[list[str]], st.session_state.get("intake_avail", []))
                if av_data:
                    st.markdown(
                        render_editorial_table(["Document Type", "Description", "Status"], av_data),
                        unsafe_allow_html=True,
                    )
            with ev2:
                st.subheader("Missing Critical Evidence Audit")
                ms_data = cast(list[list[str]], st.session_state.get("intake_missing", []))
                if ms_data:
                    st.markdown(
                        render_editorial_table(
                            ["Missing Proof", "Statutory Reason", "How to Procure"], ms_data
                        ),
                        unsafe_allow_html=True,
                    )

            if case_file_obj.clarification_questions:
                with st.container(border=True):
                    st.markdown("#### Targeted Clarification Questions")
                    for q in case_file_obj.clarification_questions:
                        st.markdown(f"- {q}")
                    clarif_ans = st.text_area(
                        "Submit Clarification Answers",
                        placeholder="Provide details for questions above...",
                        key="ta_clarif_answers",
                    )
                    if st.button("Update Case File with Clarifications", key="btn_up_clarif"):
                        builder = CaseBuilder(
                            llm_router=active_router, scope_checker=active_scope_checker
                        )
                        up_case = builder.update_case_with_clarifications(
                            case_file_obj, {"clarification": clarif_ans}
                        )
                        st.session_state["case_file"] = up_case
                        st.success("Case file updated with clarifications!")
                        st.rerun()
        else:
            st.markdown(
                "<hr style='border: none; border-top: 1px solid #CCCAC6; margin: 24px 0;' />",
                unsafe_allow_html=True,
            )
            st.caption(
                "Enter facts and click 'Analyze Facts & Build Case' to view structured summary, "
                "chronological timeline, and evidence audit."
            )

    # ==========================================================================
    # TAB 2: Legal Standing & Provenance
    # ==========================================================================
    with tab_standing:
        eval_standing_clicked = st.button(
            "Assess Legal Standing & Retrieve Statutory Grounding",
            type="primary",
            key="btn_assess_standing",
        )

        if eval_standing_clicked:
            cur_case = cast(CaseFile | None, st.session_state.get("case_file"))
            if cur_case is None:
                st.warning("Please complete Case Intake in Tab 1 first before evaluating standing.")
            else:
                standing_res, overview_txt, viol_rows, path_rows, prov_html = (
                    handle_evaluate_standing(
                        case_file=cur_case,
                        router=active_router,
                        retriever=active_retriever,
                    )
                )
                verifier = CitationVerifier()
                v_chunks, _ = active_retriever.retrieve_with_confidence(overview_txt, top_k=5)
                telemetry = verifier.verify_response(
                    response_text=overview_txt, source_chunks=v_chunks
                )
                telemetry_banner = format_citation_telemetry_banner(
                    verified_count=len(telemetry.verified_citations),
                    flagged_count=len(telemetry.flagged_citations),
                )

                st.session_state["standing"] = standing_res
                st.session_state["standing_overview"] = overview_txt
                st.session_state["standing_violations"] = viol_rows
                st.session_state["standing_pathway"] = path_rows
                st.session_state["standing_provenance"] = prov_html
                st.session_state["standing_telemetry"] = telemetry_banner

        standing_obj = cast(LegalStanding | None, st.session_state.get("standing"))

        if standing_obj is not None:
            # Top 4-Column Statutory Standing Strip
            c_label = "Eligible Consumer" if standing_obj.is_consumer else "Ineligible"
            lim_label = standing_obj.limitation_status.replace("_", " ").title()
            fee_disp = f"₹{standing_obj.estimated_costs.court_fees_inr:,.0f}"
            pec_forum_esc = html.escape(standing_obj.pecuniary_commission_forum)
            rat_esc = html.escape(standing_obj.consumer_rationale)
            standing_strip_html = (
                "<div style='display: grid; grid-template-columns: repeat(4, 1fr); "
                "gap: 16px; border-top: 2px solid #CCCAC6; border-bottom: 1px solid #CCCAC6; "
                "padding: 16px 0; margin-bottom: 24px;'>\n"
                "  <div>\n"
                "    <div style='font-size: 13px; font-weight: 500; color: #706D66; "
                "text-transform: uppercase; margin-bottom: 6px;'>Consumer Standing</div>\n"
                "    <div style='font-family: Newsreader, Georgia, serif; font-size: 22px; "
                f"font-weight: 400; color: #0F0E0D;'>{c_label}</div>\n"
                "  </div>\n"
                "  <div>\n"
                "    <div style='font-size: 13px; font-weight: 500; color: #706D66; "
                "text-transform: uppercase; margin-bottom: 6px;'>Pecuniary Forum</div>\n"
                "    <div style='font-family: Newsreader, Georgia, serif; font-size: 20px; "
                "font-weight: 400; color: #0F0E0D; white-space: normal; "
                f"word-break: break-word;'>{pec_forum_esc}</div>\n"
                "  </div>\n"
                "  <div>\n"
                "    <div style='font-size: 13px; font-weight: 500; color: #706D66; "
                "text-transform: uppercase; margin-bottom: 6px;'>Limitation Status</div>\n"
                "    <div style='font-family: Newsreader, Georgia, serif; font-size: 22px; "
                f"font-weight: 400; color: #0F0E0D;'>{lim_label}</div>\n"
                "  </div>\n"
                "  <div>\n"
                "    <div style='font-size: 13px; font-weight: 500; color: #706D66; "
                "text-transform: uppercase; margin-bottom: 6px;'>Est. Filing Fee</div>\n"
                "    <div style='font-family: Newsreader, Georgia, serif; font-size: 22px; "
                f"font-weight: 400; color: #0F0E0D;'>{fee_disp}</div>\n"
                "  </div>\n"
                "</div>"
            )
            st.markdown(standing_strip_html, unsafe_allow_html=True)

            # Main Split View
            st_col1, st_col2 = st.columns([1.15, 1])

            with st_col1:
                rat_html = (
                    "<div style='border-left: 3px solid #0F0E0D; background-color: #F2F1F0; "
                    "padding: 14px 18px; border-radius: 0 4px 4px 0; margin-bottom: 20px;'>\n"
                    "<div style='font-size: 13px; font-weight: 500; color: #706D66; "
                    "text-transform: uppercase; margin-bottom: 6px;'>"
                    "Consumer Standing Rationale</div>\n"
                    "<div style='font-size: 15px; line-height: 1.5; color: #33312C;'>"
                    f"{rat_esc}</div>\n"
                    "</div>"
                )
                st.markdown(rat_html, unsafe_allow_html=True)

                st.markdown("#### Established Statutory Violations")
                viol_data = cast(
                    list[list[str]], st.session_state.get("standing_violations", [])
                )
                if viol_data:
                    st.markdown(
                        render_editorial_table(
                            ["Statute", "Section", "Violation Nature", "Explanation"],
                            viol_data,
                        ),
                        unsafe_allow_html=True,
                    )

                st.markdown("#### Actionable 4-Step Dispute Resolution Pathway")
                path_data = cast(list[list[str]], st.session_state.get("standing_pathway", []))
                if path_data:
                    st.markdown(
                        render_editorial_table(
                            ["Step", "Forum / Action", "Owner", "Timeline", "Fee"],
                            path_data,
                        ),
                        unsafe_allow_html=True,
                    )

                st.markdown("#### Statutory Reliefs Claimable (CPA Section 39)")
                st.markdown(
                    "- Full refund of consideration with 18% p.a. interest\n"
                    "- Compensation for mental agony & hardship\n"
                    "- Litigation costs under CPA Section 39"
                )

            with st_col2:
                st.markdown("#### Statutory Grounding & Provenance Inspector")
                telem_html = str(st.session_state.get("standing_telemetry", ""))
                if telem_html:
                    st.markdown(telem_html, unsafe_allow_html=True)

                prov_html_content = str(st.session_state.get("standing_provenance", ""))
                if prov_html_content:
                    st.markdown(prov_html_content, unsafe_allow_html=True)
                else:
                    st.caption("No statutory citations retrieved yet.")
        else:
            st.info(
                "Click 'Assess Legal Standing & Retrieve Statutory Grounding' above to assess "
                "Section 2(7) standing, limitation period, and statutory grounds."
            )

    # ==========================================================================
    # TAB 3: Document Drafter
    # ==========================================================================
    with tab_drafter:
        with st.container(border=True):
            d_ctrl1, d_ctrl2 = st.columns([2, 1])
            doc_choice = d_ctrl1.radio(
                "Select Legal Artifact to Draft",
                options=[
                    "Legal Demand Notice (15-Day)",
                    "Grievance Escalation Email",
                    "e-Daakhil Consumer Complaint Draft",
                ],
                horizontal=True,
                key="rad_doc_choice",
            )
            notice_deadline = d_ctrl2.slider(
                "Notice Period Deadline (Days)",
                min_value=7,
                max_value=30,
                value=15,
                step=1,
                key="sld_notice_deadline",
            )

            btn_col1, btn_col2 = st.columns(2)
            draft_single_clicked = btn_col1.button(
                "Draft Selected Document",
                type="primary",
                key="btn_draft_single",
                use_container_width=True,
            )
            draft_all_clicked = btn_col2.button(
                "Draft All 3 Pre-Litigation Documents",
                key="btn_draft_all",
                use_container_width=True,
            )

        cur_case_f = cast(CaseFile | None, st.session_state.get("case_file"))
        cur_stand_f = cast(LegalStanding | None, st.session_state.get("standing"))

        if draft_single_clicked:
            if cur_case_f is None:
                st.warning("Please complete Case Intake in Tab 1 first.")
            else:
                doc_obj, md_text, _, path_str = handle_draft_single(
                    case_file=cur_case_f,
                    standing=cur_stand_f,
                    doc_type=str(doc_choice),
                    notice_days=int(notice_deadline),
                    router=active_router,
                    retriever=active_retriever,
                )
                st.session_state["drafted_doc"] = doc_obj
                st.session_state["draft_raw_text"] = md_text
                st.session_state["ta_raw_markdown_editor"] = md_text
                st.session_state["draft_title"] = doc_obj.title if doc_obj else "Not Drafted"
                st.session_state["draft_recipient"] = doc_obj.recipient if doc_obj else "N/A"
                st.session_state["draft_subject"] = (
                    doc_obj.subject if doc_obj and doc_obj.subject else "Consumer Protection Demand"
                )
                st.rerun()

        if draft_all_clicked:
            if cur_case_f is None:
                st.warning("Please complete Case Intake in Tab 1 first.")
            else:
                drafter_inst = DocumentDrafter(
                    llm_router=active_router, retriever=active_retriever
                )
                docs = drafter_inst.draft_all(cur_case_f, standing=cur_stand_f)
                combo_md = "\n\n---\n\n".join(d.body_markdown for d in docs.values())
                save_dir = Path("data/exports")
                save_dir.mkdir(parents=True, exist_ok=True)
                save_file = save_dir / f"{cur_case_f.case_id}_pre_litigation_package.md"
                save_file.write_text(combo_md, encoding="utf-8")

                st.session_state["draft_raw_text"] = combo_md
                st.session_state["ta_raw_markdown_editor"] = combo_md
                st.session_state["draft_title"] = "Pre-Litigation 3-Document Package"
                st.session_state["draft_recipient"] = "Multiple Designated Authorities"
                st.session_state["draft_subject"] = "Comprehensive Consumer Dispute Artifacts"
                st.rerun()

        # Document Metadata Banner
        title_label = st.session_state.get("draft_title", "No Document Drafted Yet")
        recip_label = st.session_state.get("draft_recipient", "N/A")
        subj_label = st.session_state.get("draft_subject", "N/A")
        t_esc = html.escape(str(title_label))
        r_esc = html.escape(str(recip_label))
        s_esc = html.escape(str(subj_label))
        doc_meta_html = (
            "<div style='background-color: #FFFFFF; border: 1px solid #CCCAC6; "
            "border-radius: 4px; padding: 14px 18px; margin-bottom: 20px;'>\n"
            "<div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;'>\n"
            "  <div>\n"
            "    <div style='font-size: 12px; font-weight: 500; color: #706D66; "
            "text-transform: uppercase;'>Document Title</div>\n"
            f"    <div style='font-size: 15px; font-weight: 500; color: #0F0E0D; margin-top: 2px;'>"
            f"{t_esc}</div>\n"
            "  </div>\n"
            "  <div>\n"
            "    <div style='font-size: 12px; font-weight: 500; color: #706D66; "
            "text-transform: uppercase;'>Target Recipient</div>\n"
            f"    <div style='font-size: 15px; font-weight: 500; color: #0F0E0D; margin-top: 2px;'>"
            f"{r_esc}</div>\n"
            "  </div>\n"
            "  <div>\n"
            "    <div style='font-size: 12px; font-weight: 500; color: #706D66; "
            "text-transform: uppercase;'>Subject Line</div>\n"
            f"    <div style='font-size: 15px; font-weight: 500; color: #0F0E0D; margin-top: 2px;'>"
            f"{s_esc}</div>\n"
            "  </div>\n"
            "</div>\n"
            "</div>"
        )
        st.markdown(doc_meta_html, unsafe_allow_html=True)

        # Side-by-Side Formatted Preview & Raw Editor
        p_col1, p_col2 = st.columns(2)
        raw_draft = str(st.session_state.get("draft_raw_text", ""))

        with p_col1, st.container(border=True, height=550):
            st.markdown("### Formatted Legal Preview")
            if raw_draft:
                st.markdown(raw_draft)
            else:
                st.caption("Draft preview will render here upon document generation.")

        with p_col2:
            new_raw_draft = st.text_area(
                "Raw Editable Markdown",
                height=550,
                key="ta_raw_markdown_editor",
            )
            st.session_state["draft_raw_text"] = new_raw_draft

        # Native 1-Click Downloads
        dl_col1, dl_col2 = st.columns(2)
        cid_str = cur_case_f.case_id if cur_case_f else "consumer_draft"
        dl_col1.download_button(
            "Download Markdown (.md)",
            data=str(st.session_state.get("draft_raw_text", "")),
            file_name=f"{cid_str}_legal_document.md",
            mime="text/markdown",
            key="btn_dl_md",
            use_container_width=True,
        )
        dl_col2.download_button(
            "Download Plain Text (.txt)",
            data=str(st.session_state.get("draft_raw_text", "")),
            file_name=f"{cid_str}_legal_document.txt",
            mime="text/plain",
            key="btn_dl_txt",
            use_container_width=True,
        )

    # ==========================================================================
    # TAB 4: Opposing Counsel Simulator
    # ==========================================================================
    with tab_simulator:
        has_sim_state = bool(st.session_state.get("sim_state"))
        with st.expander("Simulator Configuration", expanded=not has_sim_state):
            t_col1, t_col2, t_col3 = st.columns(3)
            sim_tactic = t_col1.selectbox(
                "Opposing Counsel Defense Tactic",
                options=[
                    "Auto",
                    "Terms & Conditions No Refund Waiver",
                    "Absence of Unboxing Video",
                    "IT Act Section 79 Intermediary Safe Harbor",
                    "Courier / 3PL Transit Damage Disclaimer",
                    "Delivery OTP Verification Defense",
                ],
                key="sb_sim_defense_tactic",
            )
            sim_opp_name = t_col2.text_input(
                "Opposing Counsel Title",
                value="Senior Corporate Defense Counsel",
                key="txt_sim_opp_name",
            )
            sim_opp_entity = t_col3.text_input(
                "Opposing Entity Represented",
                value="E-Commerce Marketplace & Merchant",
                key="txt_sim_opp_entity",
            )

            if st.button("Start / Reset Adversarial Debate", key="btn_init_sim"):
                sim_obj = OpposingCounselSimulator(router=active_router)
                effective_case = cast(CaseFile | None, st.session_state.get("case_file"))
                if effective_case is None:
                    effective_case = CaseFile(
                        case_id="sim_case_001",
                        title="Consumer Dispute Simulation",
                        disputed_amount_inr=20000.0,
                        transaction_date="2026-01-01",
                        facts_summary="Dispute regarding refund refusal for defective merchandise.",
                        opposite_parties=[
                            OppositeParty(name="Marketplace Platform", role="Marketplace")
                        ],
                        complainant=PartyDetails(name="Consumer", city="Delhi", state="Delhi"),
                    )

                chosen_tactic = (
                    DefenseTacticType.UNBOXING_VIDEO_ABSENCE
                    if "unboxing" in str(sim_tactic).lower()
                    else DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND
                )
                fresh_state = sim_obj.start_simulation(
                    case=effective_case,
                    initial_tactic=chosen_tactic,
                    opponent_name=sim_opp_name,
                    opponent_entity=sim_opp_entity,
                )
                st.session_state["sim_state"] = fresh_state
                st.session_state["chat_history"] = [
                    {"role": "assistant", "content": fresh_state.turns[0].content}
                ]
                st.session_state["sim_scores"] = {
                    "turn_score": 0.0,
                    "cumulative_score": 0.0,
                    "strengths": "Initial argument ready. Submit your counter-argument below.",
                    "weaknesses": "Avoid purely emotional appeals.",
                    "advice": "Cite CPA 2019 provisions directly.",
                }
                st.rerun()

        # Split View: Courtroom Transcript & Live Coaching
        sim_col_left, sim_col_right = st.columns([1.3, 1])

        with sim_col_left:
            with st.container(border=True, height=460):
                chat_msgs = cast(
                    list[dict[str, str]], st.session_state.get("chat_history", [])
                )
                if not chat_msgs:
                    st.caption("Start the debate above to begin opposing counsel practice.")
                else:
                    for chat_item in chat_msgs:
                        c_role = chat_item.get("role", "assistant")
                        with st.chat_message(c_role, avatar=None):
                            st.write(chat_item.get("content", ""))

            user_rebuttal = st.chat_input(
                "State your legal rebuttal citing CPA 2019 provisions...",
                key="ci_consumer_rebuttal",
            )
            if user_rebuttal:
                cur_s = cast(SimulatorState | None, st.session_state.get("sim_state"))
                u_state, hist, s_txt, str_md, weak_md, adv_md = handle_simulator_turn(
                    user_argument=user_rebuttal,
                    state=cur_s,
                    router=active_router,
                    tactic=str(sim_tactic),
                    opponent_name=sim_opp_name,
                    opponent_entity=sim_opp_entity,
                )
                st.session_state["sim_state"] = u_state
                st.session_state["chat_history"] = hist

                latest_fb = None
                for t in reversed(u_state.turns):
                    if t.speaker == "consumer" and t.feedback is not None:
                        latest_fb = t.feedback
                        break

                t_score = latest_fb.score if latest_fb else 0.0
                st.session_state["sim_scores"] = {
                    "turn_score": t_score,
                    "cumulative_score": u_state.cumulative_score,
                    "strengths": str_md,
                    "weaknesses": weak_md,
                    "advice": adv_md,
                }
                st.rerun()

        with sim_col_right:
            st.markdown("### Live Statutory Coaching & Scoring")
            scores_data = cast(
                dict[str, Any],
                st.session_state.get(
                    "sim_scores",
                    {
                        "turn_score": 0.0,
                        "cumulative_score": 0.0,
                        "strengths": "Pending",
                        "weaknesses": "Pending",
                        "advice": "Pending",
                    },
                ),
            )
            t_score_val = float(scores_data.get("turn_score", 0.0))
            c_score_val = float(scores_data.get("cumulative_score", 0.0))

            score_header_html = (
                "<div style='display: grid; grid-template-columns: 1fr 1fr; gap: 16px; "
                "border-top: 2px solid #CCCAC6; padding-top: 14px; margin-bottom: 12px;'>\n"
                "  <div>\n"
                "    <div style='font-size: 13px; font-weight: 500; color: #706D66; "
                "text-transform: uppercase; margin-bottom: 4px;'>Turn Score</div>\n"
                "    <div style='font-family: Newsreader, Georgia, serif; font-size: 24px; "
                f"font-weight: 400; color: #0F0E0D;'>{t_score_val:.1f}"
                "<span style='font-size: 14px; color: #706D66;'> / 100</span></div>\n"
                "  </div>\n"
                "  <div>\n"
                "    <div style='font-size: 13px; font-weight: 500; color: #706D66; "
                "text-transform: uppercase; margin-bottom: 4px;'>Readiness Score</div>\n"
                "    <div style='font-family: Newsreader, Georgia, serif; font-size: 24px; "
                f"font-weight: 400; color: #0F0E0D;'>{c_score_val:.1f}"
                "<span style='font-size: 14px; color: #706D66;'> / 100</span></div>\n"
                "  </div>\n"
                "</div>"
            )
            st.markdown(score_header_html, unsafe_allow_html=True)
            m_s1, m_s2 = st.columns(2)
            m_s1.progress(min(max(t_score_val / 100.0, 0.0), 1.0))
            m_s2.progress(min(max(c_score_val / 100.0, 0.0), 1.0))

            str_text = html.escape(str(scores_data.get("strengths", "No feedback yet.")))
            weak_text = html.escape(
                str(scores_data.get("weaknesses", "No vulnerabilities detected yet."))
            )
            adv_text = html.escape(
                str(scores_data.get("advice", "Practice articulating your statutory claims."))
            )
            feedback_panels_html = (
                "<div style='border-top: 1px solid #CCCAC6; padding-top: 16px; margin-top: 16px; "
                "margin-bottom: 20px;'>\n"
                "  <div style='font-size: 16px; font-weight: 500; color: #0F0E0D; "
                "margin-bottom: 8px;'>Strengths</div>\n"
                f"  <div style='font-size: 15px; font-weight: 400; line-height: 1.45; "
                f"color: #33312C;'>{str_text}</div>\n"
                "</div>\n"
                "<div style='border-top: 1px solid #CCCAC6; padding-top: 16px; "
                "margin-bottom: 20px;'>\n"
                "  <div style='font-size: 16px; font-weight: 500; color: #0F0E0D; "
                "margin-bottom: 8px;'>Vulnerabilities / Weaknesses</div>\n"
                f"  <div style='font-size: 15px; font-weight: 400; line-height: 1.45; "
                f"color: #33312C;'>{weak_text}</div>\n"
                "</div>\n"
                "<div style='border-top: 1px solid #CCCAC6; padding-top: 16px; "
                "margin-bottom: 20px;'>\n"
                "  <div style='font-size: 16px; font-weight: 500; color: #0F0E0D; "
                "margin-bottom: 8px;'>Coach's Tactical Tip & Opponent Flaws</div>\n"
                f"  <div style='font-size: 15px; font-weight: 400; line-height: 1.45; "
                f"color: #33312C;'>{adv_text}</div>\n"
                "</div>"
            )
            st.markdown(feedback_panels_html, unsafe_allow_html=True)


# ==============================================================================
# UI Component Graph Builder Factory (Gradio Compatibility Entrypoint)
# ==============================================================================
def create_app(
    settings: Settings | None = None,
    llm_router: LLMRouter | None = None,
    retriever: StatutoryHybridRetriever | None = None,
    scope_checker: ScopeChecker | None = None,
) -> gr.Blocks:
    """Construct and export the complete 5-tab Legal Saathi Gradio UI Blocks graph.

    Args:
        settings: Optional Settings instance. Defaults to get_settings().
        llm_router: Optional LLMRouter instance. Defaults to LLMRouter(settings=settings).
        retriever: Optional StatutoryHybridRetriever instance. Defaults to in-memory store.
        scope_checker: Optional ScopeChecker instance. Defaults to ScopeChecker().

    Returns:
        gr.Blocks: Complete Gradio UI Blocks instance ready for launch or programmatic testing.
    """
    app_settings = settings or get_settings()
    router = llm_router or LLMRouter(settings=app_settings)
    checker = scope_checker or ScopeChecker()

    # Initialize fallback retriever with corpus files if none supplied
    active_retriever = retriever
    if active_retriever is None:
        corpus_dir = Path("data/statutes")
        stat_chunks: list[RetrievedChunk] = []
        if corpus_dir.exists():
            chunker = StatutoryChunker()
            for f in sorted(corpus_dir.glob("*.txt")):
                parsed = chunker.split_text(f.read_text(encoding="utf-8"))
                for sc in parsed:
                    stat_chunks.append(
                        RetrievedChunk(
                            chunk_id=sc.metadata.chunk_id,
                            content=sc.content,
                            statute=sc.metadata.statute,
                            chapter=sc.metadata.chapter,
                            section=sc.metadata.section,
                            title=sc.metadata.section_title,
                            score=0.025,
                            rank=len(stat_chunks) + 1,
                        )
                    )
        active_retriever = StatutoryHybridRetriever(
            chunks=stat_chunks,
            dense_retriever=InMemoryDenseRetriever(),
        )

    with gr.Blocks(
        title="Legal Saathi - AI Consumer Lawyer for India",
    ) as app:
        # App-level state holders
        case_state = gr.State(value=None)
        standing_state = gr.State(value=None)
        sim_state = gr.State(value=None)
        active_provider_state = gr.State(value=app_settings.llm_provider)

        # Header & Statutory Disclaimer
        gr.Markdown(
            "# ⚖️ Legal Saathi: AI Consumer Lawyer for India\n"
            "**Statutory Legal Assistant under the Consumer Protection Act, 2019 & "
            "E-Commerce Rules, 2020**\n\n"
            "*Equipped with Kotaemon-style Statutory Provenance Highlighting & Live "
            "Hot-Swappable LLM Routing*"
        )
        gr.Markdown(
            "> **⚠️ Statutory Disclaimer:** This tool provides automated legal "
            "information and self-help document drafts under CPA 2019.\n"
            "> It does not constitute formal legal representation. "
            "Disputes involving criminal offenses (BNS), Section 138 NI Act cheque "
            "bounce, or corporate B2B disputes require a registered Advocate."
        )

        with gr.Tabs():
            # ------------------------------------------------------------------
            # TAB 1: Case Intake & Facts
            # ------------------------------------------------------------------
            with gr.Tab(label="📋 Case Intake & Facts", id="tab_intake"):
                with gr.Row():
                    with gr.Column(scale=3):
                        narrative_input = gr.Textbox(
                            label="Describe Your Consumer Dispute (English, Hindi, or Hinglish)",
                            placeholder=(
                                "Example: I ordered a laptop for ₹55,000 on 2026-01-10 from "
                                "an e-commerce platform. It arrived with a broken screen. "
                                "Platform refuses refund citing manufacturer warranty."
                            ),
                            lines=7,
                        )
                        with gr.Accordion("Complainant Contact Details (Optional)", open=False):
                            with gr.Row():
                                name_in = gr.Textbox(label="Full Name", placeholder="Rahul Sharma")
                                email_in = gr.Textbox(label="Email", placeholder="user@example.com")
                                phone_in = gr.Textbox(label="Phone", placeholder="+91-9876543210")
                            with gr.Row():
                                city_in = gr.Textbox(label="City", placeholder="New Delhi")
                                state_in = gr.Textbox(label="State", placeholder="Delhi")
                        analyze_btn = gr.Button("🔍 Analyze Facts & Build Case", variant="primary")

                    with gr.Column(scale=2):
                        scope_alert_box = gr.Markdown(
                            value="*Status: Ready to ingest dispute narrative.*"
                        )
                        case_title_display = gr.Textbox(
                            label="Structured Dispute Title", interactive=False
                        )
                        with gr.Row():
                            amount_disp = gr.Textbox(
                                label="Disputed Amount (INR)", interactive=False
                            )
                            tx_date_disp = gr.Textbox(label="Transaction Date", interactive=False)
                            coa_date_disp = gr.Textbox(
                                label="Cause of Action Date", interactive=False
                            )

                facts_summary_display = gr.Textbox(
                    label="Consolidated Statement of Facts", lines=3, interactive=False
                )
                timeline_table = gr.Dataframe(
                    headers=["Date", "Significance", "Event Description"],
                    datatype=["str", "str", "str"],
                    label="Chronological Dispute Timeline",
                    interactive=False,
                )
                with gr.Row():
                    evidence_available_table = gr.Dataframe(
                        headers=["Document Type", "Description", "Status"],
                        datatype=["str", "str", "str"],
                        label="Available Documentary Proof",
                        interactive=False,
                    )
                    missing_evidence_table = gr.Dataframe(
                        headers=["Missing Proof", "Statutory Reason", "How to Procure"],
                        datatype=["str", "str", "str"],
                        label="Missing Critical Evidence Audit",
                        interactive=False,
                    )

                with gr.Accordion("Targeted Clarification Questions", open=False):
                    clarification_questions_display = gr.Markdown(
                        value="*No clarification questions pending.*"
                    )
                    clarification_answer_input = gr.Textbox(
                        label="Submit Clarification Answers",
                        placeholder="Provide details for any follow-up questions above...",
                        lines=3,
                    )
                    update_case_btn = gr.Button("Update Case File with Clarifications")

            # ------------------------------------------------------------------
            # TAB 2: Legal Standing & Provenance
            # ------------------------------------------------------------------
            with gr.Tab(label="⚖️ Legal Standing & Provenance", id="tab_standing"):
                evaluate_standing_btn = gr.Button(
                    "⚖️ Assess Legal Standing & Retrieve Statutory Grounding", variant="primary"
                )
                with gr.Row():
                    with gr.Column(scale=3):
                        standing_overview_box = gr.Markdown(
                            value="*Click the button above to evaluate Section 2(7) standing.*"
                        )
                        violations_table = gr.Dataframe(
                            headers=["Statute", "Section", "Violation Type", "Factual Relevance"],
                            datatype=["str", "str", "str", "str"],
                            label="Established Statutory Violations",
                            interactive=False,
                        )
                        pathway_table = gr.Dataframe(
                            headers=["Step", "Stage Name", "Forum / Authority", "Timeline", "Fee"],
                            datatype=["str", "str", "str", "str", "str"],
                            label="Actionable 4-Step Dispute Resolution Pathway",
                            interactive=False,
                        )
                        gr.Markdown(
                            value=(
                                "### Statutory Reliefs Claimable\n"
                                "- Full refund of consideration with 18% p.a. interest\n"
                                "- Compensation for mental agony & hardship\n"
                                "- Litigation costs under CPA Section 39"
                            )
                        )

                    with gr.Column(scale=3):
                        gr.Markdown("### 🔍 Kotaemon Visual Provenance Inspector")
                        provenance_html_viewer = gr.HTML(
                            value=(
                                "<div style='padding: 16px; color: #64748b; font-style: italic; "
                                "background-color: #f8fafc; border-radius: 8px; "
                                "border: 1px dashed #cbd5e1;'>"
                                "Statutory citations and grounding excerpts appear here.</div>"
                            )
                        )
                        citation_verification_box = gr.Markdown(
                            value=(
                                "<div style='display: inline-flex; align-items: center; "
                                "gap: 8px; padding: 6px 12px; background-color: #f8fafc; "
                                "border: 1px solid #e2e8f0; border-radius: 6px; "
                                "color: #475569; font-size: 0.85rem; font-weight: 500;'>"
                                "🛡️ <em>Citation telemetry: Ground-truth verified "
                                "against corpus.</em></div>"
                            )
                        )

            # ------------------------------------------------------------------
            # TAB 3: Document Drafter
            # ------------------------------------------------------------------
            with gr.Tab(label="📄 Document Drafter", id="tab_drafter"):
                with gr.Row():
                    doc_type_radio = gr.Radio(
                        choices=[
                            "Legal Demand Notice (15-Day)",
                            "Grievance Escalation Email",
                            "e-Daakhil Consumer Complaint Draft",
                        ],
                        value="Legal Demand Notice (15-Day)",
                        label="Select Legal Artifact to Draft",
                    )
                    notice_days_slider = gr.Slider(
                        minimum=7,
                        maximum=30,
                        value=15,
                        step=1,
                        label="Notice Period Deadline (Days)",
                    )
                    draft_single_btn = gr.Button("📝 Draft Selected Document", variant="primary")
                    draft_all_btn = gr.Button(
                        "📦 Draft All 3 Pre-Litigation Documents", variant="secondary"
                    )

                with gr.Row():
                    doc_title_disp = gr.Textbox(label="Document Title", interactive=False)
                    doc_recipient_disp = gr.Textbox(label="Target Recipient", interactive=False)
                    doc_subject_disp = gr.Textbox(label="Subject Line", interactive=False)

                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 👁️ Formatted Preview")
                        doc_markdown_preview = gr.Markdown(
                            value="*Draft preview will be rendered here upon generation.*"
                        )
                    with gr.Column(scale=1):
                        gr.Markdown("### ✏️ Raw Editable Document")
                        doc_raw_editor = gr.Textbox(
                            label="Raw Text (Editable)", lines=20, buttons=["copy"]
                        )

                with gr.Row():
                    download_file_component = gr.File(label="Download Generated Legal File")
                    download_md_btn = gr.Button("💾 Download as Markdown (.md)")
                    download_txt_btn = gr.Button("📄 Download as Plain Text (.txt)")

            # ------------------------------------------------------------------
            # TAB 4: Defense Simulator
            # ------------------------------------------------------------------
            with gr.Tab(label="🥊 Defense Simulator", id="tab_simulator"):
                with gr.Row():
                    tactic_selector = gr.Radio(
                        choices=[
                            "Auto",
                            "Terms & Conditions No Refund Waiver",
                            "Absence of Unboxing Video",
                            "IT Act Section 79 Intermediary Safe Harbor",
                            "Courier / 3PL Transit Damage Disclaimer",
                            "Delivery OTP Verification Defense",
                        ],
                        value="Auto",
                        label="Opposing Counsel Defense Tactic",
                    )
                    opponent_name_in = gr.Textbox(
                        label="Opposing Counsel Title", value="Senior Corporate Defense Counsel"
                    )
                    opponent_entity_in = gr.Textbox(
                        label="Opposing Entity Represented",
                        value="E-Commerce Marketplace & Merchant",
                    )
                    start_sim_btn = gr.Button("🥊 Start Adversarial Debate", variant="secondary")

                with gr.Row():
                    with gr.Column(scale=3):
                        sim_chatbot = gr.Chatbot(
                            label="Courtroom Debate Transcript",
                            height=420,
                        )
                        user_argument_in = gr.Textbox(
                            label="Your Legal Rebuttal / Argument",
                            placeholder="State your counter-argument citing specific facts...",
                            lines=3,
                        )
                        submit_arg_btn = gr.Button(
                            "Submit Argument to Opposing Counsel", variant="primary"
                        )

                    with gr.Column(scale=2):
                        gr.Markdown("### 🎓 Live Statutory Coaching & Scoring")
                        turn_score_disp = gr.Textbox(
                            label="Readiness Assessment Score",
                            value="Score: Pending Rebuttal",
                            interactive=False,
                        )
                        strengths_display = gr.Markdown(
                            value="*Strengths will be identified after argument submission.*"
                        )
                        weaknesses_display = gr.Markdown(
                            value="*Vulnerabilities will be highlighted after argument submission.*"
                        )
                        coach_advice_display = gr.Markdown(
                            value="*Winning counter-arguments will be provided to counter defense.*"
                        )

            # ------------------------------------------------------------------
            # TAB 5: Model Switcher & Settings
            # ------------------------------------------------------------------
            with gr.Tab(label="⚙️ Model Switcher & Settings", id="tab_switcher"):
                cur_model = app_settings.get_active_model(app_settings.llm_provider)
                with gr.Row():
                    provider_select = gr.Dropdown(
                        choices=["groq", "ollama", "openai", "gemini"],
                        value=app_settings.llm_provider,
                        label="Active LLM Provider",
                    )
                    active_provider_indicator = gr.Markdown(
                        value=f"**Current Active Provider:** `{app_settings.llm_provider}` | "
                        f"**Model:** `{cur_model}`"
                    )
                    ping_btn = gr.Button("🔌 Test Connection (Ping)", variant="primary")

                ping_status_display = gr.Markdown(
                    value="*Click 'Test Connection' to check LLM connectivity and latency.*"
                )

                with gr.Accordion("Provider Specific API Configurations", open=True):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("#### Groq Cloud (Ultra-Fast Inference)")
                            groq_model_select = gr.Dropdown(
                                choices=[
                                    "openai/gpt-oss-20b",
                                    "openai/gpt-oss-120b",
                                    "qwen/qwen3.8-27b",
                                    "llama-3.1-8b-instant",
                                    "llama-3.3-70b-versatile",
                                ],
                                value=app_settings.groq_model,
                                allow_custom_value=True,
                                label="Groq Model",
                            )
                            groq_key_val = (
                                app_settings.groq_api_key.get_secret_value()
                                if app_settings.groq_api_key
                                else ""
                            )
                            groq_key_in = gr.Textbox(
                                label="Groq API Key",
                                placeholder="gsk_...",
                                type="password",
                                value=groq_key_val,
                            )

                        with gr.Column():
                            gr.Markdown("#### Local Ollama (Offline Sovereign Inference)")
                            ollama_model_in = gr.Textbox(
                                label="Ollama Model (<= 8B parameters)",
                                value=app_settings.ollama_model,
                            )
                            ollama_url_in = gr.Textbox(
                                label="Ollama Base URL", value=app_settings.ollama_base_url
                            )

                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("#### OpenAI API")
                            openai_model_in = gr.Textbox(
                                label="OpenAI Model", value=app_settings.openai_model
                            )
                            oa_key_val = (
                                app_settings.openai_api_key.get_secret_value()
                                if app_settings.openai_api_key
                                else ""
                            )
                            openai_key_in = gr.Textbox(
                                label="OpenAI API Key",
                                placeholder="sk-...",
                                type="password",
                                value=oa_key_val,
                            )

                        with gr.Column():
                            gr.Markdown("#### Google Gemini")
                            gemini_model_in = gr.Textbox(
                                label="Gemini Model", value=app_settings.gemini_model
                            )
                            gem_key_val = (
                                app_settings.gemini_api_key.get_secret_value()
                                if app_settings.gemini_api_key
                                else ""
                            )
                            gemini_key_in = gr.Textbox(
                                label="Gemini API Key",
                                placeholder="AIza...",
                                type="password",
                                value=gem_key_val,
                            )

                save_settings_btn = gr.Button(
                    "💾 Apply & Save Provider Settings", variant="primary"
                )

        # ----------------------------------------------------------------------
        # Event Callbacks Wiring
        # ----------------------------------------------------------------------
        def on_analyze_click(
            narrative: str,
            c_name: str,
            c_email: str,
            c_phone: str,
            c_city: str,
            c_state: str,
        ) -> tuple[
            CaseFile | None,
            str,
            str,
            str,
            str,
            str,
            str,
            list[list[str]],
            list[list[str]],
            list[list[str]],
            str,
        ]:
            c_file, alert, timeline, avail, missing = handle_case_intake(
                narrative=narrative,
                router=router,
                scope_checker=checker,
                complainant_name=c_name,
                complainant_email=c_email,
                complainant_phone=c_phone,
                complainant_city=c_city,
                complainant_state=c_state,
            )
            title = c_file.title if c_file else ""
            amt = (
                f"₹{c_file.disputed_amount_inr:,.2f}"
                if c_file and c_file.disputed_amount_inr
                else "N/A"
            )
            tx_d = c_file.transaction_date if c_file and c_file.transaction_date else "Unknown"
            coa_d = (
                c_file.cause_of_action_date if c_file and c_file.cause_of_action_date else "Unknown"
            )
            facts = c_file.facts_summary if c_file else ""
            clarifications = (
                "\n".join(f"- {q}" for q in c_file.clarification_questions)
                if c_file and c_file.clarification_questions
                else "*No ambiguities identified.*"
            )
            return (
                c_file,
                alert,
                title,
                amt,
                tx_d,
                coa_d,
                facts,
                timeline,
                avail,
                missing,
                clarifications,
            )

        analyze_btn.click(
            fn=on_analyze_click,
            inputs=[narrative_input, name_in, email_in, phone_in, city_in, state_in],
            outputs=[
                case_state,
                scope_alert_box,
                case_title_display,
                amount_disp,
                tx_date_disp,
                coa_date_disp,
                facts_summary_display,
                timeline_table,
                evidence_available_table,
                missing_evidence_table,
                clarification_questions_display,
            ],
        )

        def on_update_case_click(
            c_file: CaseFile | None,
            answers_text: str,
        ) -> tuple[CaseFile | None, str]:
            if c_file is None:
                return None, "Please complete intake first."
            if not answers_text.strip():
                return c_file, "Please enter clarification answers."
            builder = CaseBuilder(llm_router=router, scope_checker=checker)
            ans_dict = {"clarification": answers_text.strip()}
            updated = builder.update_case_with_clarifications(c_file, ans_dict)
            return updated, "Case file updated with clarifications!"

        update_case_btn.click(
            fn=on_update_case_click,
            inputs=[case_state, clarification_answer_input],
            outputs=[case_state, scope_alert_box],
        )

        def on_evaluate_standing_click(
            c_file: CaseFile | None,
        ) -> tuple[LegalStanding | None, str, list[list[str]], list[list[str]], str, str]:
            standing, overview, viol, path, prov = handle_evaluate_standing(
                case_file=c_file,
                router=router,
                retriever=active_retriever,
            )
            verifier = CitationVerifier()
            v_chunks, _ = active_retriever.retrieve_with_confidence(overview, top_k=5)
            telemetry = verifier.verify_response(response_text=overview, source_chunks=v_chunks)
            telemetry_str = format_citation_telemetry_banner(
                verified_count=len(telemetry.verified_citations),
                flagged_count=len(telemetry.flagged_citations),
            )
            return standing, overview, viol, path, prov, telemetry_str

        evaluate_standing_btn.click(
            fn=on_evaluate_standing_click,
            inputs=[case_state],
            outputs=[
                standing_state,
                standing_overview_box,
                violations_table,
                pathway_table,
                provenance_html_viewer,
                citation_verification_box,
            ],
        )

        def on_draft_single_click(
            c_file: CaseFile | None,
            l_standing: LegalStanding | None,
            d_type: str,
            n_days: int,
        ) -> tuple[str, str, str, str, str, str]:
            doc, md_body, raw_body, path_str = handle_draft_single(
                case_file=c_file,
                standing=l_standing,
                doc_type=d_type,
                notice_days=n_days,
                router=router,
                retriever=active_retriever,
            )
            if doc is None:
                return "Not drafted", "N/A", "N/A", md_body, "", ""
            recipient = doc.recipient
            subject = doc.subject or "Consumer Protection Demand"
            return doc.title, recipient, subject, md_body, raw_body, path_str

        draft_single_btn.click(
            fn=on_draft_single_click,
            inputs=[case_state, standing_state, doc_type_radio, notice_days_slider],
            outputs=[
                doc_title_disp,
                doc_recipient_disp,
                doc_subject_disp,
                doc_markdown_preview,
                doc_raw_editor,
                download_file_component,
            ],
        )

        def on_draft_all_click(
            c_file: CaseFile | None,
            l_standing: LegalStanding | None,
        ) -> tuple[str, str, str, str, str, str]:
            if c_file is None:
                return "No Case", "N/A", "N/A", "Complete Tab 1 Intake first.", "", ""
            drafter = DocumentDrafter(llm_router=router, retriever=active_retriever)
            docs = drafter.draft_all(c_file, standing=l_standing)
            combo_md = "\n\n---\n\n".join(d.body_markdown for d in docs.values())
            save_path = Path("data/exports") / f"{c_file.case_id}_pre_litigation_package.md"
            save_path.parent.mkdir(parents=True, exist_ok=True)
            save_path.write_text(combo_md, encoding="utf-8")
            return (
                "Pre-Litigation 3-Document Package",
                "Multiple Recipients",
                "Complete Consumer Dispute Package",
                combo_md,
                combo_md,
                str(save_path.resolve()),
            )

        draft_all_btn.click(
            fn=on_draft_all_click,
            inputs=[case_state, standing_state],
            outputs=[
                doc_title_disp,
                doc_recipient_disp,
                doc_subject_disp,
                doc_markdown_preview,
                doc_raw_editor,
                download_file_component,
            ],
        )

        def on_download_md(raw_content: str, c_file: CaseFile | None) -> str:
            cid = c_file.case_id if c_file else "draft"
            p = Path("data/exports") / f"{cid}_document.md"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(raw_content, encoding="utf-8")
            return str(p.resolve())

        download_md_btn.click(
            fn=on_download_md,
            inputs=[doc_raw_editor, case_state],
            outputs=[download_file_component],
        )

        def on_download_txt(raw_content: str, c_file: CaseFile | None) -> str:
            cid = c_file.case_id if c_file else "draft"
            p = Path("data/exports") / f"{cid}_document.txt"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(raw_content, encoding="utf-8")
            return str(p.resolve())

        download_txt_btn.click(
            fn=on_download_txt,
            inputs=[doc_raw_editor, case_state],
            outputs=[download_file_component],
        )

        def on_start_sim_click(
            c_file: CaseFile | None,
            tactic_choice: str,
            opp_name: str,
            opp_entity: str,
        ) -> tuple[SimulatorState, list[dict[str, str]], str, str, str, str]:
            sim = OpposingCounselSimulator(router=router)
            eff_case = c_file or CaseFile(
                case_id="sim_case_001",
                title="Consumer Dispute Simulation",
                disputed_amount_inr=20000.0,
                transaction_date="2026-01-01",
                facts_summary="Dispute regarding refund refusal for defective merchandise.",
                opposite_parties=[
                    OppositeParty(
                        name="Marketplace Platform",
                        role="Marketplace",
                    )
                ],
                complainant=PartyDetails(name="Consumer", city="Delhi", state="Delhi"),
            )
            tactic_key = (
                DefenseTacticType.UNBOXING_VIDEO_ABSENCE
                if "unboxing" in tactic_choice.lower()
                else DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND
            )
            new_state = sim.start_simulation(
                case=eff_case,
                initial_tactic=tactic_key,
                opponent_name=opp_name,
                opponent_entity=opp_entity,
            )
            transcript: list[dict[str, str]] = [
                {"role": "assistant", "content": new_state.turns[0].content}
            ]
            return (
                new_state,
                transcript,
                "Score: Ready to argue",
                "Submit your argument to practice.",
                "Avoid emotional pleas.",
                "Cite CPA 2019 provisions.",
            )

        start_sim_btn.click(
            fn=on_start_sim_click,
            inputs=[case_state, tactic_selector, opponent_name_in, opponent_entity_in],
            outputs=[
                sim_state,
                sim_chatbot,
                turn_score_disp,
                strengths_display,
                weaknesses_display,
                coach_advice_display,
            ],
        )

        def on_submit_argument_click(
            user_arg: str,
            s_state: SimulatorState | None,
        ) -> tuple[SimulatorState, list[dict[str, str]], str, str, str, str, str]:
            u_state, chat, score_txt, strengths, weaknesses, advice = handle_simulator_turn(
                user_argument=user_arg,
                state=s_state,
                router=router,
            )
            return u_state, chat, score_txt, strengths, weaknesses, advice, ""

        submit_arg_btn.click(
            fn=on_submit_argument_click,
            inputs=[user_argument_in, sim_state],
            outputs=[
                sim_state,
                sim_chatbot,
                turn_score_disp,
                strengths_display,
                weaknesses_display,
                coach_advice_display,
                user_argument_in,
            ],
        )

        def on_ping_click(provider: str) -> str:
            return ping_provider(provider=provider, router=router)

        ping_btn.click(
            fn=on_ping_click,
            inputs=[provider_select],
            outputs=[ping_status_display],
        )

        def on_save_settings_click(
            provider: str,
            g_model: str,
            g_key: str,
            o_model: str,
            o_url: str,
            oa_model: str,
            oa_key: str,
            gem_model: str,
            gem_key: str,
        ) -> tuple[str, str, str]:
            if g_model:
                app_settings.groq_model = g_model.strip()
            if g_key:
                app_settings.groq_api_key = SecretStr(g_key.strip())
            if o_model:
                app_settings.ollama_model = o_model.strip()
            if o_url:
                app_settings.ollama_base_url = o_url.strip()
            if oa_model:
                app_settings.openai_model = oa_model.strip()
            if oa_key:
                app_settings.openai_api_key = SecretStr(oa_key.strip())
            if gem_model:
                app_settings.gemini_model = gem_model.strip()
            if gem_key:
                app_settings.gemini_api_key = SecretStr(gem_key.strip())

            clean_p = provider.lower().strip()
            model_map: dict[str, str] = {
                "groq": g_model,
                "ollama": o_model,
                "openai": oa_model,
                "gemini": gem_model,
            }
            chosen_model = model_map.get(clean_p) or getattr(app_settings, f"{clean_p}_model", None)

            active_msg = apply_runtime_provider(
                provider=provider,
                model_name=chosen_model,
                settings=app_settings,
                router=router,
            )

            indicator = (
                f"**Current Active Provider:** `{provider}` | "
                f"**Model:** `{app_settings.get_active_model(provider)}`"
            )
            return indicator, f"Settings updated! {active_msg}", provider

        save_settings_btn.click(
            fn=on_save_settings_click,
            inputs=[
                provider_select,
                groq_model_select,
                groq_key_in,
                ollama_model_in,
                ollama_url_in,
                openai_model_in,
                openai_key_in,
                gemini_model_in,
                gemini_key_in,
            ],
            outputs=[active_provider_indicator, ping_status_display, active_provider_state],
        )

    return app  # type: ignore[no-any-return]


def main() -> None:
    """Primary CLI entrypoint for Legal Saathi UI."""
    render_streamlit_app()


if __name__ == "__main__":
    render_streamlit_app()
