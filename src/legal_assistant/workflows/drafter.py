"""Mode 3: Automated Document Drafter.

Generates ready-to-send, professionally formatted consumer legal artifacts:
1. Grievance Escalation Email: Cites E-Commerce Rules 2020 (Rule 4(4)/4(5) Grievance Officer
   mandate, 48-hour ticket number, 30-day resolution deadline).
2. Formal Legal Demand Notice: Addressed to Seller & Marketplace, stating facts, statutory
   breaches (Sections 2(10), 2(11), 2(47)), 15-day peremptory deadline for refund with interest,
   and warning of e-Daakhil filing.
3. Consumer Complaint Draft for e-Daakhil: Formatted according to NCDRC/State/District
   Commission standards (Memo of Parties, Index, Statement of Facts, Statutory Grounds,
   Pecuniary & Territorial Jurisdiction, Limitation, Prayer, and Verification Affidavit).
"""

from __future__ import annotations

import logging
import uuid
from datetime import date
from typing import TypeVar

from legal_assistant.llm.prompts import DRAFTER_SYSTEM_PROMPT
from legal_assistant.llm.router import LLMRouter
from legal_assistant.rag.hybrid_retriever import StatutoryHybridRetriever
from legal_assistant.schemas import (
    CaseFile,
    Citation,
    DocumentType,
    DraftedDocument,
    LegalNotice,
    LegalStanding,
    calculate_edaakhil_fee,
    determine_pecuniary_forum,
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=DraftedDocument)


class DraftDocument(DraftedDocument):
    """Compatibility subclass supporting doc_type and content_markdown aliases.

    Provides field name interoperability across both 'DraftedDocument' and
    'DraftDocument' specifications.
    """

    @property
    def doc_type(self) -> str:
        """Alias for document_type."""
        return self.document_type

    @property
    def content_markdown(self) -> str:
        """Alias for body_markdown."""
        return self.body_markdown


class DocumentDrafter:
    """Mode 3: Automated Legal Artifact Drafter for Indian Consumer Disputes.

    Drafts ready-to-dispatch, statutory-grounded legal documents populated with
    dispute facts, verified sections from CPA 2019 and E-Commerce Rules 2020,
    and court-compliant procedural clauses.
    """

    def __init__(
        self,
        llm_router: LLMRouter | None = None,
        retriever: StatutoryHybridRetriever | None = None,
    ) -> None:
        """Initialize DocumentDrafter.

        Args:
            llm_router: Optional custom or configured LLMRouter instance.
            retriever: Optional StatutoryHybridRetriever instance.
        """
        self.router = llm_router or LLMRouter()
        self.retriever = retriever

    def draft_document(
        self,
        case_file: CaseFile,
        doc_type: DocumentType | str,
        standing: LegalStanding | None = None,
        provider: str | None = None,
        use_llm: bool = True,
    ) -> DraftedDocument:
        """Draft a single requested legal artifact by type.

        Args:
            case_file: Structured CaseFile containing dispute facts and parties.
            doc_type: Target document type ('grievance_email', 'legal_notice',
                'edaakhil_complaint').
            standing: Optional LegalStanding analysis from Mode 2.
            provider: Optional LLM provider name override.
            use_llm: Whether to invoke LLM for dynamic drafting (defaults to True;
                falls back to deterministic legal templates on failure or when False).

        Returns:
            DraftedDocument instance.

        Raises:
            ValueError: If doc_type is unrecognized.
        """
        clean_type = str(doc_type).lower().strip()

        if clean_type in (DocumentType.GRIEVANCE_EMAIL.value, "grievance_email"):
            return self.draft_grievance_email(
                case_file=case_file,
                standing=standing,
                provider=provider,
                use_llm=use_llm,
            )
        if clean_type in (DocumentType.LEGAL_NOTICE.value, "legal_notice"):
            return self.draft_legal_notice(
                case_file=case_file,
                standing=standing,
                provider=provider,
                use_llm=use_llm,
            )
        if clean_type in (DocumentType.EDAAKHIL_COMPLAINT.value, "edaakhil_complaint"):
            return self.draft_edaakhil_complaint(
                case_file=case_file,
                standing=standing,
                provider=provider,
                use_llm=use_llm,
            )

        raise ValueError(
            f"Unsupported document type: '{doc_type}'. "
            f"Supported: grievance_email, legal_notice, edaakhil_complaint"
        )

    def draft_grievance_email(
        self,
        case_file: CaseFile,
        standing: LegalStanding | None = None,
        provider: str | None = None,
        use_llm: bool = True,
    ) -> DraftedDocument:
        """Draft a formal Grievance Escalation Email under E-Commerce Rules 2020.

        Cites Rule 4(4) (appointment of grievance officer), Rule 4(5) (48-hour
        acknowledgement mandate with ticket number, 30-day resolution deadline),
        and Rule 6(3)/7(4) (prohibition on refusal to refund for defective goods).

        Args:
            case_file: Structured CaseFile.
            standing: Optional LegalStanding result.
            provider: Optional LLM provider override.
            use_llm: Whether to attempt LLM generation.

        Returns:
            DraftedDocument configured for grievance email dispatch.
        """
        if use_llm:
            try:
                doc = self._draft_with_llm(
                    case_file=case_file,
                    doc_type="grievance_email",
                    schema=DraftedDocument,
                    standing=standing,
                    provider=provider,
                )
                if doc and doc.body_markdown and len(doc.body_markdown) > 100:
                    return doc
            except Exception as exc:
                logger.warning("LLM drafting failed for grievance email: %s. Using template.", exc)

        return self._build_grievance_email_template(case_file=case_file, standing=standing)

    def draft_legal_notice(
        self,
        case_file: CaseFile,
        standing: LegalStanding | None = None,
        notice_period_days: int = 15,
        provider: str | None = None,
        use_llm: bool = True,
    ) -> LegalNotice:
        """Draft a formal 15-Day Legal Demand Notice to Seller and Marketplace.

        Stating chronological transaction facts, specific statutory violations under
        CPA 2019 and E-Commerce Rules 2020, a peremptory 15-day deadline for full refund
        with 18% p.a. interest, mental agony compensation, and warning of e-Daakhil filing.

        Args:
            case_file: Structured CaseFile.
            standing: Optional LegalStanding result.
            notice_period_days: Notice window in days (default: 15).
            provider: Optional LLM provider override.
            use_llm: Whether to attempt LLM generation.

        Returns:
            LegalNotice instance.
        """
        if use_llm:
            try:
                doc = self._draft_with_llm(
                    case_file=case_file,
                    doc_type="legal_notice",
                    schema=LegalNotice,
                    standing=standing,
                    provider=provider,
                )
                if doc and doc.body_markdown and len(doc.body_markdown) > 150:
                    doc.notice_period_days = notice_period_days
                    doc.claim_amount_inr = (
                        case_file.disputed_amount_inr + case_file.compensation_claimed_inr
                    )
                    return doc
            except Exception as exc:
                logger.warning("LLM drafting failed for legal notice: %s. Using template.", exc)

        return self._build_legal_notice_template(
            case_file=case_file,
            standing=standing,
            notice_period_days=notice_period_days,
        )

    def draft_edaakhil_complaint(
        self,
        case_file: CaseFile,
        standing: LegalStanding | None = None,
        provider: str | None = None,
        use_llm: bool = True,
    ) -> DraftedDocument:
        """Draft a formal Consumer Complaint Petition formatted for e-Daakhil.

        Adheres strictly to NCDRC/e-Daakhil 7-part petition standards:
        Part I: Memo of Parties
        Part II: Index of Documents / Annexures
        Part III: Statement of Material Facts
        Part IV: Statutory Grounds of Claim
        Part V: Pecuniary & Territorial Jurisdiction Clauses
        Part VI: Limitation Statement (Section 69)
        Part VII: Prayer / Itemized Relief Sought
        Verification / Solemn Affirmation Clause.

        Args:
            case_file: Structured CaseFile.
            standing: Optional LegalStanding result.
            provider: Optional LLM provider override.
            use_llm: Whether to attempt LLM generation.

        Returns:
            DraftedDocument configured for e-Daakhil filing.
        """
        if use_llm:
            try:
                doc = self._draft_with_llm(
                    case_file=case_file,
                    doc_type="edaakhil_complaint",
                    schema=DraftedDocument,
                    standing=standing,
                    provider=provider,
                )
                if doc and doc.body_markdown and len(doc.body_markdown) > 200:
                    return doc
            except Exception as exc:
                logger.warning(
                    "LLM drafting failed for e-Daakhil complaint: %s. Using template.", exc
                )

        return self._build_edaakhil_complaint_template(case_file=case_file, standing=standing)

    def draft_all(
        self,
        case_file: CaseFile,
        standing: LegalStanding | None = None,
        provider: str | None = None,
        use_llm: bool = True,
    ) -> dict[str, DraftedDocument]:
        """Draft all 3 core legal artifacts for a comprehensive consumer package.

        Args:
            case_file: Structured CaseFile.
            standing: Optional LegalStanding result.
            provider: Optional LLM provider override.
            use_llm: Whether to attempt LLM generation.

        Returns:
            dict[str, DraftedDocument]: Dictionary containing:
                - 'grievance_email': DraftedDocument
                - 'legal_notice': LegalNotice
                - 'edaakhil_complaint': DraftedDocument
        """
        return {
            "grievance_email": self.draft_grievance_email(
                case_file=case_file, standing=standing, provider=provider, use_llm=use_llm
            ),
            "legal_notice": self.draft_legal_notice(
                case_file=case_file, standing=standing, provider=provider, use_llm=use_llm
            ),
            "edaakhil_complaint": self.draft_edaakhil_complaint(
                case_file=case_file, standing=standing, provider=provider, use_llm=use_llm
            ),
        }

    # ==========================================================================
    # Internal Helpers: LLM Invocation & Deterministic Templates
    # ==========================================================================

    def _draft_with_llm(
        self,
        case_file: CaseFile,
        doc_type: str,
        schema: type[T],
        standing: LegalStanding | None = None,
        provider: str | None = None,
    ) -> T:
        """Execute structured LLM generation for a document artifact."""
        opp_parties_str = "\n".join(
            f"- {p.role}: {p.name} ({p.address or 'Address on file'})"
            for p in case_file.opposite_parties
        )

        prompt = f"""\
You are an expert Indian Consumer Litigation Drafter.
Draft a complete, court-ready {doc_type} based on the following case facts:

CASE DETAILS:
Title: {case_file.title}
Transaction Date: {case_file.transaction_date}
Disputed Consideration: INR {case_file.disputed_amount_inr}
Compensation Claimed: INR {case_file.compensation_claimed_inr}
Complainant: {case_file.complainant.name}, {case_file.complainant.city or "India"}
Opposite Parties:
{opp_parties_str}

STATEMENT OF FACTS:
{case_file.facts_summary}

REQUIRED DOCUMENT TYPE: {doc_type}
Ensure all statutory sections under the Consumer Protection Act, 2019 and the
Consumer Protection (E-Commerce) Rules, 2020 are correctly referenced in the markdown body.
"""
        provider_order = [provider] if provider else None
        return self.router.generate_structured_with_fallback(
            prompt=prompt,
            schema=schema,
            system_prompt=DRAFTER_SYSTEM_PROMPT,
            provider_order=provider_order,
        )

    def _build_grievance_email_template(
        self,
        case_file: CaseFile,
        standing: LegalStanding | None = None,
    ) -> DraftDocument:
        """Construct deterministic Grievance Escalation Email template."""
        today_str = date.today().isoformat()
        platform_party = next(
            (
                p
                for p in case_file.opposite_parties
                if "marketplace" in p.entity_type or "platform" in p.role.lower()
            ),
            case_file.opposite_parties[0],
        )
        seller_party = next(
            (p for p in case_file.opposite_parties if "seller" in p.role.lower()),
            case_file.opposite_parties[0],
        )

        platform_domain = (
            "flipkart.com"
            if "flipkart" in platform_party.name.lower()
            else "amazon.in"
            if "amazon" in platform_party.name.lower()
            else "ecommerce-platform.in"
        )
        email_addr = f"grievance-officer@{platform_domain}"

        subject = (
            f"FORMAL ESCALATION: Grievance under Rule 4(5) of Consumer Protection "
            f"(E-Commerce) Rules, 2020 - Order regarding {case_file.title}"
        )

        citations = [
            Citation(
                statute="Consumer Protection (E-Commerce) Rules, 2020",
                section="Rule 4(4) & Rule 4(5)",
                title="Grievance Redressal Mechanism & Nodal Officer",
                text_excerpt=(
                    "Mandatory appointment of Grievance Officer; 48-hour acknowledgement "
                    "and 30-day redressed resolution."
                ),
                is_verified=True,
            ),
            Citation(
                statute="Consumer Protection (E-Commerce) Rules, 2020",
                section="Rule 6(3)",
                title="Duties of Sellers & Prohibition of Return Refusal",
                text_excerpt=(
                    "No seller on marketplace shall refuse to take back goods or refund "
                    "consideration if goods are defective, deficient, or spurious."
                ),
                is_verified=True,
            ),
            Citation(
                statute="Consumer Protection Act, 2019",
                section="Section 2(11)",
                title="Deficiency in Service",
                text_excerpt=(
                    "Any fault, imperfection, shortcoming or inadequacy in the quality, "
                    "nature and manner of performance."
                ),
                is_verified=True,
            ),
        ]

        c_contact = (
            f"{case_file.complainant.phone or 'Phone on record'}, "
            f"{case_file.complainant.email or 'Email on record'}"
        )

        body_markdown = f"""\
**TO**: Grievance Redressal Officer, {platform_party.name}
**EMAIL**: {email_addr}
**DATE**: {today_str}
**SUBJECT**: {subject}

Dear Grievance Officer,

I am writing to formally lodge a statutory consumer grievance pursuant to \
**Rule 4(4) and Rule 4(5) of the Consumer Protection (E-Commerce) Rules, 2020** \
regarding a transaction conducted on your platform.

### 1. TRANSACTION DETAILS
- **Complainant / Buyer**: {case_file.complainant.name} ({c_contact})
- **Transaction / Order Date**: {case_file.transaction_date}
- **Item / Service Purchased**: {case_file.title}
- **Valuable Consideration Paid**: ₹{case_file.disputed_amount_inr:,.2f}
- **Opposite Party Seller**: {seller_party.name}
- **Opposite Party Marketplace**: {platform_party.name}

### 2. FACTUAL SUMMARY OF GRIEVANCE
{case_file.facts_summary}

Despite bringing this matter to the attention of customer support, \
my legitimate request for refund / replacement was unlawfully denied.

### 3. STATUTORY BREACHES
1. **Rule 4(5)(b) & (c), Consumer Protection (E-Commerce) Rules, 2020**: \
Mandatory statutory obligation of the Grievance Officer to acknowledge receipt \
within forty-eight (48) hours with a ticket number, and redress within thirty (30) days.
2. **Rule 6(3) & Rule 7(4), Consumer Protection (E-Commerce) Rules, 2020**: \
Absolute prohibition against refusal to refund consideration paid or take back \
goods that are defective, deficient, or spurious.
3. **Section 2(11), Consumer Protection Act, 2019**: \
Gross deficiency in service by failing to deliver goods as represented and \
denying legitimate post-sale remedy.

### 4. FORMAL DEMANDS
Pursuant to the mandatory statutory framework, you are hereby called upon to:
1. **Acknowledge this grievance within forty-eight (48) hours** from receipt and \
issue an official Complaint Ticket Number.
2. **Initiate and credit a full refund of ₹{case_file.disputed_amount_inr:,.2f}** \
to my original payment source within **seven (7) working days**.
3. **Provide full written resolution** within thirty (30) days as mandated under Rule 4(5)(c).

Please be advised that failure to resolve this complaint within the statutory window \
will constrain me to escalate this matter to the **National Consumer Helpline (NCH 1915)**, \
register a formal complaint with the **Central Consumer Protection Authority (CCPA)** \
under Section 18 of CPA 2019, and institute legal proceedings before the competent \
Consumer Commission via **e-Daakhil (`edaakhil.nic.in`)**, claiming full refund with \
18% interest, compensation for mental agony, and litigation expenses.

Yours faithfully,

**{case_file.complainant.name}**
{case_file.complainant.address or "Address on record"}
Email: {case_file.complainant.email or "Email on file"} | \
Phone: {case_file.complainant.phone or "Phone on file"}
"""
        return DraftDocument(
            document_id=f"doc_{uuid.uuid4().hex[:8]}",
            document_type="grievance_email",
            title=f"Grievance Escalation Email under Rule 4(5) - {case_file.title}",
            recipient=f"Grievance Officer, {platform_party.name} ({email_addr})",
            subject=subject,
            body_markdown=body_markdown,
            statutory_citations=citations,
            verification_statement=None,
            annexure_list=[
                "Annexure 1: Tax Invoice & Payment Receipt",
                "Annexure 2: Customer Support Denial Chat / Email",
                "Annexure 3: Photographic / Unboxing Proof",
            ],
            demand_summary=(
                f"Full refund of ₹{case_file.disputed_amount_inr:,.2f} within 7 days "
                "and 48-hr ticket number."
            ),
            response_deadline_days=2,
            metadata={
                "platform": platform_party.name,
                "amount_inr": case_file.disputed_amount_inr,
            },
        )

    def _build_legal_notice_template(
        self,
        case_file: CaseFile,
        standing: LegalStanding | None = None,
        notice_period_days: int = 15,
    ) -> LegalNotice:
        """Construct deterministic 15-Day Formal Legal Demand Notice template."""
        today_str = date.today().isoformat()
        forum_name, _ = determine_pecuniary_forum(case_file.disputed_amount_inr)

        seller_party = next(
            (p for p in case_file.opposite_parties if "seller" in p.role.lower()),
            case_file.opposite_parties[0],
        )
        platform_party = next(
            (
                p
                for p in case_file.opposite_parties
                if "marketplace" in p.entity_type or "platform" in p.role.lower()
            ),
            case_file.opposite_parties[-1],
        )

        total_demand = case_file.disputed_amount_inr + (
            case_file.compensation_claimed_inr or 25000.0
        )

        citations = [
            Citation(
                statute="Consumer Protection Act, 2019",
                section="Section 2(7)",
                title="Consumer Status",
                text_excerpt=(
                    "Bona fide purchaser of goods for valuable consideration without "
                    "commercial resale purpose."
                ),
                is_verified=True,
            ),
            Citation(
                statute="Consumer Protection Act, 2019",
                section="Section 2(10) & 2(11)",
                title="Defect and Deficiency",
                text_excerpt=(
                    "Shortcoming in quality, standard, or performance required by law or contract."
                ),
                is_verified=True,
            ),
            Citation(
                statute="Consumer Protection Act, 2019",
                section="Section 2(47)(viii)",
                title="Unfair Trade Practice",
                text_excerpt="Refusal to take back defective goods or refund consideration paid.",
                is_verified=True,
            ),
            Citation(
                statute="Consumer Protection (E-Commerce) Rules, 2020",
                section="Rule 6(3)",
                title="Prohibition of Return/Refund Refusal",
                text_excerpt=(
                    "No seller on marketplace shall refuse refund for defective or "
                    "non-conforming goods."
                ),
                is_verified=True,
            ),
        ]

        subject = (
            f"FORMAL LEGAL DEMAND NOTICE: Under Section 35 CPA 2019 demanding refund of "
            f"₹{case_file.disputed_amount_inr:,.2f} with 18% interest and compensation "
            f"regarding Order for {case_file.title}"
        )

        seller_addr = seller_party.address or "Address on invoice / Platform seller directory"
        platform_addr = (
            platform_party.address
            or "Corporate Headquarters / Principal Place of Business in India"
        )
        c_city = case_file.complainant.city or "New Delhi"
        comp_amt = case_file.compensation_claimed_inr or 25000.0

        body_markdown = f"""\
# FORMAL LEGAL DEMAND NOTICE
**(ISSUED UNDER SECTIONS 2(10), 2(11), 2(47), AND 35 OF THE CONSUMER PROTECTION ACT, 2019 \
READ WITH RULES 4, 5, AND 6 OF THE CONSUMER PROTECTION (E-COMMERCE) RULES, 2020)**

**SENT VIA REGISTERED POST WITH ACKNOWLEDGMENT DUE (RPAD) & SPEED POST & REGISTERED EMAIL**

**Date**: {today_str}
**Place**: {c_city}, India

**TO**:
1. **{seller_party.name}** (Opposite Party No. 1 / Seller)
   Address: {seller_addr}
2. **{platform_party.name}** (Opposite Party No. 2 / Marketplace Entity)
   Address: {platform_addr}

**FROM**:
**{case_file.complainant.name}** (Complainant / Consumer)
Address: {case_file.complainant.address or "Residential Address on record"}, {c_city}
Email: {case_file.complainant.email or "Email on record"} | \
Phone: {case_file.complainant.phone or "Phone on record"}

**SUBJECT**: {subject}

---

SIRS / MADAM,

Under instructions and on behalf of myself, **{case_file.complainant.name}**, \
a bona fide consumer, I do hereby serve upon you this Formal Legal Notice:

### 1. BONA FIDE CONSUMER STATUS (SECTION 2(7) CPA 2019)
That the Complainant is a bona fide "consumer" within the meaning of \
**Section 2(7) of the Consumer Protection Act, 2019**, having purchased goods/services \
for personal use for valuable consideration paid, and is not engaged in any commercial resale.

### 2. TRANSACTION AND FACTUAL MATRIX
1. That on **{case_file.transaction_date}**, the Complainant ordered **{case_file.title}** \
from Opposite Party No. 1 through Opposite Party No. 2's platform, paying \
**₹{case_file.disputed_amount_inr:,.2f}** electronically.
2. That upon delivery, the Complainant discovered:
{case_file.facts_summary}
3. That the Complainant reported the issue immediately, but Opposite Parties unlawfully \
denied return/refund citing arbitrary internal policies.

### 3. STATUTORY BREACHES AND UNLAWFUL CONDUCT
1. **Defect in Goods (Section 2(10), CPA 2019)**: The goods supplied suffer from material \
faults, substandard quality, and non-conformity with representations made.
2. **Gross Deficiency in Service (Section 2(11), CPA 2019)**: Opposite Parties failed to \
fulfill statutory post-sale duties and arbitrarily rejected return requests.
3. **Unfair Trade Practice (Section 2(47)(viii), CPA 2019)**: Unlawful refusal to take back \
defective goods and refund consideration paid.
4. **Violation of E-Commerce Rules, 2020**:
   - **Rule 6(3)**: Explicit statutory bar prohibiting sellers from refusing refunds.
   - **Rule 4(5)**: Mandatory grievance resolution timeline violated.
   - **Non-Exemption under IT Act Section 79**: Under Rule 5(1), marketplace entities cannot \
seek intermediary safe harbor exemption while actively facilitating unfair trade practices.

### 4. PEREMPTORY 15-DAY DEMAND
You are hereby jointly and severally called upon to comply with the following demands \
within **FIFTEEN (15) DAYS** from the date of receipt of this Legal Notice:
1. **Full Refund**: Immediately refund **₹{case_file.disputed_amount_inr:,.2f}** along with \
interest at the rate of **18% per annum** from the date of payment until realization.
2. **Compensation**: Pay an amount of **₹{comp_amt:,.2f}** towards mental agony, severe \
harassment, trauma, and loss of valuable time caused to the Complainant.
3. **Legal Expenses**: Pay a sum of **₹5,000.00** towards legal notice expenses.

### 5. NOTICE OF LEGAL ACTION (E-DAAKHIL FILING)
Please take notice that if you fail to comply with the aforesaid demands within the stipulated \
period of **15 days**, the Complainant shall institute an online consumer complaint before the \
competent **{forum_name}** under **Section 35 of CPA 2019 via e-Daakhil (`edaakhil.nic.in`)**.

In that event, you shall be held jointly and severally liable for all consequential damages, \
punitive damages, and full costs of litigation at your sole risk and peril.

**Copy retained for official records and production before the Hon'ble Consumer Commission.**

Yours faithfully,

**{case_file.complainant.name}**
(Complainant / Party-in-Person)

**LIST OF ANNEXURES**:
- Annexure A: Copy of Tax Invoice & Proof of Purchase
- Annexure B: Bank / UPI Electronic Payment Confirmation
- Annexure C: Photographs / Video Proof of Defective Goods
- Annexure D: Customer Support Chat / Rejection Email Trail
"""
        return LegalNotice(
            document_id=f"doc_{uuid.uuid4().hex[:8]}",
            document_type="legal_notice",
            title=f"15-Day Formal Legal Notice under CPA 2019 - {case_file.title}",
            recipient=f"{seller_party.name} & {platform_party.name}",
            subject=subject,
            body_markdown=body_markdown,
            statutory_citations=citations,
            verification_statement=None,
            annexure_list=[
                "Annexure A: Tax Invoice with GSTIN",
                "Annexure B: Bank / UPI Payment Receipt",
                "Annexure C: Photographs / Proof of Defective Goods",
                "Annexure D: Customer Support Chat / Rejection Email Trail",
            ],
            demand_summary=(
                f"Full refund of ₹{case_file.disputed_amount_inr:,.2f} + 18% p.a. interest + "
                f"₹{comp_amt:,.2f} compensation within 15 days."
            ),
            response_deadline_days=notice_period_days,
            notice_period_days=notice_period_days,
            claim_amount_inr=total_demand,
            metadata={
                "seller": seller_party.name,
                "platform": platform_party.name,
                "forum": forum_name,
            },
        )

    def _build_edaakhil_complaint_template(
        self,
        case_file: CaseFile,
        standing: LegalStanding | None = None,
    ) -> DraftDocument:
        """Construct deterministic 7-part e-Daakhil Consumer Complaint Petition template."""
        today = date.today()
        today_str = today.isoformat()
        forum_name, _ = determine_pecuniary_forum(case_file.disputed_amount_inr)
        court_fee = calculate_edaakhil_fee(case_file.disputed_amount_inr)
        coa_date_str = case_file.cause_of_action_date or case_file.transaction_date

        seller_party = next(
            (p for p in case_file.opposite_parties if "seller" in p.role.lower()),
            case_file.opposite_parties[0],
        )
        platform_party = next(
            (
                p
                for p in case_file.opposite_parties
                if "marketplace" in p.entity_type or "platform" in p.role.lower()
            ),
            case_file.opposite_parties[-1],
        )

        complainant_city = case_file.complainant.city or "New Delhi"
        complainant_state = case_file.complainant.state or "Delhi"
        comp_amt = case_file.compensation_claimed_inr or 25000.0

        citations = [
            Citation(
                statute="Consumer Protection Act, 2019",
                section="Section 35(1)",
                title="Manner in which Complaint shall be made",
                text_excerpt=(
                    "Filing of consumer complaint electronically through e-Daakhil "
                    "before District Commission."
                ),
                is_verified=True,
            ),
            Citation(
                statute="Consumer Protection Act, 2019",
                section="Section 34(2)(d)",
                title="Territorial Jurisdiction",
                text_excerpt=(
                    "Complaint instituted where the complainant resides or personally "
                    "works for gain."
                ),
                is_verified=True,
            ),
            Citation(
                statute="Consumer Protection (Jurisdiction of Commissions) Rules, 2021",
                section="Rule 3",
                title="Pecuniary Jurisdiction of District Commission",
                text_excerpt=(
                    "Value of goods or services paid as consideration does not exceed "
                    "fifty lakh rupees."
                ),
                is_verified=True,
            ),
            Citation(
                statute="Consumer Protection Act, 2019",
                section="Section 69(1)",
                title="Limitation Period",
                text_excerpt=(
                    "Complaint shall be admitted within two years from the date on which "
                    "cause of action has arisen."
                ),
                is_verified=True,
            ),
            Citation(
                statute="Consumer Protection Act, 2019",
                section="Section 39",
                title="Findings of Commission & Reliefs",
                text_excerpt=(
                    "Orders directing refund of price, compensation for negligence, "
                    "and payment of costs."
                ),
                is_verified=True,
            ),
        ]

        verification_text = (
            f"I, {case_file.complainant.name}, do hereby solemnly declare and verify on oath "
            "that the contents of Paragraphs 1 to 5 of the Statement of Facts and the Grounds "
            "of Claim are true and correct to the best of my personal knowledge and belief, "
            "based on official records, and no part thereof is false and nothing material has "
            f"been concealed therefrom. Verified at {complainant_city} on this {today.day} day of "
            f"{today.strftime('%B')}, {today.year}."
        )

        subject = (
            f"CONSUMER COMPLAINT UNDER SECTION 35 CPA 2019: {case_file.complainant.name} "
            f"v. {seller_party.name} & {platform_party.name} regarding {case_file.title}"
        )

        c_upper_city = complainant_city.upper()
        c_upper_state = complainant_state.upper()
        seller_addr = seller_party.address or "Address on file / Platform seller directory"
        platform_addr = platform_party.address or "Corporate Headquarters in India"

        body_markdown = f"""\
# BEFORE THE HON'BLE DISTRICT CONSUMER DISPUTES REDRESSAL COMMISSION \
AT {c_upper_city}, {c_upper_state}

### CONSUMER COMPLAINT NO. _________ OF {today.year}
**(INSTITUTED UNDER SECTION 35 READ WITH SECTION 34(2)(d) OF THE CONSUMER PROTECTION ACT, 2019)**

---

### PART I: MEMO OF PARTIES

**IN THE MATTER OF:**

**{case_file.complainant.name}**
Age: Adult, S/o or D/o: [Parent/Spouse Name on record]
Residing at: {case_file.complainant.address or "Address on file"}, \
{complainant_city}, {complainant_state}
Mobile: {case_file.complainant.phone or "Mobile on file"} | \
Email: {case_file.complainant.email or "Email on file"}
... **COMPLAINANT**

**VERSUS**

1. **{seller_party.name}** (Seller)
   Registered Office: {seller_addr}
   ... **OPPOSITE PARTY NO. 1**

2. **{platform_party.name}** (E-Commerce Marketplace Entity)
   Principal Office: {platform_addr}
   ... **OPPOSITE PARTY NO. 2**

---

### PART II: INDEX OF DOCUMENTS

| Sl. No. | Description of Annexure | Annexure Marker |
|:---:|:---|:---:|
| 1. | Formal Consumer Complaint with Solemn Verification Affidavit | - |
| 2. | Copy of Tax Invoice & Proof of Purchase dated {case_file.transaction_date} | \
**Annexure C-1** |
| 3. | Copy of Electronic Bank / UPI Payment Receipt of \
₹{case_file.disputed_amount_inr:,.2f} | **Annexure C-2** |
| 4. | Photographic Proof / Video Recording of Defective / Spurious Goods | **Annexure C-3** |
| 5. | Email Communication & Customer Support Denial Records | **Annexure C-4** |
| 6. | Copy of Formal 15-Day Legal Demand Notice dated \
{case_file.cause_of_action_date or today_str} with Postal Receipt | **Annexure C-5** |

---

### PART III: STATEMENT OF MATERIAL FACTS

MOST RESPECTFULLY SHOWETH:

1. **Status of Parties**:
   The Complainant is an individual residing at {complainant_city}, {complainant_state}, \
and is a bona fide "consumer" under **Section 2(7) of the Consumer Protection Act, 2019**. \
The goods/services were purchased solely for personal use for valuable consideration paid, \
and not for commercial resale. Opposite Party No. 1 is the registered seller, and \
Opposite Party No. 2 is the marketplace platform under the E-Commerce Rules, 2020.

2. **Purchase Transaction & Consideration**:
   On **{case_file.transaction_date}**, the Complainant purchased **{case_file.title}** \
through Opposite Party No. 2's marketplace, paying valuable consideration of \
**₹{case_file.disputed_amount_inr:,.2f}** (**Annexure C-1 and C-2**).

3. **Defect & Grievance**:
   {case_file.facts_summary}

4. **Arbitrary Denial & Statutory Breach**:
   The Complainant immediately reported the grievance to Opposite Parties. Opposite Parties \
arbitrarily refused return/refund, directly violating Rule 4(5) and Rule 6(3) of \
the Consumer Protection (E-Commerce) Rules, 2020.

5. **Exhaustion of Pre-Litigation Notice**:
   The Complainant dispatched a formal 15-day Legal Demand Notice upon Opposite Parties on \
{case_file.cause_of_action_date or today_str} (**Annexure C-5**). Opposite Parties \
failed to remedy the grievance within the stipulated window.

---

### PART IV: STATUTORY GROUNDS OF CLAIM

The present complaint is instituted on the following distinct legal grounds:

- **GROUND A (GROSS DEFICIENCY IN SERVICE - SECTION 2(11) CPA 2019)**:
  Opposite Parties acted with gross deficiency, imperfection, and inadequacy in the quality \
and manner of performance required by law and contract.

- **GROUND B (DEFECT IN GOODS - SECTION 2(10) CPA 2019)**:
  The goods delivered were defective, substandard, and failed to conform to the representations.

- **GROUND C (UNFAIR TRADE PRACTICE - SECTION 2(47)(viii) CPA 2019)**:
  Opposite Parties adopted an unfair trade practice by unlawfully refusing to take back \
defective goods and refund consideration paid within thirty days.

- **GROUND D (VIOLATION OF CONSUMER PROTECTION (E-COMMERCE) RULES, 2020)**:
  Opposite Party No. 1 violated Rule 6(3) barring refusal of refunds. Opposite Party No. 2 \
breached Rule 4(4) and Rule 4(5) by failing to ensure proper grievance officer redressal.

- **GROUND E (JOINT AND SEVERAL LIABILITY)**:
  Pursuant to Rule 5(1) of the E-Commerce Rules, Opposite Party No. 2 cannot claim safe harbor \
under Section 79 of the Information Technology Act, 2000, and is jointly and severally liable.

---

### PART V: PECUNIARY & TERRITORIAL JURISDICTION

1. **Pecuniary Jurisdiction**:
   The value of consideration paid is **₹{case_file.disputed_amount_inr:,.2f}**, which does \
not exceed ₹50,00,000/- (Rupees Fifty Lakhs). Hence, this Hon'ble District Commission has \
competent pecuniary jurisdiction under **Rule 3 of the 2021 Pecuniary Rules**.

2. **Territorial Jurisdiction**:
   The Complainant resides and personally works for gain at \
**{complainant_city}, {complainant_state}**. Territorial jurisdiction is expressly conferred \
under **Section 34(2)(d) of the Consumer Protection Act, 2019**.

3. **Statutory Filing Fee**:
   The statutory filing fee is **₹{court_fee}** under the statutory schedule, payable \
online via Bharatkosh on e-Daakhil (Nil fee for consideration up to ₹5,00,000/-).

---

### PART VI: LIMITATION STATEMENT (SECTION 69)

The cause of action first arose on **{coa_date_str}** when Opposite Parties rejected the \
return/refund. The present complaint is instituted within the mandatory 2-year limitation \
period (730 days) prescribed under **Section 69(1) of the Consumer Protection Act, 2019**.

---

### PART VII: PRAYER / RELIEF SOUGHT

WHEREFORE, in light of the above facts, grounds, and statutory provisions, the Complainant \
most respectfully prays that this Hon'ble Commission may be pleased to:

a) **Direct Opposite Parties jointly and severally to refund** the full consideration \
amount of **₹{case_file.disputed_amount_inr:,.2f}** along with interest @ **12% per annum** \
from the date of payment until realization;
b) **Award compensation of ₹{comp_amt:,.2f}** against Opposite Parties for mental \
harassment, trauma, agony, and hardship caused to the Complainant;
c) **Award litigation costs of ₹5,000.00** incurred in pursuing these proceedings; and
d) **Pass such other and further relief(s)** as this Hon'ble Commission may deem fit \
and proper in the interest of justice.

**COMPLAINANT**
Through: Self (Party-in-Person)
Place: {complainant_city}
Date: {today_str}

---

### VERIFICATION / SOLEMN AFFIDAVIT CLAUSE

{verification_text}

**DEPONENT / COMPLAINANT**
"""
        return DraftDocument(
            document_id=f"doc_{uuid.uuid4().hex[:8]}",
            document_type="edaakhil_complaint",
            title=f"e-Daakhil Complaint Petition before {forum_name} - {case_file.title}",
            recipient=f"{forum_name} at {complainant_city}, {complainant_state}",
            subject=subject,
            body_markdown=body_markdown,
            statutory_citations=citations,
            verification_statement=verification_text,
            annexure_list=[
                "Annexure C-1: Copy of Tax Invoice & Proof of Purchase",
                "Annexure C-2: Bank / UPI Payment Confirmation Receipt",
                "Annexure C-3: Photographic Proof / Video Recording of Defective Goods",
                "Annexure C-4: Customer Support Denial Chat & Grievance Logs",
                ("Annexure C-5: Copy of 15-Day Legal Demand Notice with Postal Tracking Receipt"),
            ],
            demand_summary=(
                f"Full refund of ₹{case_file.disputed_amount_inr:,.2f} + 12% p.a. interest + "
                f"₹{comp_amt:,.2f} compensation + ₹5,000 costs."
            ),
            response_deadline_days=21,
            metadata={
                "forum": forum_name,
                "court_fee_inr": court_fee,
                "territorial_jurisdiction": f"{complainant_city}, {complainant_state}",
            },
        )
