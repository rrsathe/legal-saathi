"""Domain schemas for Legal Saathi AI Consumer Lawyer.

Defines Pydantic v2 data models for all 4 legal workflow modes (Case Builder,
Standing Advisor, Document Drafter, and Opposing Counsel Simulator), anti-hallucination
guardrails (Scope Checker, Citation Verifier), statutory calculations, and benchmark evaluation.
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ==============================================================================
# Enumerations and Domain Constants
# ==============================================================================


class PecuniaryForum(StrEnum):
    """Consumer dispute redressal commissions under 2021 Pecuniary Rules."""

    DISTRICT_COMMISSION = "District Consumer Disputes Redressal Commission"
    STATE_COMMISSION = "State Consumer Disputes Redressal Commission"
    NATIONAL_COMMISSION = "National Consumer Disputes Redressal Commission (NCDRC)"


class LimitationStatus(StrEnum):
    """Statutory limitation statuses under Section 69 CPA 2019 (2-year limit)."""

    WITHIN_LIMITATION = "within_limitation"
    APPROACHING_DEADLINE = "approaching_deadline"
    BARRED_BY_LIMITATION = "barred_by_limitation"
    CONDONATION_REQUIRED = "condonation_required"


class DocumentType(StrEnum):
    """Types of legal artifacts drafted by Mode 3."""

    GRIEVANCE_EMAIL = "grievance_email"
    LEGAL_NOTICE = "legal_notice"
    EDAAKHIL_COMPLAINT = "edaakhil_complaint"


class DebateSpeaker(StrEnum):
    """Roles participating in Mode 4 opposing counsel simulation."""

    USER = "user"
    OPPOSING_COUNSEL = "opposing_counsel"
    JUDGE = "judge"
    MEDIATOR = "mediator"


class ScopeCategory(StrEnum):
    """Classification of dispute scope for anti-hallucination guardrail 1."""

    CONSUMER_DISPUTE = "consumer_dispute"
    CRIMINAL_OFFENSE = "criminal_offense"
    CHEQUE_BOUNCE = "cheque_bounce"
    COMMERCIAL_B2B = "commercial_b2b"
    FAMILY_DIVORCE = "family_divorce"
    LABOR_EMPLOYMENT = "labor_employment"
    URGENT_INJUNCTION = "urgent_injunction"
    OTHER_NON_CONSUMER = "other_non_consumer"


# ==============================================================================
# Statutory Citation & Evidence Models
# ==============================================================================


class Citation(BaseModel):
    """Statutory citation reference anchored to Indian consumer legislation."""

    model_config = ConfigDict(extra="ignore")

    statute: str = Field(
        ...,
        description="Name of statute, e.g. 'Consumer Protection Act, 2019'",
    )
    section: str = Field(
        ...,
        description="Section or Rule identifier, e.g. 'Section 2(47)', 'Rule 4(5)'",
    )
    title: str = Field(
        default="",
        description="Title or rubric of statutory provision, e.g. 'Unfair Trade Practice'",
    )
    text_excerpt: str = Field(
        ...,
        description="Authoritative text excerpt or key statutory requirement",
    )
    is_verified: bool = Field(
        default=False,
        description="Whether this citation was verified against the statutory corpus",
    )
    verification_source: str | None = Field(
        default=None,
        description="Source chunk ID or document name confirming validity",
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score for this citation",
    )


class TimelineEvent(BaseModel):
    """Chronological event in the dispute history."""

    model_config = ConfigDict(extra="ignore")

    event_id: str = Field(
        default_factory=lambda: f"evt_{uuid.uuid4().hex[:6]}",
        description="Unique identifier for timeline event",
    )
    date: str = Field(
        ...,
        description="Date of event (YYYY-MM-DD or readable date string)",
    )
    description: str = Field(
        ...,
        description="Detailed description of what occurred",
    )
    supporting_document: str | None = Field(
        default=None,
        description="Name or reference of supporting documentary proof (e.g. 'Invoice #1029')",
    )
    significance: str = Field(
        ...,
        description="Legal relevance (e.g. 'Date of purchase', 'Date refund formally denied')",
    )


class EvidenceItem(BaseModel):
    """Documentary or digital evidence item held by complainant."""

    model_config = ConfigDict(extra="ignore")

    item_name: str = Field(
        ...,
        description="Evidence item title (e.g. 'Tax Invoice', 'Unboxing Video', 'Email Trail')",
    )
    category: str = Field(
        default="documentary",
        description="Category: documentary, payment_record, communication, visual, expert",
    )
    is_available: bool = Field(
        default=True,
        description="Whether complainant currently has possession of this evidence",
    )
    description: str = Field(
        ...,
        description="Content and probative value of the evidence item",
    )
    file_reference: str | None = Field(
        default=None,
        description="Filename or path of uploaded proof if available",
    )


class MissingEvidence(BaseModel):
    """Audit of required evidence currently missing from complainant's case."""

    model_config = ConfigDict(extra="ignore")

    item_name: str = Field(
        ...,
        description="Missing proof item name (e.g. 'Job Sheet / Service Center Report')",
    )
    importance: str = Field(
        default="high",
        description="Criticality: critical, high, medium, optional",
    )
    why_needed: str = Field(
        ...,
        description="Legal reason this evidence is essential under CPA 2019 evidentiary burden",
    )
    where_to_obtain: str = Field(
        ...,
        description="Actionable guidance on where and how to obtain this evidence",
    )


class ClarificationQuestion(BaseModel):
    """Follow-up question to resolve ambiguity in consumer's factual narrative."""

    model_config = ConfigDict(extra="ignore")

    question_id: str = Field(
        default_factory=lambda: f"q_{uuid.uuid4().hex[:6]}",
        description="Unique question identifier",
    )
    question: str = Field(
        ...,
        description="Specific question directed to the complainant",
    )
    legal_relevance: str = Field(
        ...,
        description="Why this fact matters for statutory standing or pecuniary determination",
    )
    suggested_answer_options: list[str] = Field(
        default_factory=list,
        description="Optional list of suggested responses for guided intake",
    )


class Party(BaseModel):
    """Party involved in a consumer dispute."""

    model_config = ConfigDict(extra="ignore")

    name: str = Field(..., description="Full legal or registered business name")
    role: str = Field(
        default="complainant",
        description="Role in transaction (e.g. 'Complainant', 'Seller', 'Manufacturer')",
    )
    address: str | None = Field(default=None, description="Physical or corporate address")
    email: str | None = Field(default=None, description="Contact email address")
    phone: str | None = Field(default=None, description="Contact telephone/mobile number")
    city: str | None = Field(default=None, description="City for territorial jurisdiction")
    state: str | None = Field(default=None, description="State of residence in India")
    party_type: str = Field(
        default="individual",
        description="Classification: individual, joint, marketplace, corporate",
    )


class PartyDetails(Party):
    """Complainant personal and contact information."""

    party_type: str = Field(
        default="individual",
        description="Party category: individual, joint, association",
    )


class OppositeParty(Party):
    """Opposite party (merchant, e-commerce platform, manufacturer) in dispute."""

    role: str = Field(
        ...,
        description="Role in transaction (e.g. 'E-Commerce Marketplace', 'Seller', 'Manufacturer')",
    )
    entity_type: str = Field(
        default="marketplace",
        description="Classification: marketplace, inventory_ecommerce, authorized_seller",
    )


# ==============================================================================
# Mode 1: Case Builder Schema
# ==============================================================================


class CaseFile(BaseModel):
    """Structured consumer dispute case file extracted from narrative intake."""

    model_config = ConfigDict(extra="ignore")

    case_id: str = Field(
        default_factory=lambda: f"case_{uuid.uuid4().hex[:8]}",
        description="Unique case file identifier",
    )
    title: str = Field(
        ...,
        description="Concise descriptive title of consumer dispute",
    )
    complainant: PartyDetails = Field(
        ...,
        description="Complainant personal and contact details",
    )
    opposite_parties: list[OppositeParty] = Field(
        ...,
        min_length=1,
        description="List of opposite parties against whom remedies are sought",
    )
    transaction_date: str = Field(
        ...,
        description="Date of purchase or transaction (YYYY-MM-DD or readable date)",
    )
    cause_of_action_date: str | None = Field(
        default=None,
        description="Date when cause of action first arose (e.g. date of final refund refusal)",
    )
    disputed_amount_inr: float = Field(
        ...,
        ge=0.0,
        description="Actual consideration paid or amount in dispute in Indian Rupees (INR)",
    )
    compensation_claimed_inr: float = Field(
        default=0.0,
        ge=0.0,
        description="Additional damages/compensation claimed for mental agony and harassment",
    )
    facts_summary: str = Field(
        ...,
        description="Cohesive chronological summary of material dispute facts",
    )
    timeline: list[TimelineEvent] = Field(
        default_factory=list,
        description="Chronological event sequence from order to dispute",
    )
    evidence_checklist: list[EvidenceItem] = Field(
        default_factory=list,
        description="Checklist of available documentary and digital evidence",
    )
    missing_evidence: list[MissingEvidence] = Field(
        default_factory=list,
        description="Audit of missing proofs required before formal filing",
    )
    clarification_questions: list[str] = Field(
        default_factory=list,
        description="Open clarification questions required to remove ambiguities",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Categorization tags (e.g. 'e-commerce', 'defective_goods', 'refund_refusal')",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when case was created",
    )

    @field_validator("disputed_amount_inr", "compensation_claimed_inr", mode="before")
    @classmethod
    def parse_inr_amount(cls, value: Any) -> float:
        """Sanitize and parse INR amount strings with currency symbols or commas.

        Args:
            value: Raw amount value.

        Returns:
            Float representation of amount.
        """
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            sanitized = (
                value.replace("₹", "").replace("Rs.", "").replace("Rs", "").replace(",", "").strip()
            )
            try:
                return float(sanitized)
            except ValueError:
                return 0.0
        return 0.0


# ==============================================================================
# Mode 2: Plain-Language Legal Standing Schemas
# ==============================================================================


class StatutoryViolation(BaseModel):
    """Specific statutory violation identified under CPA 2019 or E-Commerce Rules 2020."""

    model_config = ConfigDict(extra="ignore")

    statute: str = Field(
        ...,
        description="Statute name, e.g. 'Consumer Protection Act, 2019'",
    )
    section_or_rule: str = Field(
        ...,
        description="Section or rule number, e.g. 'Section 2(47)(viii)', 'Rule 4(5)'",
    )
    title: str = Field(
        ...,
        description="Rubric or provision title, e.g. 'Refusal to Refund for Defective Goods'",
    )
    violation_nature: str = Field(
        ...,
        description="Nature: defect, deficiency, unfair_trade_practice, misleading_advertisement",
    )
    explanation: str = Field(
        ...,
        description="Plain-language explanation of how the opposite party violated this rule",
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score for this statutory grounding",
    )


class ResolutionStep(BaseModel):
    """One sequential step in the consumer resolution ladder."""

    model_config = ConfigDict(extra="ignore")

    step_number: int = Field(..., ge=1, description="Sequential step number (1 to 4)")
    forum_or_action: str = Field(
        ...,
        description="Action name (e.g. 'Grievance Officer Escalation', 'NCH 1915', 'Legal Notice')",
    )
    description: str = Field(
        ...,
        description="Clear instructions on how to execute this step and what to demand",
    )
    statutory_basis: str | None = Field(
        default=None,
        description="Supporting statute reference (e.g. 'Rule 4(5) E-Commerce Rules')",
    )
    expected_duration: str = Field(
        ...,
        description="Expected timeline (e.g. '48 hours ack, 30 days resolution', '15 days notice')",
    )
    action_owner: str = Field(
        default="Consumer",
        description="Party executing action (Consumer, Advocate, Commission)",
    )
    cost_inr: float = Field(
        default=0.0,
        description="Official statutory fee or cost in INR",
    )


class CostEstimate(BaseModel):
    """Detailed breakdown of costs and statutory fees for consumer redressal."""

    model_config = ConfigDict(extra="ignore")

    court_fees_inr: float = Field(
        default=0.0,
        ge=0.0,
        description="Statutory fee on e-Daakhil (₹0 for <= ₹5L, ₹200-₹1000 for up to ₹50L)",
    )
    notice_costs_inr: float = Field(
        default=100.0,
        ge=0.0,
        description="Speed Post with Acknowledgment Due (AD) postal charges (~₹50-₹100)",
    )
    lawyer_required: bool = Field(
        default=False,
        description="Whether an advocate is legally required (False: party-in-person permitted)",
    )
    total_estimated_out_of_pocket_inr: str = Field(
        ...,
        description="Readable cost summary (e.g. '₹0 fee under ₹5 Lakhs; ~₹100 for Speed Post')",
    )


class LegalStanding(BaseModel):
    """Comprehensive legal standing assessment and options analysis for consumer."""

    model_config = ConfigDict(extra="ignore")

    is_consumer: bool = Field(
        ...,
        description="Whether complainant qualifies as a 'consumer' under Section 2(7) CPA 2019",
    )
    consumer_rationale: str = Field(
        ...,
        description="Detailed legal reasoning establishing consumer status",
    )
    statutory_violations: list[StatutoryViolation] = Field(
        default_factory=list,
        description="List of established statutory violations against opposite parties",
    )
    pecuniary_commission_forum: str = Field(
        ...,
        description="Designated consumer commission based on 2021 Pecuniary Rules",
    )
    pecuniary_jurisdiction_limit: str = Field(
        ...,
        description="Rule threshold (e.g. 'District Commission (Up to ₹50 Lakhs) 2021 Rules')",
    )
    jurisdiction_rationale: str = Field(
        ...,
        description="Explanation of pecuniary and territorial jurisdiction under CPA 2019",
    )
    limitation_period_days: int = Field(
        default=730,
        description="Limitation period under Section 69 CPA 2019 (2 years = 730 days)",
    )
    days_since_cause_of_action: int | None = Field(
        default=None,
        ge=0,
        description="Elapsed days since cause of action arose",
    )
    limitation_status: str = Field(
        default="within_limitation",
        description="Limitation status (within_limitation, approaching_deadline, etc.)",
    )
    limitation_rationale: str = Field(
        ...,
        description="Detailed limitation analysis under Section 69 CPA 2019",
    )
    resolution_pathway: list[ResolutionStep] = Field(
        default_factory=list,
        description="Recommended 4-stage escalation ladder (Grievance -> NCH -> Notice -> Court)",
    )
    estimated_timeline: str = Field(
        ...,
        description="Projected timeline across stages (e.g. '15-45 days pre-litigation')",
    )
    estimated_costs: CostEstimate = Field(
        ...,
        description="Itemized breakdown of statutory fees and expenses",
    )
    reliefs_entitled: list[str] = Field(
        default_factory=list,
        description="Remedies under Section 39 CPA 2019 (Refund, Replacement, Compensation, Costs)",
    )


# ==============================================================================
# Mode 3: Automated Document Drafter Schemas
# ==============================================================================


class DraftedDocument(BaseModel):
    """Ready-to-send legally formatted document artifact."""

    model_config = ConfigDict(extra="ignore")

    document_id: str = Field(
        default_factory=lambda: f"doc_{uuid.uuid4().hex[:8]}",
        description="Unique document identifier",
    )
    document_type: Literal["grievance_email", "legal_notice", "edaakhil_complaint"] = Field(
        ...,
        description="Document artifact type",
    )
    title: str = Field(
        ...,
        description="Formal title of legal artifact (e.g. 'Formal Legal Notice under CPA 2019')",
    )
    recipient: str = Field(
        ...,
        description="Full recipient legal entity, designation, and address/email",
    )
    subject: str = Field(
        ...,
        description="Formal subject line",
    )
    body_markdown: str = Field(
        ...,
        description="Complete document body formatted in Markdown with statutory citations",
    )
    statutory_citations: list[Citation] = Field(
        default_factory=list,
        description="Statutory sections and rules invoked in document",
    )
    verification_statement: str | None = Field(
        default=None,
        description="Solemn verification statement for formal complaints / petitions",
    )
    annexure_list: list[str] = Field(
        default_factory=list,
        description="List of marked annexures (e.g. 'Annexure A: Tax Invoice')",
    )
    demand_summary: str = Field(
        ...,
        description="Summary of relief demanded (e.g. 'Full refund of ₹54,000 in 15 days')",
    )
    response_deadline_days: int = Field(
        default=15,
        description="Response window in days (e.g. 15 days for legal notice)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional template metadata",
    )


class LegalNotice(DraftedDocument):
    """Specialized schema for 15-day formal Legal Notice demand letter."""

    document_type: Literal["grievance_email", "legal_notice", "edaakhil_complaint"] = Field(
        default="legal_notice",
        description="Document artifact type",
    )
    notice_period_days: int = Field(
        default=15,
        description="Statutory notice period granted to opposite party before Commission filing",
    )
    claim_amount_inr: float = Field(
        default=0.0,
        ge=0.0,
        description="Total monetary demand including refund and damages in INR",
    )


# ==============================================================================
# Mode 4: Opposing Counsel Simulator Schemas
# ==============================================================================


class DebateTurn(BaseModel):
    """Single exchange in argument practice simulation."""

    model_config = ConfigDict(extra="ignore")

    turn_number: int = Field(
        ...,
        ge=1,
        description="1-based turn number in debate sequence",
    )
    speaker: Literal["user", "opposing_counsel", "judge", "mediator"] = Field(
        ...,
        description="Role of current speaker",
    )
    argument: str = Field(
        ...,
        description="Substantive argument or defense advanced by speaker",
    )
    defense_strategy_name: str | None = Field(
        default=None,
        description="Common merchant defense tactic (e.g. 'No Refund Policy', 'IT Act 79')",
    )
    statutory_counter: str | None = Field(
        default=None,
        description="Authoritative statutory counter-argument neutralizing the defense",
    )
    evidenced_facts: list[str] = Field(
        default_factory=list,
        description="Specific facts and evidence documents supporting the rebuttal",
    )
    counter_strategy: str | None = Field(
        default=None,
        description="Tactical coaching advice for consumer on delivery and presentation",
    )
    weakness_exploited: str | None = Field(
        default=None,
        description="Vulnerability in opponent's stance (e.g. 'Unfair contract term void')",
    )


class SimulationSession(BaseModel):
    """Full practice debate session transcript and assessment."""

    model_config = ConfigDict(extra="ignore")

    session_id: str = Field(
        default_factory=lambda: f"sim_{uuid.uuid4().hex[:8]}",
        description="Unique simulation session identifier",
    )
    case_id: str = Field(
        ...,
        description="Associated CaseFile identifier",
    )
    opponent_name: str = Field(
        ...,
        description="Name of opposing platform or merchant roleplayed",
    )
    turns: list[DebateTurn] = Field(
        default_factory=list,
        description="Chronological transcript of debate turns",
    )
    readiness_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Consumer argument readiness percentage score (0-100)",
    )
    coaching_summary: str = Field(
        default="",
        description="Overall evaluation of consumer's argumentation and key legal takeaways",
    )


# ==============================================================================
# Guardrails: Scope Checker & Citation Verifier Schemas
# ==============================================================================


class ScopeResult(BaseModel):
    """Determination from pre-retrieval scope and escalation guardrail."""

    model_config = ConfigDict(extra="ignore")

    is_in_scope: bool = Field(
        ...,
        description="True if query is a consumer dispute; False if non-consumer matter",
    )
    out_of_scope_category: str | None = Field(
        default=None,
        description="Category if out of scope: criminal, cheque_bounce, commercial_b2b, etc.",
    )
    escalation_advice: str | None = Field(
        default=None,
        description="Mandatory advisory directing user to an Advocate, Police, or Court",
    )
    detected_triggers: list[str] = Field(
        default_factory=list,
        description="Specific keywords or legal concepts triggering scope determination",
    )


class VerifiedResponse(BaseModel):
    """Sanitized response payload after post-generation citation verification."""

    model_config = ConfigDict(extra="ignore")

    cleaned_text: str = Field(
        ...,
        description="Response text with hallucinated citations stripped or corrected",
    )
    verified_citations: list[str] = Field(
        default_factory=list,
        description="List of statutory sections/rules verified against ground-truth corpus",
    )
    flagged_citations: list[str] = Field(
        default_factory=list,
        description="List of fabricated citations caught and removed",
    )
    hallucination_detected: bool = Field(
        default=False,
        description="True if ungrounded sections or fabricated case laws were detected",
    )
    warning_message: str | None = Field(
        default=None,
        description="User-facing notice if ungrounded statements were sanitized",
    )


# ==============================================================================
# Benchmark Evaluation Schema
# ==============================================================================


class EvalResult(BaseModel):
    """Execution telemetry and quality metric record for benchmark test cases."""

    model_config = ConfigDict(extra="ignore")

    scenario_id: str = Field(
        ...,
        description="Benchmark scenario identifier, e.g. 'scenario_1'",
    )
    scenario_title: str = Field(..., description="Descriptive scenario name")
    mode_name: str = Field(
        ...,
        description="Workflow mode tested (case_builder, advisor, drafter, simulator)",
    )
    provider: str = Field(..., description="LLM provider used for inference")
    model_name: str = Field(..., description="Model identifier used")
    is_successful: bool = Field(..., description="Whether workflow completed without failure")
    citations_verified_count: int = Field(
        default=0,
        description="Count of verified statutory citations",
    )
    hallucinations_count: int = Field(
        default=0,
        description="Count of hallucinated citations detected",
    )
    latency_seconds: float = Field(
        default=0.0,
        description="End-to-end execution latency in seconds",
    )
    tokens_used: int = Field(
        default=0,
        description="Total tokens consumed (prompt + completion)",
    )
    output_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Structured output payload",
    )
    evaluation_notes: str = Field(
        default="",
        description="Evaluator remarks and observations",
    )


# ==============================================================================
# Statutory Calculation Functions
# ==============================================================================


def determine_pecuniary_forum(amount: float) -> tuple[str, str]:
    """Determine the competent Consumer Commission forum under 2021 Pecuniary Rules.

    Strictly enforces 2021 Pecuniary Rules based exclusively on the value of
    goods or services paid as consideration (NOT aggregate damages or compensation):
    - District Commission: Consideration paid <= ₹50 Lakhs (₹5,000,000).
    - State Commission: Consideration paid > ₹50 Lakhs and <= ₹2 Crores (₹20,000,000).
    - National Commission: Consideration paid > ₹2 Crores (> ₹20,000,000).

    Args:
        amount: Value of goods or services paid as consideration in INR.

    Returns:
        tuple[str, str]: (Forum name, statutory rationale citing 2021 Pecuniary Rules).
    """
    if amount <= 5_000_000.0:
        return (
            PecuniaryForum.DISTRICT_COMMISSION.value,
            (
                f"Value of consideration paid (₹{amount:,.2f}) does not exceed ₹50 Lakhs. "
                "Jurisdiction lies with the District Consumer Disputes Redressal Commission "
                "under Rule 3 of the Consumer Protection (Jurisdiction of the District "
                "Commission, the State Commission and the National Commission) Rules, 2021."
            ),
        )
    if amount <= 20_000_000.0:
        return (
            PecuniaryForum.STATE_COMMISSION.value,
            (
                f"Value of consideration paid (₹{amount:,.2f}) exceeds ₹50 Lakhs but "
                "does not exceed ₹2 Crores. Jurisdiction lies with the State Consumer "
                "Disputes Redressal Commission under Rule 4 of the Consumer Protection "
                "(Jurisdiction of the District Commission, the State Commission and the "
                "National Commission) Rules, 2021."
            ),
        )
    return (
        PecuniaryForum.NATIONAL_COMMISSION.value,
        (
            f"Value of consideration paid (₹{amount:,.2f}) exceeds ₹2 Crores. "
            "Jurisdiction lies with the National Consumer Disputes Redressal Commission "
            "(NCDRC) under Rule 5 of the Consumer Protection (Jurisdiction of the District "
            "Commission, the State Commission and the National Commission) Rules, 2021."
        ),
    )


def calculate_edaakhil_fee(amount: float) -> int:
    """Calculate official statutory e-Daakhil filing fee under Consumer Protection Regulations.

    Official fee slabs:
    - Up to ₹5 Lakhs (₹500,000): ₹0 (Nil)
    - Above ₹5 Lakhs up to ₹10 Lakhs: ₹200
    - Above ₹10 Lakhs up to ₹20 Lakhs: ₹400
    - Above ₹20 Lakhs up to ₹50 Lakhs: ₹1,000
    - Above ₹50 Lakhs up to ₹1 Crore: ₹2,000
    - Above ₹1 Crore up to ₹2 Crores: ₹2,500
    - Above ₹2 Crores up to ₹4 Crores: ₹3,000
    - Above ₹4 Crores up to ₹6 Crores: ₹4,000
    - Above ₹6 Crores up to ₹8 Crores: ₹5,000
    - Above ₹8 Crores up to ₹10 Crores: ₹6,000
    - Above ₹10 Crores: ₹7,500

    Args:
        amount: Total value of consideration paid in INR.

    Returns:
        int: Statutory filing fee in INR payable on e-Daakhil.
    """
    if amount <= 500_000.0:
        return 0
    if amount <= 1_000_000.0:
        return 200
    if amount <= 2_000_000.0:
        return 400
    if amount <= 5_000_000.0:
        return 1000
    if amount <= 10_000_000.0:
        return 2000
    if amount <= 20_000_000.0:
        return 2500
    if amount <= 40_000_000.0:
        return 3000
    if amount <= 60_000_000.0:
        return 4000
    if amount <= 80_000_000.0:
        return 5000
    if amount <= 100_000_000.0:
        return 6000
    return 7500


def check_limitation_status(
    cause_of_action_date: str | date | datetime | int,
    filing_date: str | date | datetime | None = None,
) -> tuple[bool, int, str]:
    """Check statutory limitation status under Section 69 CPA 2019 (2-year limit = 730 days).

    Section 69(1) of CPA 2019 prescribes a strict limitation period of 2 years
    (730 days) from the date on which the cause of action arose. Section 69(2) allows
    admission after 2 years only if sufficient cause is shown for the delay.

    Args:
        cause_of_action_date: Date cause of action arose (string 'YYYY-MM-DD', date/datetime,
            or integer representing days elapsed).
        filing_date: Proposed filing date (string 'YYYY-MM-DD', date/datetime, or None for today).

    Returns:
        tuple[bool, int, str]: (is_within_limitation, days_remaining, rationale).
            - is_within_limitation: True if filed within 730 days, False if barred.
            - days_remaining: Days remaining before limitation expiry (negative if expired).
            - rationale: Detailed legal explanation citing Section 69.
    """
    if isinstance(cause_of_action_date, int):
        days_elapsed = cause_of_action_date
    else:
        coa_dt: date
        if isinstance(cause_of_action_date, str):
            coa_dt = date.fromisoformat(cause_of_action_date.strip())
        elif isinstance(cause_of_action_date, datetime):
            coa_dt = cause_of_action_date.date()
        else:
            coa_dt = cause_of_action_date

        filing_dt: date
        if filing_date is None:
            filing_dt = date.today()
        elif isinstance(filing_date, str):
            filing_dt = date.fromisoformat(filing_date.strip())
        elif isinstance(filing_date, datetime):
            filing_dt = filing_date.date()
        else:
            filing_dt = filing_date

        days_elapsed = (filing_dt - coa_dt).days

    days_remaining = 730 - days_elapsed
    is_within = days_elapsed <= 730

    if days_elapsed <= 600:
        rationale = (
            f"Complaint is well within the 2-year limitation period under Section 69(1) "
            f"of CPA 2019 ({days_elapsed} days elapsed, {days_remaining} days remaining)."
        )
    elif days_elapsed <= 730:
        rationale = (
            f"URGENT: Limitation period is expiring soon ({days_elapsed} of 730 days elapsed, "
            f"only {days_remaining} days remaining). "
            f"File e-Daakhil complaint promptly under Section 69(1)."
        )
    else:
        rationale = (
            f"Statutory 2-year limitation period under Section 69(1) of CPA 2019 has expired "
            f"({days_elapsed} days elapsed, exceeded by {-days_remaining} days). "
            "Under Section 69(2), an application for condonation of delay must be filed "
            "demonstrating sufficient cause."
        )

    return is_within, days_remaining, rationale
