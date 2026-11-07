"""Pre-retrieval scope and escalation guardrail for Legal Saathi.

Detects non-consumer legal disputes (BNS criminal offences, Section 138 NI Act cheque
bounce, commercial B2B disputes, corporate insolvency under IBC, family/matrimonial
disputes, and urgent court injunctions) before retrieval or LLM inference, directing
users to an Advocate enrolled with the Bar Council of India.
"""

from __future__ import annotations

import logging
import re

from pydantic import BaseModel, Field

from legal_assistant.llm.base import BaseLLMClient
from legal_assistant.schemas import ScopeCategory, ScopeResult

logger = logging.getLogger(__name__)


class ScopeClassificationOutput(BaseModel):
    """Structured Pydantic schema for LLM fallback intent classification."""

    is_in_scope: bool = Field(
        ...,
        description="True if query is a consumer dispute; False if out of scope",
    )
    category: str = Field(
        ...,
        description="Category name matching ScopeCategory values",
    )
    detected_triggers: list[str] = Field(
        default_factory=list,
        description="List of legal terms triggering the classification",
    )
    rationale: str = Field(
        ...,
        description="Brief legal reasoning supporting the classification",
    )


class ScopeChecker:
    """Pre-retrieval scope evaluator and Bar Council of India escalation filter."""

    # Escalation Advisories Mandating Bar Council of India Advocate Consultation
    ESCALATION_ADVICE: dict[ScopeCategory, str] = {
        ScopeCategory.CRIMINAL_OFFENSE: (
            "This matter involves allegations of a criminal offence governed by the "
            "Bharatiya Nyaya Sanhita, 2023 (or Indian Penal Code, 1860) and "
            "Bharatiya Nagarik Suraksha Sanhita, 2023. Criminal offences fall outside "
            "the jurisdiction of Consumer Disputes Redressal Commissions. You are "
            "advised to immediately report this matter to the nearest Police Station "
            "or the National Cyber Crime Reporting Portal (cybercrime.gov.in) to "
            "register a First Information Report (FIR). Furthermore, you should "
            "consult an Advocate enrolled with the Bar Council of India for "
            "representation before a competent Criminal Court or Judicial Magistrate."
        ),
        ScopeCategory.CHEQUE_BOUNCE: (
            "Dishonour of cheques and debt recovery under Section 138 of the "
            "Negotiable Instruments Act, 1881 are quasi-criminal proceedings "
            "falling outside the jurisdiction of Consumer Commissions. You must issue "
            "a formal Statutory Demand Notice within 30 days of receiving the cheque "
            "return memo, demanding payment within 15 days. If payment is not received, "
            "a criminal complaint must be filed before the competent Judicial Magistrate "
            "/ Metropolitan Magistrate within one month. You are advised to immediately "
            "engage an Advocate enrolled with the Bar Council of India to draft the "
            "statutory notice and represent you."
        ),
        ScopeCategory.COMMERCIAL_B2B: (
            "Commercial B2B transactions where goods or services are acquired for "
            "commercial purpose or resale (without falling under the personal "
            "self-employment livelihood exception of Section 2(7) of the Consumer "
            "Protection Act, 2019), as well as corporate insolvency matters under the "
            "Insolvency and Bankruptcy Code, 2016 (IBC), are excluded from Consumer "
            "Commission jurisdiction. Your remedy lies before the Commercial Courts "
            "under the Commercial Courts Act, 2015 (subject to mandatory pre-institution "
            "mediation under Section 12A) or the National Company Law Tribunal (NCLT). "
            "You are advised to consult an Advocate enrolled with the Bar Council of "
            "India specializing in commercial litigation."
        ),
        ScopeCategory.FAMILY_DIVORCE: (
            "Matrimonial disputes, divorce, child custody, maintenance, and property "
            "succession or inheritance fall exclusively under the jurisdiction of "
            "Family Courts, Civil Courts, and High Courts under personal laws (e.g., "
            "Hindu Marriage Act, 1955, Special Marriage Act, 1954, Indian Succession "
            "Act, 1925). Consumer Commissions have zero jurisdiction over family, "
            "matrimonial, or inheritance disputes. You are strongly advised to seek "
            "confidential legal counsel from an Advocate enrolled with the Bar Council "
            "of India practicing family and civil law."
        ),
        ScopeCategory.URGENT_INJUNCTION: (
            "Your dispute requires urgent interlocutory injunctive relief (such as a "
            "temporary stay order, restraining order against demolition or eviction, "
            "or emergency judicial intervention). Consumer Commissions follow summary "
            "procedure and lack ordinary plenary powers to grant immediate physical "
            "emergency stay orders on real estate demolition, eviction, or constitutional "
            "violations. You must immediately file an Urgent Suit for Injunction under "
            "Order 39 Rules 1 & 2 of the Code of Civil Procedure, 1908 (CPC) before "
            "the competent Civil Court, or file a Writ Petition under Article 226 of the "
            "Constitution before the High Court, through an Advocate enrolled with the "
            "Bar Council of India."
        ),
        ScopeCategory.LABOR_EMPLOYMENT: (
            "Employer-employee disputes, wrongful termination of employment, and "
            "recovery of unpaid salary or statutory gratuity/provident fund do not "
            "constitute consumer disputes under the Consumer Protection Act, 2019. "
            "The remedy lies before the Labor Court, Industrial Tribunal under the "
            "Industrial Disputes Act, 1947, or the Controlling Authority under the "
            "Payment of Gratuity Act, 1972. You should consult an Advocate enrolled "
            "with the Bar Council of India specializing in labor and employment law."
        ),
        ScopeCategory.OTHER_NON_CONSUMER: (
            "This matter does not appear to involve a consumer transaction for "
            "consideration paid under the Consumer Protection Act, 2019. You are advised "
            "to consult an Advocate enrolled with the Bar Council of India for advice on "
            "the competent legal forum."
        ),
    }

    def __init__(
        self,
        llm_client: BaseLLMClient | None = None,
        enable_llm_fallback: bool = False,
    ) -> None:
        """Initialize ScopeChecker.

        Args:
            llm_client: Optional BaseLLMClient instance for ambiguous fallback classification.
            enable_llm_fallback: Whether to invoke LLM if deterministic rules are ambiguous.
        """
        self.llm_client = llm_client
        self.enable_llm_fallback = enable_llm_fallback
        self._init_patterns()

    def _init_patterns(self) -> None:
        """Compile regex patterns for high-speed deterministic scope evaluation."""
        # 1. Criminal Offences (BNS / IPC / Police / Violence)
        self._criminal_patterns = [
            re.compile(
                r"\b(?:bharatiya\s+nyaya\s+sanhita|bns|ipc|indian\s+penal\s+code)\b",
                re.I,
            ),
            re.compile(
                r"\b(?:fir|first\s+information\s+report|police\s+complaint|police\s+station)\b",
                re.I,
            ),
            re.compile(
                r"\b(?:murder|homicide|assault|battery|physical\s+violence|grievous\s+hurt|stabbed)\b",
                re.I,
            ),
            re.compile(
                r"\b(?:rape|sexual\s+assault|pocso|harassment|stalking|kidnap|extortion|blackmail)\b",
                re.I,
            ),
            re.compile(r"\b(?:theft|robbery|dacoity|burglary|break-in|stolen\s+jewelry)\b", re.I),
            re.compile(
                r"\b(?:arrest|bail|anticipatory\s+bail|remand|charge\s*sheet|magistrate\s+warrant)\b",
                re.I,
            ),
            re.compile(r"\b(?:ndps|narcotics|arms\s+act|weapon|firearm)\b", re.I),
        ]

        # 2. Cheque Bounce / Debt Recovery (Section 138 NI Act)
        self._cheque_bounce_patterns = [
            re.compile(
                r"\b(?:section\s*138|sec\.?\s*138|138\s*ni\s*act|negotiable\s+instruments?\s+act)\b",
                re.I,
            ),
            re.compile(
                r"\b(?:cheque\s+bounce|bounced\s+cheque|cheque\s+dishonou?r(?:ed)?|"
                r"dishonou?r\s+of\s+cheque)\b",
                re.I,
            ),
            re.compile(
                r"\b(?:insufficient\s+funds|funds\s+insufficient|account\s+closed|"
                r"cheque\s+return\s+memo)\b",
                re.I,
            ),
            re.compile(
                r"\b(?:statutory\s+notice\s+under\s+section\s+138|15\s+days?\s+notice\s+for\s+cheque)\b",
                re.I,
            ),
            re.compile(r"\b(?:promissory\s+note|loan\s+recovery\s+against\s+cheque)\b", re.I),
        ]

        # 3. Commercial B2B / Corporate Insolvency (IBC / NCLT)
        self._commercial_patterns = [
            re.compile(r"\b(?:ibc|insolvency\s+and\s+bankruptcy(?:\s+code)?|nclt|nclat)\b", re.I),
            re.compile(
                r"\b(?:corporate\s+debtor|operational\s+creditor|financial\s+creditor|"
                r"cirp|moratorium)\b",
                re.I,
            ),
            re.compile(
                r"\b(?:b2b|wholesale\s+(?:purchase|goods)(?:\s+for\s+resale)?|"
                r"commercial\s+resale|factory\s+resale|"
                r"raw\s+material(?:\s+for\s+(?:factory\s+)?resale)?|"
                r"goods\s+purchased\s+for\s+resale|commercial\s+purpose|"
                r"commercial\s+use)\b",
                re.I,
            ),
            re.compile(
                r"\b(?:shareholder\s+dispute|oppression\s+and\s+mismanagement|"
                r"companies\s+act|board\s+of\s+directors)\b",
                re.I,
            ),
            re.compile(r"\b(?:commercial\s+courts?\s+act|section\s*12a\s+mediation)\b", re.I),
            re.compile(
                r"\b(?:distributorship\s+agreement|franchise\s+agreement\s+dispute|"
                r"supply\s+chain\s+contract)\b",
                re.I,
            ),
        ]

        # 4. Family / Matrimonial / Succession
        self._family_patterns = [
            re.compile(
                r"\b(?:divorce|mutual\s+consent\s+divorce|contested\s+divorce|"
                r"annulment\s+of\s+marriage)\b",
                re.I,
            ),
            re.compile(
                r"\b(?:hindu\s+marriage\s+act|special\s+marriage\s+act|matrimonial\s+dispute)\b",
                re.I,
            ),
            re.compile(
                r"\b(?:child\s+custody|custody\s+of\s+(?:the\s+|our\s+|my\s+|a\s+)?children|"
                r"custody\s+of\s+(?:the\s+|our\s+|my\s+|a\s+)?child|"
                r"visitation\s+rights|guardianship|adoption)\b",
                re.I,
            ),
            re.compile(
                r"\b(?:alimony|maintenance|section\s*125\s*crpc|section\s*144\s*bnss)\b",
                re.I,
            ),
            re.compile(r"\b(?:domestic\s+violence|pwdva|498a|dowry|stridhan)\b", re.I),
            re.compile(
                r"\b(?:ancestral\s+property|partition\s+suit|succession|inheritance|coparcenary)\b",
                re.I,
            ),
            re.compile(
                r"\b(?:probate|will|testament|letters\s+of\s+administration|"
                r"succession\s+certificate)\b",
                re.I,
            ),
        ]

        # 5. Urgent Injunctions / Demolition / Stay Orders
        self._injunction_patterns = [
            re.compile(
                r"\b(?:urgent\s+stay\s+order|stay\s+order|interim\s+injunction|"
                r"interlocutory\s+injunction|urgent\s+injunction)\b",
                re.I,
            ),
            re.compile(
                r"\b(?:ex\s*parte\s+stay|emergency\s+injunction|restraining\s+order|"
                r"status\s+quo\s+order)\b",
                re.I,
            ),
            re.compile(
                r"\b(?:demolition\s+stay|demolition\s+notice|municipal\s+demolition|"
                r"demolition\s+squad|bulldozer)\b",
                re.I,
            ),
            re.compile(
                r"\b(?:eviction\s+stay|eviction\s+injunction|"
                r"stay\s+order\s+against\s+eviction|urgent\s+stay\s+(?:on|against)\s+eviction|"
                r"injunction\s+against\s+(?:eviction|demolition)|"
                r"order\s*39\s*rules?\s*1\s*and\s*2)\b",
                re.I,
            ),
            re.compile(
                r"\b(?:writ\s+petition|article\s*226|article\s*32|habeas\s+corpus|mandamus)\b",
                re.I,
            ),
            re.compile(r"\b(?:police\s+protection\s+order|threat\s+to\s+life)\b", re.I),
        ]

        # 6. Labor / Employment
        self._labor_patterns = [
            re.compile(
                r"\b(?:wrongful\s+termination|illegal\s+termination|fired\s+from\s+job|"
                r"dismissal\s+from\s+employment)\b",
                re.I,
            ),
            re.compile(
                r"\b(?:unpaid\s+salary|unpaid\s+wages|salary\s+arrears|provident\s+fund|"
                r"epfo|gratuity\s+recovery)\b",
                re.I,
            ),
            re.compile(
                r"\b(?:labor\s+court|industrial\s+tribunal|industrial\s+disputes\s+act)\b",
                re.I,
            ),
        ]

        # 7. Consumer Protection Overrides
        self._consumer_indicators = [
            re.compile(
                r"\b(?:amazon|flipkart|meesho|myntra|instagram|swiggy|zomato|zepto|blinkit|tataneu)\b",
                re.I,
            ),
            re.compile(
                r"\b(?:order|ordered|seller|merchant|buyer|customer|product|item|delivery|delivered)\b",
                re.I,
            ),
            re.compile(
                r"\b(?:refund|return|replacement|defective|warranty|guarantee|damaged|broken)\b",
                re.I,
            ),
            re.compile(
                r"\b(?:upi|payment|paid|consideration|invoice|bill|receipt|subscription|edtech)\b",
                re.I,
            ),
            re.compile(
                r"\b(?:airline|flight|hotel|booking|telecom|broadband|courier|service\s+center)\b",
                re.I,
            ),
            re.compile(
                r"\b(?:livelihood|self-employed|self\s+employment|earning\s+livelihood)\b",
                re.I,
            ),
        ]

    def check_scope(self, text: str, use_llm_fallback: bool | None = None) -> ScopeResult:
        """Evaluate dispute scope and determine if matter requires Advocate escalation.

        Args:
            text: Unstructured dispute narrative or query from user.
            use_llm_fallback: Optional override to enable/disable LLM classification fallback.

        Returns:
            ScopeResult: Evaluation with in-scope flag, category, and escalation advice.
        """
        if not text or not text.strip():
            return ScopeResult(
                is_in_scope=False,
                out_of_scope_category=ScopeCategory.OTHER_NON_CONSUMER.value,
                escalation_advice=self.ESCALATION_ADVICE[ScopeCategory.OTHER_NON_CONSUMER],
                detected_triggers=["empty_query"],
            )

        # 1. Deterministic Rule Matching
        deterministic_result = self._evaluate_deterministic(text)
        if deterministic_result is not None:
            return deterministic_result

        # 2. LLM Fallback (if enabled and client available)
        should_fallback = (
            use_llm_fallback if use_llm_fallback is not None else self.enable_llm_fallback
        )
        if should_fallback and self.llm_client is not None:
            try:
                return self._classify_via_llm(text)
            except Exception as e:
                logger.warning(
                    "LLM scope fallback classification failed: %s. Defaulting to in-scope.",
                    e,
                )

        # Default: In-scope consumer dispute
        return ScopeResult(
            is_in_scope=True,
            out_of_scope_category=None,
            escalation_advice=None,
            detected_triggers=[],
        )

    def _evaluate_deterministic(self, text: str) -> ScopeResult | None:
        """Run pattern matching across categories with consumer protection overrides.

        Args:
            text: Input text string.

        Returns:
            ScopeResult if decisive match, else None.
        """
        matches: dict[ScopeCategory, list[str]] = {
            ScopeCategory.CRIMINAL_OFFENSE: self._find_matches(self._criminal_patterns, text),
            ScopeCategory.CHEQUE_BOUNCE: self._find_matches(self._cheque_bounce_patterns, text),
            ScopeCategory.COMMERCIAL_B2B: self._find_matches(self._commercial_patterns, text),
            ScopeCategory.FAMILY_DIVORCE: self._find_matches(self._family_patterns, text),
            ScopeCategory.URGENT_INJUNCTION: self._find_matches(self._injunction_patterns, text),
            ScopeCategory.LABOR_EMPLOYMENT: self._find_matches(self._labor_patterns, text),
        }

        consumer_matches = self._find_matches(self._consumer_indicators, text)
        has_consumer_context = len(consumer_matches) >= 1

        has_livelihood_exception = bool(
            re.search(
                r"\b(?:livelihood|self-employed|self\s+employment|for\s+earning\s+(?:my\s+)?living)\b",
                text,
                re.I,
            )
        )

        # Priority 1: Cheque bounce under Section 138 (always out of scope for consumer forum)
        if matches[ScopeCategory.CHEQUE_BOUNCE]:
            triggers = matches[ScopeCategory.CHEQUE_BOUNCE]
            return ScopeResult(
                is_in_scope=False,
                out_of_scope_category=ScopeCategory.CHEQUE_BOUNCE.value,
                escalation_advice=self.ESCALATION_ADVICE[ScopeCategory.CHEQUE_BOUNCE],
                detected_triggers=triggers,
            )

        # Priority 2: Urgent stay / injunction (demolition / eviction)
        if matches[ScopeCategory.URGENT_INJUNCTION]:
            triggers = matches[ScopeCategory.URGENT_INJUNCTION]
            return ScopeResult(
                is_in_scope=False,
                out_of_scope_category=ScopeCategory.URGENT_INJUNCTION.value,
                escalation_advice=self.ESCALATION_ADVICE[ScopeCategory.URGENT_INJUNCTION],
                detected_triggers=triggers,
            )

        # Priority 3: Family / Matrimonial / Succession
        if matches[ScopeCategory.FAMILY_DIVORCE]:
            triggers = matches[ScopeCategory.FAMILY_DIVORCE]
            return ScopeResult(
                is_in_scope=False,
                out_of_scope_category=ScopeCategory.FAMILY_DIVORCE.value,
                escalation_advice=self.ESCALATION_ADVICE[ScopeCategory.FAMILY_DIVORCE],
                detected_triggers=triggers,
            )

        # Priority 4: Labor & Employment
        if matches[ScopeCategory.LABOR_EMPLOYMENT]:
            triggers = matches[ScopeCategory.LABOR_EMPLOYMENT]
            return ScopeResult(
                is_in_scope=False,
                out_of_scope_category=ScopeCategory.LABOR_EMPLOYMENT.value,
                escalation_advice=self.ESCALATION_ADVICE[ScopeCategory.LABOR_EMPLOYMENT],
                detected_triggers=triggers,
            )

        # Priority 5: Commercial B2B / IBC
        if matches[ScopeCategory.COMMERCIAL_B2B]:
            if has_livelihood_exception:
                return ScopeResult(
                    is_in_scope=True,
                    out_of_scope_category=None,
                    escalation_advice=None,
                    detected_triggers=["livelihood_exception_applied"],
                )
            triggers = matches[ScopeCategory.COMMERCIAL_B2B]
            return ScopeResult(
                is_in_scope=False,
                out_of_scope_category=ScopeCategory.COMMERCIAL_B2B.value,
                escalation_advice=self.ESCALATION_ADVICE[ScopeCategory.COMMERCIAL_B2B],
                detected_triggers=triggers,
            )

        # Priority 6: Criminal Offences (with Consumer Scam Reconciliation)
        if matches[ScopeCategory.CRIMINAL_OFFENSE]:
            triggers = matches[ScopeCategory.CRIMINAL_OFFENSE]

            violent_pattern = (
                r"\b(?:murder|assault|rape|violence|stabbed|pocso|fir|"
                r"first\s+information\s+report|police\s+station|arrest|bail|physically\s+attacked)\b"
            )
            violent_or_formal_police = any(re.search(violent_pattern, t, re.I) for t in triggers)
            direct_violent_or_police = bool(re.search(violent_pattern, text, re.I))

            if has_consumer_context and not (violent_or_formal_police or direct_violent_or_police):
                return ScopeResult(
                    is_in_scope=True,
                    out_of_scope_category=None,
                    escalation_advice=None,
                    detected_triggers=["consumer_unfair_trade_practice_override"],
                )

            return ScopeResult(
                is_in_scope=False,
                out_of_scope_category=ScopeCategory.CRIMINAL_OFFENSE.value,
                escalation_advice=self.ESCALATION_ADVICE[ScopeCategory.CRIMINAL_OFFENSE],
                detected_triggers=triggers,
            )

        if has_consumer_context or has_livelihood_exception:
            return ScopeResult(
                is_in_scope=True,
                out_of_scope_category=None,
                escalation_advice=None,
                detected_triggers=consumer_matches,
            )

        return None

    def _find_matches(self, patterns: list[re.Pattern[str]], text: str) -> list[str]:
        """Find unique matched terms for a list of regex patterns."""
        matched: list[str] = []
        for pat in patterns:
            for match in pat.finditer(text):
                val = match.group(0).strip().lower()
                if val not in matched:
                    matched.append(val)
        return matched

    def _classify_via_llm(self, text: str) -> ScopeResult:
        """Use fast LLM structured generation to classify ambiguous query."""
        assert self.llm_client is not None
        system_prompt = (
            "You are an Indian Legal Scope Classifier. Determine whether a dispute is an "
            "IN-SCOPE consumer dispute under the Consumer Protection Act, 2019 (buying goods or "
            "services for consideration, e-commerce orders, refund refusals, deficient services, "
            "or livelihood self-employment), or an OUT-OF-SCOPE legal matter: "
            "'criminal_offense', 'cheque_bounce', 'commercial_b2b', 'family_divorce', "
            "'labor_employment', or 'urgent_injunction'."
        )
        prompt = f'Dispute Text:\n"""\n{text}\n"""\nClassify the legal dispute scope:'
        output = self.llm_client.generate_structured(
            prompt=prompt,
            schema=ScopeClassificationOutput,
            system_prompt=system_prompt,
        )
        cat_enum = (
            ScopeCategory(output.category)
            if output.category in ScopeCategory._value2member_map_
            else ScopeCategory.OTHER_NON_CONSUMER
        )
        advice = self.ESCALATION_ADVICE.get(cat_enum) if not output.is_in_scope else None

        return ScopeResult(
            is_in_scope=output.is_in_scope,
            out_of_scope_category=output.category if not output.is_in_scope else None,
            escalation_advice=advice,
            detected_triggers=output.detected_triggers,
        )
