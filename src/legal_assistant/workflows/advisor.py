"""Mode 2: Plain-Language Legal Standing, Statutory Mapping & Resolution Advisor.

Analyzes structured CaseFiles under the Consumer Protection Act, 2019 and the
Consumer Protection (E-Commerce) Rules, 2020. Retrieves authoritative statutory context
via StatutoryHybridRetriever, establishes consumer standing under Section 2(7), identifies
statutory breaches, computes deterministic pecuniary jurisdiction and court fee schedules,
verifies Section 69 limitation periods, and formulates an actionable 4-step resolution ladder.
"""

from __future__ import annotations

import logging
from datetime import date

from legal_assistant.llm.prompts import (
    LEGAL_ADVISOR_SYSTEM_PROMPT,
    format_legal_advisor_prompt,
)
from legal_assistant.llm.router import LLMRouter
from legal_assistant.rag.hybrid_retriever import StatutoryHybridRetriever
from legal_assistant.schemas import (
    CaseFile,
    CostEstimate,
    LegalStanding,
    LimitationStatus,
    ResolutionStep,
    StatutoryViolation,
    calculate_edaakhil_fee,
    check_limitation_status,
    determine_pecuniary_forum,
)

logger = logging.getLogger(__name__)

# Canonical type alias requested by system dispatch specification
LegalAnalysisResult = LegalStanding

# Curated fallback statutory excerpts if hybrid retriever is unindexed or unavailable
CANONICAL_STATUTORY_FALLBACK: list[str] = [
    (
        "[Consumer Protection Act, 2019 | Section 2(7) | Definition of Consumer]\n"
        "(7) 'consumer' means any person who buys any goods for a consideration which has been "
        "paid or promised... but does not include a person who obtains such goods for resale or "
        "for any commercial purpose. Explanation: 'commercial purpose' does not include use by a "
        "person of goods bought and used by him exclusively for the purpose of earning his "
        "livelihood, by means of self-employment."
    ),
    (
        "[Consumer Protection Act, 2019 | Section 2(10) | Defect]\n"
        "(10) 'defect' means any fault, imperfection or shortcoming in the quality, quantity, "
        "potency, purity or standard which is required to be maintained by or under any law for "
        "the time being in force or under any contract, express or implied or as is claimed by "
        "the trader in any manner whatsoever in relation to any goods."
    ),
    (
        "[Consumer Protection Act, 2019 | Section 2(11) | Deficiency in Service]\n"
        "(11) 'deficiency' means any fault, imperfection, shortcoming or inadequacy in the "
        "quality, nature and manner of performance which is required to be maintained by or "
        "under any law for the time being in force or has been undertaken to be performed by a "
        "person in pursuance of a contract or otherwise in relation to any service."
    ),
    (
        "[Consumer Protection Act, 2019 | Section 2(47) | Unfair Trade Practice]\n"
        "(47) 'unfair trade practice' means a trade practice which adopts any unfair method or "
        "deceptive practice... Clause (viii): refusing to take back goods or discontinue the "
        "service and not refunding consideration taken within thirty days if no period is "
        "stipulated."
    ),
    (
        "[Consumer Protection (E-Commerce) Rules, 2020 | Rule 4 | Duties of E-Commerce Entities]\n"
        "Rule 4(4) & (5): Every e-commerce entity shall appoint a Grievance Officer, acknowledge "
        "receipt of complaint within forty-eight hours, and redress the complaint within thirty "
        "days from date of receipt. Provide a unique ticket number for tracking."
    ),
    (
        "[Consumer Protection (E-Commerce) Rules, 2020 | Rule 6(3) & 7(4) | Return & Refund]\n"
        "No seller on marketplace, and no inventory e-commerce entity, shall refuse to take back "
        "goods, or refuse to refund consideration paid, if goods or services are defective, "
        "deficient or spurious, or do not conform to representations made."
    ),
]


class LegalAdvisor:
    """Mode 2: Plain-Language Legal Standing, Rights & Options Advisor.

    Integrates StatutoryHybridRetriever for contextual legal grounding, invokes LLMRouter
    for structured legal analysis, and reconciles deterministic calculations for pecuniary
    forum, court fees, and Section 69 limitation status with 100% statutory precision.
    """

    def __init__(
        self,
        llm_router: LLMRouter | None = None,
        retriever: StatutoryHybridRetriever | None = None,
    ) -> None:
        """Initialize LegalAdvisor.

        Args:
            llm_router: Optional custom or configured LLMRouter instance.
            retriever: Optional StatutoryHybridRetriever instance. If None,
                canonical statutory texts are used as baseline grounding.
        """
        self.router = llm_router or LLMRouter()
        self.retriever = retriever

    def assess_standing(
        self,
        case_file: CaseFile,
        provider: str | None = None,
        use_llm: bool = True,
    ) -> LegalStanding:
        """Assess consumer legal standing (alias for analyze_standing).

        Args:
            case_file: Structured CaseFile.
            provider: Optional LLM provider override.
            use_llm: Whether to attempt LLM analysis. Defaults to True.

        Returns:
            LegalStanding instance.
        """
        return self.analyze_standing(case_file=case_file, provider=provider, use_llm=use_llm)

    def analyze_standing(
        self,
        case_file: CaseFile,
        provider: str | None = None,
        use_llm: bool = True,
    ) -> LegalStanding:
        """Assess consumer legal standing, statutory breaches, and resolution options.

        Args:
            case_file: Structured CaseFile output from Mode 1 Case Builder.
            provider: Optional LLM provider name override.
            use_llm: Whether to attempt LLM analysis. Defaults to True.

        Returns:
            LegalStanding (LegalAnalysisResult) containing verified consumer standing,
            statutory violations, pecuniary forum, limitation assessment, and 4-step pathway.
        """
        # 1. Authoritative Statutory Calculations (Deterministic Ground Truth)
        pecuniary_forum_name, forum_rationale = determine_pecuniary_forum(
            case_file.disputed_amount_inr
        )
        edaakhil_fee_inr = calculate_edaakhil_fee(case_file.disputed_amount_inr)

        coa_date_str = case_file.cause_of_action_date or case_file.transaction_date
        is_within_limitation, days_remaining, limitation_rationale = check_limitation_status(
            cause_of_action_date=coa_date_str,
            filing_date=date.today(),
        )

        days_elapsed = 730 - days_remaining
        if not is_within_limitation:
            limitation_status_enum = LimitationStatus.BARRED_BY_LIMITATION.value
        elif days_remaining <= 130:
            limitation_status_enum = LimitationStatus.APPROACHING_DEADLINE.value
        else:
            limitation_status_enum = LimitationStatus.WITHIN_LIMITATION.value

        # 2. Retrieve Statutory Grounding via RAG
        statutes_context: list[str] = []
        if self.retriever is not None:
            rag_query = (
                f"{case_file.title} {case_file.facts_summary} "
                "deficiency in service unfair trade practice refund refusal e-commerce rules 2020"
            )
            retrieved_chunks = self.retriever.retrieve(query=rag_query, top_k=5)
            if retrieved_chunks:
                statutes_context = [
                    f"[{c.statute} | Section {c.section} | {c.title}]\n{c.content}"
                    for c in retrieved_chunks
                ]

        if not statutes_context:
            statutes_context = list(CANONICAL_STATUTORY_FALLBACK)

        # 3. Construct Prompt & Attempt Structured LLM Generation
        standing: LegalStanding | None = None
        if use_llm:
            try:
                prompt = format_legal_advisor_prompt(
                    case_summary=(
                        f"Title: {case_file.title}\n"
                        f"Disputed Amount: INR {case_file.disputed_amount_inr}\n"
                        f"Transaction Date: {case_file.transaction_date}\n"
                        f"Cause of Action Date: {coa_date_str}\n"
                        f"Facts: {case_file.facts_summary}"
                    ),
                    retrieved_statutes=statutes_context,
                    schema=LegalStanding,
                )

                provider_order = [provider] if provider else None
                standing = self.router.generate_structured_with_fallback(
                    prompt=prompt,
                    schema=LegalStanding,
                    system_prompt=LEGAL_ADVISOR_SYSTEM_PROMPT,
                    provider_order=provider_order,
                )
            except Exception as exc:
                logger.info(
                    "LLM standing analysis unavailable: %s. Using deterministic analysis.",
                    exc,
                )
                standing = self._build_deterministic_standing(case_file)
        else:
            standing = self._build_deterministic_standing(case_file)

        # 4. Anti-Hallucination Reconciler: Enforce Authoritative Statutory Calculations
        standing.pecuniary_commission_forum = pecuniary_forum_name
        standing.jurisdiction_rationale = forum_rationale
        if case_file.disputed_amount_inr <= 5_000_000.0:
            standing.pecuniary_jurisdiction_limit = (
                "District Commission (Up to ₹50 Lakhs) under 2021 Pecuniary Rules"
            )
        elif case_file.disputed_amount_inr <= 20_000_000.0:
            standing.pecuniary_jurisdiction_limit = (
                "State Commission (> ₹50 Lakhs up to ₹2 Crores) under 2021 Pecuniary Rules"
            )
        else:
            standing.pecuniary_jurisdiction_limit = (
                "National Commission (NCDRC, Exceeding ₹2 Crores) under 2021 Pecuniary Rules"
            )

        standing.limitation_status = limitation_status_enum
        standing.days_since_cause_of_action = max(0, days_elapsed)
        standing.limitation_period_days = 730
        standing.limitation_rationale = limitation_rationale

        # Reconcile 4-step resolution ladder
        authoritative_pathway = self.build_resolution_pathway(
            case_file=case_file,
            forum_name=pecuniary_forum_name,
            court_fee=edaakhil_fee_inr,
        )
        if len(standing.resolution_pathway) < 4:
            standing.resolution_pathway = authoritative_pathway

        # Reconcile cost estimate
        standing.estimated_costs = CostEstimate(
            court_fees_inr=float(edaakhil_fee_inr),
            notice_costs_inr=100.0,
            lawyer_required=False,
            total_estimated_out_of_pocket_inr=(
                f"₹{edaakhil_fee_inr} e-Daakhil statutory fee + ~₹100 Speed Post AD "
                "(Advocate not required; party-in-person permitted under Section 35 CPA 2019)"
            ),
        )

        # Ensure core statutory remedies are listed
        if not standing.reliefs_entitled:
            standing.reliefs_entitled = [
                f"Refund of ₹{case_file.disputed_amount_inr:,.2f} with 12-18% p.a. interest",
                "Replacement of defective goods or removal of deficiency under Section 39(1)",
                "Compensation for mental agony and emotional harassment under Section 39(1)(d)",
                "Award of litigation costs and incidental expenses under Section 39(1)(m)",
            ]

        return standing

    def _build_deterministic_standing(self, case_file: CaseFile) -> LegalStanding:
        """Construct fallback LegalStanding deterministically when LLM is offline."""
        violations: list[StatutoryViolation] = [
            StatutoryViolation(
                statute="Consumer Protection Act, 2019",
                section_or_rule="Section 2(11)",
                title="Deficiency in Service",
                violation_nature="deficiency_in_service",
                explanation="Shortcoming in quality and manner of performance in servicing order.",
            ),
            StatutoryViolation(
                statute="Consumer Protection Act, 2019",
                section_or_rule="Section 2(47)",
                title="Unfair Trade Practice",
                violation_nature="unfair_trade_practice",
                explanation="Refusal to refund consideration for defective goods or services.",
            ),
            StatutoryViolation(
                statute="Consumer Protection (E-Commerce) Rules, 2020",
                section_or_rule="Rule 6(3)",
                title="Prohibition of Return / Refund Refusal",
                violation_nature="rule_violation",
                explanation="Seller refused to accept return or refund for defective goods.",
            ),
        ]

        if any(
            w in case_file.facts_summary.lower()
            for w in ("broken", "crack", "defect", "damage", "fault")
        ):
            violations.append(
                StatutoryViolation(
                    statute="Consumer Protection Act, 2019",
                    section_or_rule="Section 2(10)",
                    title="Defect in Goods",
                    violation_nature="defect_in_goods",
                    explanation="Material imperfection and defect in goods delivered to consumer.",
                )
            )

        return LegalStanding(
            is_consumer=True,
            consumer_rationale=(
                f"The complainant paid consideration of ₹{case_file.disputed_amount_inr:,.2f} "
                "for personal use, qualifying as a consumer under Section 2(7) of CPA 2019."
            ),
            statutory_violations=violations,
            pecuniary_commission_forum="District Consumer Disputes Redressal Commission",
            pecuniary_jurisdiction_limit="Up to ₹50 Lakhs under 2021 Pecuniary Rules",
            jurisdiction_rationale="Governed by consideration paid under 2021 Pecuniary Rules.",
            limitation_period_days=730,
            days_since_cause_of_action=30,
            limitation_status="within_limitation",
            limitation_rationale=(
                "Complaint is within the 2-year statutory limit under Section 69(1) of CPA 2019."
            ),
            resolution_pathway=[],
            estimated_timeline="3 to 12 months for complete adjudication",
            estimated_costs=CostEstimate(
                court_fees_inr=0.0,
                notice_costs_inr=100.0,
                lawyer_required=False,
                total_estimated_out_of_pocket_inr="Nil court fee + ~₹100 postal charges",
            ),
            reliefs_entitled=[],
        )

    def build_resolution_pathway(
        self,
        case_file: CaseFile,
        forum_name: str | None = None,
        court_fee: int | None = None,
    ) -> list[ResolutionStep]:
        """Construct the standard 4-step statutory dispute resolution ladder.

        Args:
            case_file: Associated CaseFile.
            forum_name: Competent commission name (District / State / National).
            court_fee: Official e-Daakhil filing fee in INR.

        Returns:
            list[ResolutionStep]: 4 sequential dispute resolution steps.
        """
        target_forum = forum_name or determine_pecuniary_forum(case_file.disputed_amount_inr)[0]
        fee = (
            court_fee
            if court_fee is not None
            else calculate_edaakhil_fee(case_file.disputed_amount_inr)
        )

        return [
            ResolutionStep(
                step_number=1,
                forum_or_action="Platform Grievance Officer Escalation",
                description=(
                    "Submit formal written escalation to the designated Grievance Officer of the "
                    "e-commerce marketplace citing the 48-hour acknowledgement and 30-day "
                    "resolution mandate. Demand unique complaint ticket number."
                ),
                statutory_basis=(
                    "Rule 4(4) and Rule 4(5), Consumer Protection (E-Commerce) Rules, 2020"
                ),
                expected_duration="48 hours acknowledgement; 30 days final resolution",
                action_owner="Consumer",
                cost_inr=0.0,
            ),
            ResolutionStep(
                step_number=2,
                forum_or_action="National Consumer Helpline (NCH 1915)",
                description=(
                    "Lodge an informal convergence grievance via Toll-Free 1915, official WhatsApp "
                    "bot (+91 8800001915), or web portal (consumerhelpline.gov.in). Leverages "
                    "network with 800+ companies for informal pre-litigation settlement."
                ),
                statutory_basis="NCH-INGRAM Convergence Framework (Department of Consumer Affairs)",
                expected_duration="30 to 45 calendar days",
                action_owner="Consumer",
                cost_inr=0.0,
            ),
            ResolutionStep(
                step_number=3,
                forum_or_action="Formal 15-Day Legal Notice",
                description=(
                    "Dispatch a formal Legal Demand Notice via Speed Post with AD and registered "
                    "email to Seller and Marketplace headquarters. Demands full refund, 18% "
                    "interest, and litigation costs within 15 days, warning of e-Daakhil filing."
                ),
                statutory_basis=(
                    "Sections 2(10), 2(11), 2(47) CPA 2019 & Rule 6(3) E-Commerce Rules"
                ),
                expected_duration="15 calendar days from date of receipt",
                action_owner="Consumer / Advocate",
                cost_inr=100.0,
            ),
            ResolutionStep(
                step_number=4,
                forum_or_action=f"e-Daakhil Online Filing ({target_forum})",
                description=(
                    f"Institute a formal online consumer complaint on edaakhil.nic.in before the "
                    f"{target_forum} under Section 35(1) second proviso. Consumer may "
                    f"self-represent (party-in-person). Fee payable online via Bharatkosh."
                ),
                statutory_basis=(
                    "Section 35 CPA 2019 read with 2021 Pecuniary Rules & Section 34(2)(d)"
                ),
                expected_duration="3 to 12 months for final adjudication",
                action_owner="Consumer (Party-in-Person) / Advocate",
                cost_inr=float(fee),
            ),
        ]
