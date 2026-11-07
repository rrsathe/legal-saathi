"""Opposing Counsel Simulator workflow (Mode 4).

Adversarial practice engine simulating corporate defense counsel representing
e-commerce platforms and merchants, evaluating consumer arguments, and providing
statutory counter-strategies under the Consumer Protection Act, 2019.
"""

from __future__ import annotations

import logging
import re
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from legal_assistant.llm.prompts import (
    SIMULATOR_SYSTEM_PROMPT,
)
from legal_assistant.llm.router import LLMRouter
from legal_assistant.schemas import CaseFile, DebateTurn, SimulationSession

logger = logging.getLogger(__name__)


class DefenseTacticType(StrEnum):
    """Canonical defense tactics deployed by e-commerce platforms and merchants."""

    TERMS_AND_CONDITIONS_NO_REFUND = "terms_and_conditions_no_refund"
    UNBOXING_VIDEO_ABSENCE = "unboxing_video_absence"
    IT_ACT_SECTION_79_SAFE_HARBOR = "it_act_section_79_safe_harbor"
    THIRD_PARTY_LOGISTICS_MANUFACTURER = "third_party_logistics_manufacturer"
    OTP_VERIFICATION_ACCEPTANCE = "otp_verification_acceptance"
    CUSTOM_TACTIC = "custom_tactic"


class ArgumentFeedback(BaseModel):
    """Detailed evaluation feedback on a consumer's argument or rebuttal."""

    model_config = ConfigDict(extra="ignore")

    score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Argument effectiveness and legal soundness score (0-100)",
    )
    strengths: list[str] = Field(
        default_factory=list,
        description="Factual and statutory strengths in the consumer's argument",
    )
    weaknesses: list[str] = Field(
        default_factory=list,
        description="Legal vulnerabilities or omissions in the consumer's rebuttal",
    )
    statutory_sections_cited: list[str] = Field(
        default_factory=list,
        description="Verified statutory sections/rules correctly invoked by consumer",
    )
    missing_statutory_sections: list[str] = Field(
        default_factory=list,
        description="Essential statutory sections consumer should have cited",
    )
    flaws_in_merchant_defense: list[str] = Field(
        default_factory=list,
        description="Inherent legal flaws, fallacies, or violations in opponent's tactic",
    )
    suggested_counter_arguments: list[str] = Field(
        default_factory=list,
        description="Authoritative, winning statutory counter-arguments for Commission",
    )
    coaching_tip: str = Field(
        ...,
        description="Tactical advice on presentation, tone, and evidentiary framing",
    )


class SimulatorTurn(BaseModel):
    """Single turn in the opposing counsel simulation session."""

    model_config = ConfigDict(extra="ignore")

    turn_id: str = Field(
        default_factory=lambda: f"turn_{uuid.uuid4().hex[:6]}",
        description="Unique turn identifier",
    )
    turn_number: int = Field(
        ...,
        ge=1,
        description="1-based sequence index",
    )
    speaker: Literal["opposing_counsel", "consumer", "moderator"] = Field(
        ...,
        description="Speaker role",
    )
    content: str = Field(
        ...,
        description="Verbatim spoken or submitted argument text",
    )
    defense_tactic: DefenseTacticType | str | None = Field(
        default=None,
        description="Defense tactic employed if speaker is opposing counsel",
    )
    feedback: ArgumentFeedback | None = Field(
        default=None,
        description="Evaluation feedback if speaker is consumer",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Turn completion timestamp",
    )


class SimulatorState(BaseModel):
    """Dynamic conversational state of the Opposing Counsel Simulator."""

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
        default="Corporate Legal Counsel",
        description="Name or title of opposing advocate/counsel",
    )
    opponent_entity: str = Field(
        default="E-Commerce Marketplace",
        description="Entity represented: marketplace, seller, manufacturer, 3PL",
    )
    case_summary: str = Field(
        ...,
        description="Salient case facts establishing the dispute premise",
    )
    turns: list[SimulatorTurn] = Field(
        default_factory=list,
        description="Chronological transcript of simulation turns",
    )
    cumulative_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Aggregate argument readiness score across evaluated consumer turns",
    )
    turn_count: int = Field(
        default=0,
        ge=0,
        description="Total turns exchanged",
    )
    is_concluded: bool = Field(
        default=False,
        description="Whether the debate session has concluded",
    )
    final_assessment: str | None = Field(
        default=None,
        description="Overall performance assessment and courtroom readiness conclusion",
    )

    def to_simulation_session(self) -> SimulationSession:
        """Convert SimulatorState to canonical schemas.SimulationSession.

        Returns:
            SimulationSession matching the central schemas model.
        """
        debate_turns: list[DebateTurn] = []
        for t in self.turns:
            speaker_mapped: Literal["user", "opposing_counsel", "judge", "mediator"]
            if t.speaker == "consumer":
                speaker_mapped = "user"
            elif t.speaker == "opposing_counsel":
                speaker_mapped = "opposing_counsel"
            else:
                speaker_mapped = "mediator"

            tactic_name = str(t.defense_tactic) if t.defense_tactic else None
            statutory_counter = None
            flaws = None
            suggested = None
            if t.feedback:
                statutory_counter = (
                    "; ".join(t.feedback.suggested_counter_arguments)
                    if t.feedback.suggested_counter_arguments
                    else None
                )
                flaws = (
                    "; ".join(t.feedback.flaws_in_merchant_defense)
                    if t.feedback.flaws_in_merchant_defense
                    else None
                )
                suggested = t.feedback.coaching_tip

            debate_turns.append(
                DebateTurn(
                    turn_number=t.turn_number,
                    speaker=speaker_mapped,
                    argument=t.content,
                    defense_strategy_name=tactic_name,
                    statutory_counter=statutory_counter,
                    weakness_exploited=flaws,
                    counter_strategy=suggested,
                )
            )

        return SimulationSession(
            session_id=self.session_id,
            case_id=self.case_id,
            opponent_name=self.opponent_name,
            turns=debate_turns,
            readiness_score=self.cumulative_score,
            coaching_summary=self.final_assessment or "",
        )


@dataclass(frozen=True)
class DefenseTacticProfile:
    """Catalog entry defining a corporate defense tactic and statutory counters."""

    tactic_type: DefenseTacticType
    title: str
    sample_arguments: tuple[str, ...]
    essential_statutes: tuple[str, ...]
    defense_flaws: tuple[str, ...]
    winning_counter_points: tuple[str, ...]
    keyword_triggers: tuple[str, ...]


TACTIC_CATALOG: dict[DefenseTacticType, DefenseTacticProfile] = {
    DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND: DefenseTacticProfile(
        tactic_type=DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND,
        title="Terms & Conditions: All Sales Final / No Refunds Policy",
        sample_arguments=(
            (
                "Clause 14 of our Terms of Use explicitly states: 'All sales are final; "
                "items cannot be returned or refunded under any circumstances once delivered.' "
                "You accepted these terms when clicking 'Place Order'. "
                "Under the Indian Contract Act, this forms a binding contract, "
                "so no refund is payable."
            ),
            (
                "Our platform policy clearly disclaims any cash refunds; "
                "we only provide replacement or store wallet credits at our sole discretion."
            ),
        ),
        essential_statutes=(
            "Section 2(46)",
            "Section 2(47)",
            "Rule 6(5)",
            "Rule 6(3)",
            "Rule 7(4)",
        ),
        defense_flaws=(
            (
                "Unilateral standard-form adhesion contracts containing blanket 'no refund' "
                "terms are void ab initio as 'unfair contracts' under Section 2(46)(vi) "
                "of CPA 2019."
            ),
            (
                "Rule 6(3) and Rule 7(4) of E-Commerce Rules 2020 explicitly forbid "
                "refusal to refund consideration for defective or deficient goods."
            ),
            (
                "Statutory consumer rights override private contractual disclaimers; "
                "parties cannot contract out of CPA 2019."
            ),
        ),
        winning_counter_points=(
            (
                "Under Section 2(46)(vi) of CPA 2019, any contractual condition that "
                "imposes unreasonable terms or puts the consumer at a disadvantage "
                "is an 'unfair contract'."
            ),
            (
                "Rule 6(5) of Consumer Protection (E-Commerce) Rules, 2020 strictly bars "
                "marketplace entities from adopting unfair trade practices."
            ),
            (
                "As settled by the Supreme Court in Pioneer Urban Land & Infrastructure "
                "Ltd. v. Govindan Raghavan (2019), one-sided standard clauses in contracts "
                "cannot be enforced against consumers."
            ),
        ),
        keyword_triggers=(
            "terms",
            "terms and conditions",
            "policy",
            "no refund",
            "final sale",
            "contract",
        ),
    ),
    DefenseTacticType.UNBOXING_VIDEO_ABSENCE: DefenseTacticProfile(
        tactic_type=DefenseTacticType.UNBOXING_VIDEO_ABSENCE,
        title="Absence of Continuous 360-Degree Unboxing Video",
        sample_arguments=(
            (
                "Our return policy clearly mandates an unbroken, continuous 360-degree "
                "unboxing video recorded from the moment of package receipt to inspect "
                "any claims of missing or damaged items. Since you failed to submit an "
                "unboxing video, your refund claim is summarily rejected."
            ),
            (
                "Without an uninterrupted unboxing video, we cannot verify whether the "
                "item was damaged before or after delivery. The burden of proof is on you."
            ),
        ),
        essential_statutes=(
            "Section 2(10)",
            "Section 2(11)",
            "Section 2(46)",
            "Section 2(47)",
            "Rule 4(5)",
        ),
        defense_flaws=(
            (
                "Neither the Consumer Protection Act, 2019 nor the E-Commerce Rules, 2020 "
                "authorize merchants to impose video recording obligations on consumers as "
                "a prerequisite for grievance redressal."
            ),
            (
                "Demanding continuous video recording creates an unreasonable evidentiary "
                "hurdle, constituting an 'unfair contract' under Section 2(46)(vi) and an "
                "'unfair trade practice' under Section 2(47)."
            ),
            (
                "Contemporaneous photos, delivery invoices, and prompt notification to customer "
                "support satisfy the initial evidentiary burden under Indian law."
            ),
        ),
        winning_counter_points=(
            (
                "There is no statutory requirement under CPA 2019 or E-Commerce Rules 2020 "
                "requiring consumers to record video evidence of package opening."
            ),
            (
                "Imposing an unboxing video condition constitutes an 'unfair contract' under "
                "Section 2(46)(vi) and 'unfair trade practice' under Section 2(47)."
            ),
            (
                "The tax invoice, outer packaging photos showing label weight, and grievance "
                "ticket raised within hours of delivery establish prima facie proof of deficiency "
                "in service under Section 2(11)."
            ),
        ),
        keyword_triggers=(
            "unboxing",
            "video",
            "unboxing video",
            "proof of opening",
            "package receipt",
        ),
    ),
    DefenseTacticType.IT_ACT_SECTION_79_SAFE_HARBOR: DefenseTacticProfile(
        tactic_type=DefenseTacticType.IT_ACT_SECTION_79_SAFE_HARBOR,
        title="Intermediary Immunity under Section 79 of Information Technology Act, 2000",
        sample_arguments=(
            (
                "Our platform is merely an electronic marketplace intermediary under Section "
                "2(1)(w) of the IT Act, 2000. Under Section 79 of the IT Act, 2000, we are "
                "entitled to safe harbor immunity from third-party seller listings and defective "
                "goods. Your claim lies solely against the third-party merchant, not against "
                "our platform."
            ),
            (
                "We only provide the technology infrastructure connecting buyers and "
                "independent third-party sellers. We cannot be held liable for defective "
                "products supplied by independent vendors."
            ),
        ),
        essential_statutes=(
            "Section 79 IT Act",
            "Section 86",
            "Rule 4(4)",
            "Rule 4(5)",
            "Rule 5",
            "Rule 6",
        ),
        defense_flaws=(
            (
                "Section 79 IT Act safe harbor applies to third-party content and data "
                "transmission, not to contractual and statutory obligations under consumer "
                "protection legislation."
            ),
            (
                "Under Section 86 of CPA 2019, an e-commerce platform that provides services "
                "or handles payments/returns is liable in a product liability action."
            ),
            (
                "Consumer Protection (E-Commerce) Rules, 2020 establish independent affirmative "
                "duties for marketplace entities (Grievance Officer, 48-hour ack, preventing "
                "unfair trade practices) that cannot be derogated using Section 79."
            ),
        ),
        winning_counter_points=(
            (
                "Intermediary safe harbor under Section 79 of the IT Act does not exempt "
                "e-commerce marketplaces from liability under the Consumer Protection Act, "
                "2019 or the E-Commerce Rules, 2020."
            ),
            (
                "Under Section 86 of CPA 2019, marketplace platforms that exercise control "
                "over payment processing, delivery, or return logistics are directly liable "
                "in product liability claims."
            ),
            (
                "Rule 4(4) and Rule 4(5) of the E-Commerce Rules 2020 mandate that every "
                "marketplace must acknowledge consumer complaints within 48 hours and redress "
                "them within one month."
            ),
        ),
        keyword_triggers=(
            "section 79",
            "intermediary",
            "safe harbor",
            "it act",
            "third-party seller",
            "marketplace only",
        ),
    ),
    DefenseTacticType.THIRD_PARTY_LOGISTICS_MANUFACTURER: DefenseTacticProfile(
        tactic_type=DefenseTacticType.THIRD_PARTY_LOGISTICS_MANUFACTURER,
        title="Dispute Between Customer and 3PL Courier / Manufacturer Warranty",
        sample_arguments=(
            (
                "Our warehouse records confirm the product was dispatched in pristine condition. "
                "Any damage or transit loss is the sole responsibility of the third-party courier "
                "partner (3PL). Furthermore, for electronic defects, you must contact the "
                "manufacturer's authorized service center under warranty."
            ),
            (
                "We have already discharged our obligations by handing over the package to the "
                "courier. Please take this up with the logistics agency or manufacturer directly."
            ),
        ),
        essential_statutes=(
            "Section 2(7)",
            "Section 2(11)",
            "Section 84",
            "Section 86",
            "Rule 6(3)",
            "Rule 7(4)",
        ),
        defense_flaws=(
            (
                "Privity of contract exists between the consumer and the seller/platform from "
                "whom consideration was paid (Section 2(7)). The consumer has no privity with "
                "the seller's logistics contractor."
            ),
            (
                "Under Section 2(11) of CPA 2019, transit failure or courier mishandling engaged "
                "by the merchant constitutes 'deficiency in service' directly attributable to "
                "the merchant."
            ),
            (
                "Rules 6(3) and 7(4) of E-Commerce Rules 2020 prohibit merchants from deflecting "
                "consumers to manufacturers for defective or non-conforming items."
            ),
        ),
        winning_counter_points=(
            (
                "The consumer paid consideration to the platform/seller, establishing privity of "
                "contract under Section 2(7); logistics partners are agents of the seller."
            ),
            (
                "Failure to deliver goods intact constitutes deficiency in service under Section "
                "2(11) of CPA 2019, for which the merchant bears vicarious and direct liability."
            ),
            (
                "Under Rule 6(3) of E-Commerce Rules 2020, sellers cannot refuse "
                "returns or refunds by deflecting consumers to third-party manufacturers."
            ),
        ),
        keyword_triggers=(
            "courier",
            "logistics",
            "3pl",
            "manufacturer",
            "service center",
            "warranty only",
            "transit",
        ),
    ),
    DefenseTacticType.OTP_VERIFICATION_ACCEPTANCE: DefenseTacticProfile(
        tactic_type=DefenseTacticType.OTP_VERIFICATION_ACCEPTANCE,
        title="Delivery Accepted via OTP Verification",
        sample_arguments=(
            (
                "The delivery was completed and authenticated via One-Time Password (OTP) shared "
                "by the customer at the time of delivery. Sharing OTP constitutes conclusive legal "
                "acknowledgment that the package was received in sound condition."
            ),
        ),
        essential_statutes=(
            "Section 2(10)",
            "Section 2(11)",
            "Section 2(46)",
            "Rule 6(3)",
        ),
        defense_flaws=(
            (
                "OTP verification merely confirms receipt of the outer parcel from the delivery "
                "agent, not inspection or acceptance of internal contents."
            ),
            (
                "Latent defects or delivery of spurious/wrong goods inside a sealed box cannot "
                "be detected prior to opening."
            ),
        ),
        winning_counter_points=(
            (
                "OTP verification confirms delivery of the outer package, not satisfaction with "
                "internal sealed goods."
            ),
            (
                "Under Section 2(10) and Section 2(11), latent defects discovered upon opening "
                "entitle the consumer to full return and refund."
            ),
        ),
        keyword_triggers=("otp", "otp verification", "delivered with otp", "accepted delivery"),
    ),
}


class OpposingCounselSimulator:
    """Mode 4: Opposing Counsel Simulator and Argumentation Coach."""

    def __init__(self, router: LLMRouter | None = None) -> None:
        """Initialize simulator with LLM router.

        Args:
            router: Optional LLMRouter instance. Defaults to new LLMRouter().
        """
        self.router = router or LLMRouter()

    def start_simulation(
        self,
        case: CaseFile | dict[str, Any] | str,
        initial_tactic: DefenseTacticType | str | None = None,
        opponent_name: str = "Adv. Vikrant Singhania (Corporate Legal Counsel)",
        opponent_entity: str = "Marketplace Platform",
    ) -> SimulatorState:
        """Initialize a new simulation session and generate opening defense salvo.

        Args:
            case: CaseFile instance, raw case dictionary, or string summary.
            initial_tactic: Specific defense tactic to open with. If None, chosen
                automatically based on case facts.
            opponent_name: Name of opposing corporate advocate.
            opponent_entity: Entity represented (marketplace, merchant, logistics).

        Returns:
            SimulatorState initialized with Turn 1 containing counsel's opening argument.
        """
        case_id = getattr(case, "case_id", "case_sim_01")
        if isinstance(case, CaseFile):
            summary = case.facts_summary
        elif isinstance(case, dict):
            summary = str(case.get("facts_summary", case.get("summary", "Consumer dispute")))
        else:
            summary = str(case)

        chosen_tactic: DefenseTacticType
        if initial_tactic:
            chosen_tactic = (
                DefenseTacticType(initial_tactic)
                if initial_tactic in DefenseTacticType.__members__.values()
                else DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND
            )
        else:
            lower_summary = summary.lower()
            if "video" in lower_summary or "unboxing" in lower_summary:
                chosen_tactic = DefenseTacticType.UNBOXING_VIDEO_ABSENCE
            elif "courier" in lower_summary or "logistics" in lower_summary:
                chosen_tactic = DefenseTacticType.THIRD_PARTY_LOGISTICS_MANUFACTURER
            elif "platform" in lower_summary or "marketplace" in lower_summary:
                chosen_tactic = DefenseTacticType.IT_ACT_SECTION_79_SAFE_HARBOR
            else:
                chosen_tactic = DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND

        fallback_profile = TACTIC_CATALOG[DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND]
        profile = TACTIC_CATALOG.get(chosen_tactic, fallback_profile)
        opening_content = profile.sample_arguments[0]

        turn_1 = SimulatorTurn(
            turn_number=1,
            speaker="opposing_counsel",
            content=opening_content,
            defense_tactic=chosen_tactic,
        )

        return SimulatorState(
            case_id=case_id,
            opponent_name=opponent_name,
            opponent_entity=opponent_entity,
            case_summary=summary,
            turns=[turn_1],
            cumulative_score=0.0,
            turn_count=1,
            is_concluded=False,
        )

    def evaluate_consumer_argument(
        self,
        argument: str,
        active_tactic: DefenseTacticType | str,
        case_summary: str = "",
        use_llm: bool = False,
    ) -> ArgumentFeedback:
        """Evaluate consumer's rebuttal against opposing defense tactic.

        Args:
            argument: Consumer's verbatim rebuttal text.
            active_tactic: The defense tactic deployed by opposing counsel.
            case_summary: Disputed case facts summary.
            use_llm: Whether to invoke LLM structured generation or use
                deterministic evaluation.

        Returns:
            ArgumentFeedback with score, strengths, weaknesses, sections, and tips.
        """
        tactic_enum = (
            DefenseTacticType(active_tactic)
            if active_tactic in DefenseTacticType.__members__.values()
            else DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND
        )
        fallback_profile = TACTIC_CATALOG[DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND]
        profile = TACTIC_CATALOG.get(tactic_enum, fallback_profile)

        if use_llm:
            try:
                prompt = (
                    f"Evaluate this consumer's rebuttal to a corporate defense counsel:\n\n"
                    f"DISPUTE SUMMARY: {case_summary}\n"
                    f"OPPOSING COUNSEL TACTIC: {profile.title}\n"
                    f'CONSUMER ARGUMENT: """{argument}"""\n\n'
                    f"ESSENTIAL STATUTES EXPECTED: {', '.join(profile.essential_statutes)}\n"
                    f"KNOWN FLAWS IN DEFENSE: {'; '.join(profile.defense_flaws)}\n\n"
                    f"Score from 0 to 100 and populate the ArgumentFeedback schema."
                )
                return self.router.generate_structured(
                    prompt=prompt,
                    schema=ArgumentFeedback,
                    system_prompt=SIMULATOR_SYSTEM_PROMPT,
                    temperature=0.1,
                )
            except Exception as e:
                logger.warning(
                    "LLM evaluation failed, falling back to deterministic evaluation: %s",
                    e,
                )

        return self._score_argument_deterministically(argument, profile, case_summary)

    def _score_argument_deterministically(
        self,
        argument: str,
        profile: DefenseTacticProfile,
        case_summary: str,
    ) -> ArgumentFeedback:
        """Score consumer argument deterministically using legal token rules.

        Args:
            argument: Verbatim consumer rebuttal.
            profile: Defense tactic catalog profile.
            case_summary: Case facts summary.

        Returns:
            ArgumentFeedback instance.
        """
        arg_lower = argument.lower()

        # 1. Detect statutory references
        statutory_pattern = re.compile(
            r"(?:Section|Sec\.?|Rule)\s*\d+[a-zA-Z]?(?:\([a-zA-Z0-9]+\))*",
            re.IGNORECASE,
        )
        found_sections: list[str] = [m.strip() for m in statutory_pattern.findall(argument)]

        has_cpa = "consumer protection act" in arg_lower or "cpa" in arg_lower
        has_ecom = "e-commerce" in arg_lower or "ecommerce" in arg_lower
        has_it_act = "it act" in arg_lower or "information technology" in arg_lower

        # 2. Check essential sections
        cited_essential: list[str] = []
        missing_essential: list[str] = []
        for sec in profile.essential_statutes:
            sec_clean = re.sub(r"^(?:Section|Rule)\s*", "", sec, flags=re.I).lower()
            if sec.lower() in arg_lower or sec_clean in arg_lower:
                cited_essential.append(sec)
            else:
                missing_essential.append(sec)

        # 3. Calculate score components
        score = 0.0
        strengths: list[str] = []
        weaknesses: list[str] = []

        # A. Statutory grounding (up to 45 points)
        if has_cpa or has_ecom or has_it_act:
            score += 15.0
            strengths.append(
                "Invoked statutory consumer protection frameworks (CPA 2019 / E-Commerce Rules)."
            )
        else:
            weaknesses.append("Failed to invoke governing legislation (CPA 2019).")

        if cited_essential:
            score += min(len(cited_essential) * 15.0, 30.0)
            strengths.append(
                f"Successfully cited relevant statutory provisions: {', '.join(cited_essential)}."
            )
        else:
            weaknesses.append(
                f"Omitted crucial statutory sections neutralizing this tactic: "
                f"{', '.join(profile.essential_statutes[:2])}."
            )

        # B. Factual & Tactical alignment (up to 35 points)
        tactic_countered = any(trigger in arg_lower for trigger in profile.keyword_triggers)

        if tactic_countered:
            score += 20.0
            strengths.append(f"Directly confronted opponent's tactic regarding {profile.title}.")
        else:
            weaknesses.append(
                "Did not directly dismantle the factual premise of the merchant's claim."
            )

        has_relief_keywords = any(
            w in arg_lower for w in ("refund", "defective", "deficiency", "void")
        )
        if has_relief_keywords:
            score += 15.0
            strengths.append(
                "Clearly demanded statutory refund and identified defect / deficiency in service."
            )

        # C. Professional legal tone (up to 20 points)
        colloquial_words = ["plz", "pls", "looting", "fraudster", "scam", "looter"]
        has_colloquial = any(w in arg_lower for w in colloquial_words)
        if len(argument.split()) >= 15 and not has_colloquial:
            score += 20.0
            strengths.append("Maintained an assertive, professional, courtroom-appropriate tone.")
        else:
            score += 5.0
            weaknesses.append("Tone was colloquial or emotional rather than legally assertive.")

        score = min(max(score, 10.0), 100.0)

        # Coaching tip construction
        if score >= 80.0:
            tip = (
                "Outstanding rebuttal. Your argument is anchored in statutory law and dismantles "
                "the defense. You are ready to present this position to the Commission."
            )
        elif score >= 50.0:
            primary_missing = missing_essential[0] if missing_essential else "Section 2(46)"
            tip = (
                f"Decent factual rebuttal, but strengthen your legal leverage. Explicitly invoke "
                f"{primary_missing} and assert that private terms cannot override statutory rights."
            )
        else:
            sec0 = profile.essential_statutes[0]
            sec1 = (
                profile.essential_statutes[1] if len(profile.essential_statutes) > 1 else "CPA 2019"
            )
            tip = (
                f"Weak rebuttal. Avoid emotional pleas. Assert that under {sec0} and {sec1}, "
                f"the merchant's stance is void as an unfair trade practice."
            )

        return ArgumentFeedback(
            score=round(score, 1),
            strengths=strengths,
            weaknesses=weaknesses,
            statutory_sections_cited=list(set(found_sections + cited_essential)),
            missing_statutory_sections=missing_essential,
            flaws_in_merchant_defense=list(profile.defense_flaws),
            suggested_counter_arguments=list(profile.winning_counter_points),
            coaching_tip=tip,
        )

    def step_simulation(
        self,
        state: SimulatorState,
        consumer_response: str,
        next_tactic: DefenseTacticType | str | None = None,
        use_llm: bool = False,
    ) -> SimulatorState:
        """Advance simulation: evaluate consumer response and generate counter-turn.

        Args:
            state: Current SimulatorState instance.
            consumer_response: The consumer's rebuttal to the previous turn.
            next_tactic: Tactic for opposing counsel's next salvo. If None,
                advances to next tactic in sequence or concludes.
            use_llm: Whether to invoke LLM for generation.

        Returns:
            Updated SimulatorState with consumer turn (evaluated) and next counsel turn.
        """
        if state.is_concluded:
            return state

        # Determine last opposing counsel tactic
        last_tactic: DefenseTacticType = DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND
        for t in reversed(state.turns):
            if t.speaker == "opposing_counsel" and t.defense_tactic:
                if t.defense_tactic in DefenseTacticType.__members__.values():
                    last_tactic = DefenseTacticType(t.defense_tactic)
                break

        # Evaluate consumer argument
        feedback = self.evaluate_consumer_argument(
            argument=consumer_response,
            active_tactic=last_tactic,
            case_summary=state.case_summary,
            use_llm=use_llm,
        )

        consumer_turn = SimulatorTurn(
            turn_number=len(state.turns) + 1,
            speaker="consumer",
            content=consumer_response,
            feedback=feedback,
        )
        state.turns.append(consumer_turn)

        # Update scores
        consumer_scores = [
            t.feedback.score
            for t in state.turns
            if t.speaker == "consumer" and t.feedback is not None
        ]
        avg_score = sum(consumer_scores) / len(consumer_scores) if consumer_scores else 0.0
        state.cumulative_score = round(avg_score, 1)
        state.turn_count = len(state.turns)

        # If 3 or more consumer turns completed, conclude
        if len(consumer_scores) >= 3:
            return self.conclude_simulation(state)

        # Select next tactic
        tactic_keys = list(TACTIC_CATALOG.keys())
        current_idx = tactic_keys.index(last_tactic) if last_tactic in tactic_keys else 0
        next_enum = tactic_keys[(current_idx + 1) % len(tactic_keys)]

        if next_tactic and next_tactic in DefenseTacticType.__members__.values():
            next_enum = DefenseTacticType(next_tactic)

        fallback_next = TACTIC_CATALOG[DefenseTacticType.TERMS_AND_CONDITIONS_NO_REFUND]
        next_profile = TACTIC_CATALOG.get(next_enum, fallback_next)
        tactic_str = last_tactic.replace("_", " ")
        next_counsel_salvo = (
            f"Even assuming for a moment that your assertion regarding {tactic_str} has merit, "
            f"our client maintains an independent defense: {next_profile.sample_arguments[0]}"
        )

        counsel_turn = SimulatorTurn(
            turn_number=len(state.turns) + 1,
            speaker="opposing_counsel",
            content=next_counsel_salvo,
            defense_tactic=next_enum,
        )
        state.turns.append(counsel_turn)
        state.turn_count = len(state.turns)

        return state

    def conclude_simulation(
        self,
        state: SimulatorState,
    ) -> SimulatorState:
        """Conclude the simulation session and compute final assessment summary.

        Args:
            state: Active SimulatorState instance.

        Returns:
            Concluded SimulatorState with is_concluded=True and final_assessment.
        """
        state.is_concluded = True
        consumer_turns = [t for t in state.turns if t.speaker == "consumer" and t.feedback]
        if not consumer_turns:
            state.final_assessment = "Simulation concluded before any arguments were evaluated."
            return state

        final_score = state.cumulative_score
        if final_score >= 80.0:
            assessment = (
                f"EXCELLENT COURTROOM READINESS (Score: {final_score}/100). "
                "The consumer demonstrated strong mastery of the Consumer Protection Act, 2019 "
                "and E-Commerce Rules, 2020. Key statutory provisions were cited with precision, "
                "effectively neutralizing corporate defenses. The consumer is fully prepared "
                "to proceed with formal Legal Notice dispatch and e-Daakhil filing."
            )
        elif final_score >= 60.0:
            assessment = (
                f"MODERATE READINESS (Score: {final_score}/100). "
                "The consumer presented valid complaints but relied on general assertions. "
                "Review coaching tips and ensure Section 2(46), Section 2(47), and Rule 6(5) are "
                "explicitly incorporated into the Legal Notice."
            )
        else:
            assessment = (
                f"NEEDS IMPROVEMENT (Score: {final_score}/100). "
                "The consumer's arguments were primarily emotional or vulnerable to adhesion "
                "defenses. Study the winning statutory counter-arguments and "
                "re-run the practice session before filing on e-Daakhil."
            )

        state.final_assessment = assessment
        return state
