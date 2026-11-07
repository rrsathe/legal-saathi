"""Mode 1: Case Builder (Fact Intake, Entity & Timeline Extraction).

Ingests unstructured consumer narratives in English, Hindi, or Hinglish, executes
structured LLM extraction conforming to the CaseFile schema, standardizes chronological
timeline events, audits evidentiary sufficiency (present vs missing proof), and generates
targeted follow-up questions to resolve legal ambiguities under the Consumer Protection Act, 2019.
"""

from __future__ import annotations

import logging
import re
import uuid
from datetime import date
from typing import Any

from legal_assistant.llm.prompts import (
    CASE_BUILDER_SYSTEM_PROMPT,
    format_case_builder_prompt,
)
from legal_assistant.llm.router import LLMRouter
from legal_assistant.schemas import (
    CaseFile,
    EvidenceItem,
    MissingEvidence,
    OppositeParty,
    PartyDetails,
    ScopeResult,
    TimelineEvent,
)

logger = logging.getLogger(__name__)


class OutOfScopeDisputeError(ValueError):
    """Raised when a narrative is classified as outside consumer commission jurisdiction."""

    def __init__(self, message: str, scope_result: ScopeResult | None = None) -> None:
        """Initialize error with message and optional ScopeResult payload.

        Args:
            message: Explanation of jurisdictional exclusion.
            scope_result: Optional structured ScopeResult from pre-retrieval guardrail.
        """
        super().__init__(message)
        self.scope_result = scope_result


class CaseBuilder:
    """Mode 1: Fact Intake, Entity Extraction & Structured Case Construction.

    Analyzes conversational consumer narratives (in English, Hindi, or Hinglish),
    validates jurisdictional scope, extracts chronological dispute facts into a Pydantic
    CaseFile, audits available vs missing documentary proof, and identifies critical
    ambiguities requiring user clarification.
    """

    def __init__(
        self,
        llm_router: LLMRouter | None = None,
        scope_checker: Any | None = None,
    ) -> None:
        """Initialize CaseBuilder workflow.

        Args:
            llm_router: Optional custom or configured LLMRouter instance.
                If None, instantiates a default router from settings.
            scope_checker: Optional ScopeChecker instance for pre-retrieval
                jurisdictional filtering.
        """
        self.router = llm_router or LLMRouter()
        self.scope_checker = scope_checker

    def build_case(
        self,
        narrative: str,
        complainant_details: PartyDetails | None = None,
        provider: str | None = None,
        use_llm: bool = True,
    ) -> CaseFile:
        """Analyze unstructured consumer narrative and generate structured CaseFile.

        Args:
            narrative: Raw narrative text in English, Hindi, or Hinglish.
            complainant_details: Optional pre-populated Complainant details.
            provider: Optional LLM provider name override (e.g. 'groq', 'ollama').
            use_llm: Whether to attempt LLM extraction. Defaults to True.

        Returns:
            Validated CaseFile instance populated with parties, timeline, and evidence audit.

        Raises:
            ValueError: If narrative is empty or contains only whitespace.
            OutOfScopeDisputeError: If narrative falls outside consumer protection scope.
        """
        cleaned_narrative = narrative.strip()
        if not cleaned_narrative:
            raise ValueError("Dispute narrative cannot be empty.")

        # 1. Pre-retrieval jurisdictional scope check
        if self.scope_checker is not None:
            scope_res: ScopeResult = self.scope_checker.check_scope(cleaned_narrative)
            if not scope_res.is_in_scope:
                advice = (
                    scope_res.escalation_advice
                    or "Dispute falls outside consumer commission jurisdiction."
                )
                logger.warning(
                    "Narrative filtered by scope checker: category=%s",
                    scope_res.out_of_scope_category,
                )
                raise OutOfScopeDisputeError(advice, scope_result=scope_res)

        # 2. Format structured intake prompt and attempt LLM extraction
        case_file: CaseFile | None = None
        if use_llm:
            try:
                prompt = format_case_builder_prompt(cleaned_narrative, CaseFile)
                provider_order = [provider] if provider else None
                case_file = self.router.generate_structured_with_fallback(
                    prompt=prompt,
                    schema=CaseFile,
                    system_prompt=CASE_BUILDER_SYSTEM_PROMPT,
                    provider_order=provider_order,
                )
            except Exception as exc:
                logger.info(
                    "LLM extraction unavailable or failed: %s. Using deterministic extractor.",
                    exc,
                )
                case_file = self._extract_deterministic(cleaned_narrative, complainant_details)
        else:
            case_file = self._extract_deterministic(cleaned_narrative, complainant_details)

        # 3. Reconcile explicit complainant details if provided
        if complainant_details is not None:
            case_file = self._merge_complainant_details(case_file, complainant_details)

        # 4. Ensure at least one Opposite Party exists
        if not case_file.opposite_parties:
            case_file.opposite_parties.append(
                OppositeParty(
                    name="Opposite Party (Merchant / Platform)",
                    role="E-Commerce Marketplace",
                    entity_type="marketplace",
                )
            )

        # 5. Execute evidentiary sufficiency audit
        supplemental_missing = self.audit_missing_evidence(case_file)
        existing_missing_names = {item.item_name.lower() for item in case_file.missing_evidence}
        for missing in supplemental_missing:
            if missing.item_name.lower() not in existing_missing_names:
                case_file.missing_evidence.append(missing)

        # 6. Auto-tag case for downstream RAG and classification
        case_file = self._enrich_tags(case_file)

        return case_file

    def update_case_with_clarifications(
        self,
        case_file: CaseFile,
        clarification_answers: dict[str, str],
        provider: str | None = None,
    ) -> CaseFile:
        """Refine an existing CaseFile with user responses to clarifying questions.

        Args:
            case_file: Existing CaseFile instance.
            clarification_answers: Dictionary mapping clarification questions to user answers.
            provider: Optional LLM provider name override.

        Returns:
            Updated CaseFile with resolved ambiguities, refined timeline, and updated facts.
        """
        if not clarification_answers:
            return case_file

        qa_pairs = "\n".join(
            f"Q: {q}\nA: {a}" for q, a in clarification_answers.items() if a.strip()
        )
        if not qa_pairs:
            return case_file

        update_prompt = f"""\
You are updating an existing consumer CaseFile with new factual answers provided by the consumer.

EXISTING CASE FACTS:
Title: {case_file.title}
Transaction Date: {case_file.transaction_date}
Disputed Amount: INR {case_file.disputed_amount_inr}
Summary: {case_file.facts_summary}

NEW CLARIFICATION ANSWERS FROM CONSUMER:
\"\"\"
{qa_pairs}
\"\"\"

TASK:
1. Merge these factual answers into the facts_summary and timeline.
2. If commercial resale vs personal use was clarified, record personal use explicitly.
3. Remove answered clarification questions from clarification_questions.
4. Output the complete updated CaseFile JSON conforming strictly to schema.
"""
        provider_order = [provider] if provider else None
        try:
            updated_case: CaseFile = self.router.generate_structured_with_fallback(
                prompt=update_prompt,
                schema=CaseFile,
                system_prompt=CASE_BUILDER_SYSTEM_PROMPT,
                provider_order=provider_order,
            )
            # Preserve original case ID and creation timestamp
            updated_case.case_id = case_file.case_id
            updated_case.created_at = case_file.created_at
            return updated_case
        except Exception as exc:
            logger.info("LLM clarification update failed: %s. Merging deterministically.", exc)
            case_file.facts_summary = (
                f"{case_file.facts_summary}\n\nAdditional Clarifications:\n{qa_pairs}"
            )
            return case_file

    def audit_missing_evidence(self, case_file: CaseFile) -> list[MissingEvidence]:
        """Audit case facts and identify essential missing proofs required under CPA 2019.

        Args:
            case_file: CaseFile instance to audit.

        Returns:
            list[MissingEvidence]: List of essential missing evidentiary proofs.
        """
        present_names = " ".join(
            item.item_name.lower() + " " + item.description.lower()
            for item in case_file.evidence_checklist
        )
        facts_lower = case_file.facts_summary.lower()
        missing: list[MissingEvidence] = []

        # 1. Tax Invoice audit
        if "invoice" not in present_names and "bill" not in present_names:
            missing.append(
                MissingEvidence(
                    item_name="Tax Invoice with GSTIN & Serial Number",
                    importance="critical",
                    why_needed=(
                        "Mandatory proof of purchase, consideration paid, and seller identity "
                        "under Section 2(7) CPA 2019 and Rule 5(2) of the E-Commerce Rules, 2020."
                    ),
                    where_to_obtain=(
                        "Download tax invoice from the platform 'My Orders' section or request "
                        "an itemized duplicate tax invoice directly from the seller."
                    ),
                )
            )

        # 2. Payment confirmation audit
        if not any(
            k in present_names
            for k in ("payment", "upi", "bank statement", "transaction slip", "card receipt")
        ):
            missing.append(
                MissingEvidence(
                    item_name="Electronic Payment Receipt / Bank Statement",
                    importance="high",
                    why_needed=(
                        "Establishes conclusive payment of valuable consideration and exact date "
                        "of transaction to prove consumer standing under Section 2(7) CPA 2019."
                    ),
                    where_to_obtain=(
                        "Bank netbanking portal, UPI app transaction history, "
                        "or credit card statement."
                    ),
                )
            )

        # 3. Continuous unboxing video audit (for wrong/missing/tampered items)
        is_tampered_or_wrong = any(
            k in facts_lower
            for k in (
                "sabun",
                "soap",
                "dummy",
                "wrong item",
                "empty box",
                "counterfeit",
                "fake",
                "tampered",
                "missing item",
            )
        )
        if is_tampered_or_wrong and "unboxing" not in present_names:
            missing.append(
                MissingEvidence(
                    item_name="Continuous Unboxing Video from Seal to Content",
                    importance="high",
                    why_needed=(
                        "E-commerce platforms routinely deny refund requests alleging "
                        "post-delivery tampering. An uncut unboxing video rebuts "
                        "delivery integrity objections."
                    ),
                    where_to_obtain=(
                        "Self-recorded continuous unboxing footage. If unavailable, photograph "
                        "the shipping label, outer package barcode, and received contents."
                    ),
                )
            )

        # 4. Rejection record / Grievance ticket audit
        if not any(
            k in present_names
            for k in ("email", "grievance", "ticket", "rejection", "support chat", "job sheet")
        ):
            missing.append(
                MissingEvidence(
                    item_name="Customer Support Denial Trail / Grievance Ticket Number",
                    importance="high",
                    why_needed=(
                        "Proves cause of action date under Section 69 CPA 2019 and establishes "
                        "platform failure to acknowledge within 48h / resolve within 30d under "
                        "Rule 4(5) of the E-Commerce Rules, 2020."
                    ),
                    where_to_obtain=(
                        "Platform customer support chat logs, helpdesk email responses, "
                        "or SMS alerts."
                    ),
                )
            )

        # 5. Technical defect audit (for electronic/mechanical appliances)
        is_electronic_defect = any(
            k in facts_lower
            for k in (
                "phone",
                "laptop",
                "mobile",
                "television",
                "tv",
                "appliance",
                "refrigerator",
                "motherboard",
                "display defect",
                "cracked",
            )
        )
        has_service_proof = "job sheet" in present_names or "service center" in present_names
        if is_electronic_defect and not has_service_proof:
            missing.append(
                MissingEvidence(
                    item_name="Authorized Service Center Job Sheet / Inspection Report",
                    importance="critical",
                    why_needed=(
                        "Statutory proof of manufacturing defect under Section 2(10) CPA 2019 "
                        "to rebut merchant claims of user-induced physical or liquid damage."
                    ),
                    where_to_obtain=(
                        "Visit brand's authorized service center and obtain an official "
                        "stamped job sheet."
                    ),
                )
            )

        return missing

    def _extract_deterministic(
        self,
        narrative: str,
        complainant_details: PartyDetails | None = None,
    ) -> CaseFile:
        """Deterministic regex and keyword parser used when LLM is offline or unavailable."""
        # 1. Amount Extraction
        amount = 0.0
        amount_match = re.search(
            r"(?:₹|rs\.?|inr)\s*([\d,]+(?:\.\d+)?)|([\d,]+(?:\.\d+)?)\s*(?:₹|rs\.?|inr|rupees|/-)",
            narrative,
            re.IGNORECASE,
        )
        if amount_match:
            raw_amt = amount_match.group(1) or amount_match.group(2)
            if raw_amt:
                try:
                    amount = CaseFile.parse_inr_amount(raw_amt)
                except Exception:
                    amount = 0.0

        # 2. Date Extraction
        tx_date = date.today().isoformat()
        iso_date_match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", narrative)
        if iso_date_match:
            tx_date = iso_date_match.group(1)
        else:
            # Common date strings e.g. "15 Jan 2024", "15 January 2024", "5 Jan"
            date_match = re.search(
                r"\b(\d{1,2})\s+(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)(?:\s+(\d{4}))?\b",
                narrative,
                re.IGNORECASE,
            )
            if date_match:
                day = int(date_match.group(1))
                mon_str = date_match.group(2).lower()[:3]
                year = int(date_match.group(3)) if date_match.group(3) else 2024
                month_map = {
                    "jan": 1,
                    "feb": 2,
                    "mar": 3,
                    "apr": 4,
                    "may": 5,
                    "jun": 6,
                    "jul": 7,
                    "aug": 8,
                    "sep": 9,
                    "oct": 10,
                    "nov": 11,
                    "dec": 12,
                }
                m = month_map.get(mon_str, 1)
                tx_date = f"{year:04d}-{m:02d}-{day:02d}"

        # 3. Complainant Name & Contact
        comp_name = "Complainant"
        name_match = re.search(
            r"\b(?:name\s+is|naam\s+hai|i\s+am)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\b",
            narrative,
            re.IGNORECASE,
        )
        if name_match:
            comp_name = name_match.group(1).strip()

        email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", narrative)
        email = email_match.group(0) if email_match else None

        phone_match = re.search(r"\b(?:\+91[-\s]?)?[6-9]\d{9}\b", narrative)
        phone = phone_match.group(0) if phone_match else None

        city = None
        for c in [
            "Delhi",
            "New Delhi",
            "Mumbai",
            "Bengaluru",
            "Kolkata",
            "Chennai",
            "Hyderabad",
            "Pune",
        ]:
            if re.search(rf"\b{c}\b", narrative, re.IGNORECASE):
                city = c
                break

        complainant = PartyDetails(
            name=comp_name,
            email=email,
            phone=phone,
            city=city,
            state="Delhi" if city and "delhi" in city.lower() else None,
            role="Complainant",
            party_type="individual",
        )

        # 4. Opposite Parties
        opposite_parties: list[OppositeParty] = []
        lower_narrative = narrative.lower()

        if "flipkart" in lower_narrative:
            opposite_parties.append(
                OppositeParty(
                    name="Flipkart Internet Private Limited",
                    role="E-Commerce Marketplace",
                    address=(
                        "Buildings Alyssa, Begonia & Clover, Embassy Tech Village, "
                        "Bengaluru, Karnataka"
                    ),
                    entity_type="marketplace",
                )
            )
        elif "amazon" in lower_narrative:
            opposite_parties.append(
                OppositeParty(
                    name="Amazon Seller Services Private Limited",
                    role="E-Commerce Marketplace",
                    address=(
                        "8th Floor, Brigade Gateway, 26/1 Dr. Rajkumar Road, "
                        "Malleshwaram, Bengaluru"
                    ),
                    entity_type="marketplace",
                )
            )
        elif "zomato" in lower_narrative:
            opposite_parties.append(
                OppositeParty(
                    name="Zomato Limited",
                    role="Online Food Delivery Platform",
                    address="Ground Floor, 12A, 94 Meghdoot, Nehru Place, New Delhi",
                    entity_type="marketplace",
                )
            )
        elif "swiggy" in lower_narrative:
            opposite_parties.append(
                OppositeParty(
                    name="Bundl Technologies Private Limited (Swiggy)",
                    role="Online Food Delivery Platform",
                    address="Devarabisanahalli, Bengaluru, Karnataka",
                    entity_type="marketplace",
                )
            )
        else:
            opposite_parties.append(
                OppositeParty(
                    name="Opposite Party (Merchant / Platform)",
                    role="E-Commerce Marketplace",
                    entity_type="marketplace",
                )
            )

        # 5. Timeline Events
        timeline: list[TimelineEvent] = [
            TimelineEvent(
                date=tx_date,
                description="Transaction entered and consideration paid for goods/services.",
                significance="Purchase date establishing consumer standing under Section 2(7)",
            ),
        ]
        if "reject" in lower_narrative or "refus" in lower_narrative or "deni" in lower_narrative:
            timeline.append(
                TimelineEvent(
                    date=tx_date,
                    description="Opposite party customer support refused refund or return request.",
                    significance="Cause of action arose under Section 69",
                )
            )

        # 6. Evidence Checklist
        evidence_checklist: list[EvidenceItem] = []
        if "invoice" in lower_narrative or "inv-" in lower_narrative or "bill" in lower_narrative:
            evidence_checklist.append(
                EvidenceItem(
                    item_name="Tax Invoice",
                    category="documentary",
                    description="Tax invoice / bill issued by seller for purchase.",
                    is_available=True,
                )
            )
        if "delivery slip" in lower_narrative or "slip" in lower_narrative:
            evidence_checklist.append(
                EvidenceItem(
                    item_name="Delivery Slip",
                    category="documentary",
                    description="Delivery receipt / courier acknowledgment slip.",
                    is_available=True,
                )
            )
        if "unboxing video" in lower_narrative:
            # If user said "do not have unboxing video"
            has_no_video = bool(
                re.search(
                    r"\b(?:not?|nahi)\s+have\s+an?\s+unboxing\s+video\b|\bdo\s+not\s+have\s+an?\s+unboxing\s+video\b",
                    lower_narrative,
                )
            )
            if not has_no_video:
                evidence_checklist.append(
                    EvidenceItem(
                        item_name="Unboxing Video",
                        category="digital_media",
                        description="Continuous unboxing video.",
                        is_available=True,
                    )
                )

        # Determine Title
        title = "Consumer Dispute regarding Goods / Services"
        if "laptop" in lower_narrative:
            title = "Defective Laptop Refund Refusal Dispute"
        elif "phone" in lower_narrative or "smartphone" in lower_narrative:
            title = "Defective Smartphone Delivery and Refund Refusal"
        elif "mixer" in lower_narrative:
            title = "Damaged Mixer Grinder Return Refusal"

        return CaseFile(
            case_id=f"case_{uuid.uuid4().hex[:8]}",
            title=title,
            complainant=complainant,
            opposite_parties=opposite_parties,
            transaction_date=tx_date,
            cause_of_action_date=tx_date,
            disputed_amount_inr=amount,
            compensation_claimed_inr=25000.0,
            facts_summary=narrative,
            timeline=timeline,
            evidence_checklist=evidence_checklist,
            missing_evidence=[],
            clarification_questions=[],
            tags=["consumer_dispute"],
        )

    def _merge_complainant_details(self, case_file: CaseFile, details: PartyDetails) -> CaseFile:
        """Merge provided complainant details into CaseFile complainant record."""
        c = case_file.complainant
        case_file.complainant = PartyDetails(
            name=details.name if details.name and details.name != "Complainant" else c.name,
            role="Complainant",
            address=details.address or c.address,
            email=details.email or c.email,
            phone=details.phone or c.phone,
            city=details.city or c.city,
            state=details.state or c.state,
            party_type="individual",
        )
        return case_file

    def _enrich_tags(self, case_file: CaseFile) -> CaseFile:
        """Enrich CaseFile tags with standard statutory and domain categories."""
        tags = set(case_file.tags)
        tags.add("consumer_protection_act_2019")
        facts_lower = case_file.facts_summary.lower()

        if any(p.entity_type == "marketplace" for p in case_file.opposite_parties) or any(
            m in facts_lower
            for m in (
                "flipkart",
                "amazon",
                "meesho",
                "myntra",
                "zepto",
                "blinkit",
                "zomato",
                "swiggy",
            )
        ):
            tags.add("ecommerce_rules_2020")
            tags.add("marketplace_dispute")

        if any(w in facts_lower for w in ("refund", "return", "rejected", "denied")):
            tags.add("refund_refusal")

        if any(
            w in facts_lower
            for w in ("defect", "broken", "dummy", "soap", "damaged", "fake", "cracked")
        ):
            tags.add("defective_goods")

        if any(w in facts_lower for w in ("support", "grievance", "delayed", "late delivery")):
            tags.add("deficiency_in_service")

        case_file.tags = sorted(tags)
        return case_file
