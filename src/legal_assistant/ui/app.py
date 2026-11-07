"""Gradio interactive web user interface for Legal Saathi AI Consumer Lawyer.

Integrates Kotaemon-inspired visual citation provenance with <mark> tags,
comprehensive consumer intake and timeline extraction (Mode 1), legal standing
assessment and 4-step pathway advice (Mode 2), automated legal demand and
e-Daakhil complaint drafting (Mode 3), opposing counsel adversarial practice
simulator (Mode 4), and live multi-provider runtime model switching across
Ollama, Groq Cloud, OpenAI, and Google Gemini.
"""

from __future__ import annotations

import html
import logging
import re
import time
from collections.abc import Sequence
from pathlib import Path

import gradio as gr
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


# ==============================================================================
# Helper Functions: Provenance Highlighting & Model Switching
# ==============================================================================
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
        msg = (
            "<div style='padding: 16px; color: #757575; font-style: italic;'>"
            "No statutory grounds retrieved. "
            "Enter case facts in Tab 1 to retrieve provisions.</div>"
        )
        return msg

    cards: list[str] = [
        "<div class='legal-provenance-container' style='font-family: -apple-system, "
        "BlinkMacSystemFont, Segoe UI, Roboto, sans-serif;'>"
    ]

    all_terms: set[str] = set(highlight_terms or [])
    all_terms.update(CORE_HIGHLIGHT_TERMS)
    sorted_terms = sorted(all_terms, key=len, reverse=True)

    for chunk in chunks:
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

        border_color = "#1e88e5" if is_cited else "#cfd8dc"
        bg_card = "#f0f7ff" if is_cited else "#fafafa"
        cited_badge = (
            "<span style='background-color: #1565c0; color: white; padding: 2px 8px; "
            "border-radius: 12px; font-size: 0.75rem; margin-left: 8px;'>CITED IN ADVICE</span>"
            if is_cited
            else ""
        )

        safe_content = html.escape(chunk.content)

        for term in sorted_terms:
            pattern = re.compile(rf"\b({re.escape(term)})\b", re.IGNORECASE)
            safe_content = pattern.sub(
                r"<mark style='background-color: #fff176; color: #1a237e; "
                r"font-weight: 600; padding: 1px 3px; border-radius: 2px;'>\1</mark>",
                safe_content,
            )

        card_html = (
            f"<details class='statutory-provenance-card' style='margin-bottom: 10px; "
            f"border: 1.5px solid {border_color}; border-radius: 8px; "
            f"background-color: {bg_card}; padding: 8px 12px;'>\n"
            f"  <summary style='cursor: pointer; font-weight: 600; color: #0d47a1; "
            f"display: flex; justify-content: space-between; align-items: center;'>\n"
            f"    <span>#{chunk.rank}: [{html.escape(chunk.statute)} | "
            f"Sec {html.escape(chunk.section)}] {html.escape(chunk.title)} {cited_badge}</span>\n"
            f"    <span style='color: #2e7d32; font-size: 0.85rem; font-weight: 500;'>"
            f"RRF: {chunk.score:.4f}</span>\n"
            f"  </summary>\n"
            f"  <div style='margin-top: 8px; padding: 10px; background: white; "
            f"border-radius: 4px; border-left: 4px solid #1e88e5; font-size: 0.88rem; "
            f"line-height: 1.5; color: #263238; white-space: pre-wrap;'>\n"
            f"{safe_content}\n"
            f"  </div>\n"
            f"</details>"
        )
        cards.append(card_html)

    cards.append("</div>")
    return "\n".join(cards)


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
        setattr(cfg, f"{clean_provider}_model", model_name.strip())
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
    router: LLMRouter,
    scope_checker: ScopeChecker,
    complainant_name: str = "",
    complainant_email: str = "",
    complainant_phone: str = "",
    complainant_city: str = "",
    complainant_state: str = "",
) -> tuple[CaseFile | None, str, list[list[str]], list[list[str]], list[list[str]]]:
    """Process unstructured narrative into structured CaseFile and audit evidence.

    Args:
        narrative: Verbatim consumer narrative input.
        router: Active LLMRouter instance.
        scope_checker: Pre-retrieval scope checker instance.
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

    # Pre-retrieval scope validation check
    scope_result = scope_checker.check_scope(narrative)
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

    builder = CaseBuilder(llm_router=router, scope_checker=scope_checker)
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
        f"### Legal Standing Assessment\n"
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
) -> tuple[SimulatorState, list[list[str | None]], str, str, str, str]:
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
            - Chatbot transcript list of [user, bot] turn pairs.
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

    # Build chat transcript pairs for gr.Chatbot
    chat_history: list[list[str | None]] = []
    current_user_msg: str | None = None

    for turn in updated_state.turns:
        if turn.speaker == "opposing_counsel":
            if current_user_msg is not None:
                chat_history.append([current_user_msg, turn.content])
                current_user_msg = None
            else:
                chat_history.append([None, turn.content])
        elif turn.speaker == "consumer":
            if current_user_msg is not None:
                chat_history.append([current_user_msg, None])
            current_user_msg = turn.content

    if current_user_msg is not None:
        chat_history.append([current_user_msg, None])

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
# UI Component Graph Builder Factory
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
        theme=gr.themes.Soft(primary_hue="blue", secondary_hue="indigo"),
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
                                "<div style='padding: 16px; color: #757575; font-style: italic;'>"
                                "Statutory citations and grounding excerpts appear here.</div>"
                            )
                        )
                        citation_verification_box = gr.Markdown(
                            value="*Citation telemetry: Ground-truth verified against corpus.*"
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
                            label="Raw Text (Editable)", lines=20, show_copy_button=True
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
                        sim_chatbot = gr.Chatbot(label="Courtroom Debate Transcript", height=420)
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
                                choices=["llama-3.1-8b-instant", "llama-3.3-70b-versatile"],
                                value=app_settings.groq_model,
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
            telemetry_str = (
                f"**Citation Telemetry:** {len(telemetry.verified_citations)} verified, "
                f"{len(telemetry.flagged_citations)} ungrounded citations."
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
        ) -> tuple[SimulatorState, list[list[str | None]], str, str, str, str]:
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
            transcript: list[list[str | None]] = [[None, new_state.turns[0].content]]
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
        ) -> tuple[SimulatorState, list[list[str | None]], str, str, str, str, str]:
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
            active_msg = apply_runtime_provider(
                provider=provider,
                settings=app_settings,
                router=router,
            )
            if g_model:
                app_settings.groq_model = g_model
            if g_key:
                app_settings.groq_api_key = SecretStr(g_key)
            if o_model:
                app_settings.ollama_model = o_model
            if o_url:
                app_settings.ollama_base_url = o_url
            if oa_model:
                app_settings.openai_model = oa_model
            if oa_key:
                app_settings.openai_api_key = SecretStr(oa_key)
            if gem_model:
                app_settings.gemini_model = gem_model
            if gem_key:
                app_settings.gemini_api_key = SecretStr(gem_key)

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

    return app


if __name__ == "__main__":
    app_instance = create_app()
    app_instance.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
    )
