"""Anti-hallucination verification engine for Legal Saathi.

Contains Layer 2 (Retrieval Confidence Gate) and Layer 3 (Post-Generation
Citation Verifier) ensuring zero ungrounded statutory citations or fabricated
case precedents reach the consumer.
"""

from __future__ import annotations

import logging
import re
from typing import Literal, TypedDict

from pydantic import ConfigDict, Field

from legal_assistant.rag.hybrid_retriever import (
    RetrievalConfidenceResult,
    RetrievedChunk,
    StatutoryHybridRetriever,
)
from legal_assistant.schemas import VerifiedResponse

logger = logging.getLogger(__name__)


class ExtractedCitation(TypedDict):
    """Internal representation of an extracted statutory or judicial citation."""

    raw_text: str
    type: str
    canonical: str
    start: int
    end: int


class CitationVerificationResult(VerifiedResponse):
    """Structured result of post-generation statutory citation verification."""

    model_config = ConfigDict(extra="ignore")

    is_valid: bool = Field(
        default=True,
        description="True if citations were verified against corpus; False if hallucinated",
    )


class RetrievalUngroundedError(Exception):
    """Raised when retrieved context fails Layer 2 confidence threshold."""


class RetrievalConfidenceGate:
    """Layer 2 Anti-Hallucination Gate evaluating retrieval confidence and grounding."""

    def __init__(
        self,
        min_rrf_threshold: float = 0.012,
        abstention_message: str | None = None,
    ) -> None:
        """Initialize RetrievalConfidenceGate.

        Args:
            min_rrf_threshold: Minimum top RRF score to pass confidence gate (default: 0.012).
            abstention_message: Refusal notice returned upon gate failure.
        """
        self.min_rrf_threshold = min_rrf_threshold
        self.abstention_message = (
            abstention_message or StatutoryHybridRetriever.DEFAULT_ABSTENTION_MESSAGE
        )

    def evaluate(
        self,
        chunks: list[RetrievedChunk],
        query: str = "",
    ) -> RetrievalConfidenceResult:
        """Evaluate statutory grounding of retrieved candidates.

        Args:
            chunks: List of retrieved chunks from StatutoryHybridRetriever.
            query: User dispute query string.

        Returns:
            RetrievalConfidenceResult: Gate status and telemetry.
        """
        top_score = max((c.score for c in chunks), default=0.0)
        has_chunks = len(chunks) > 0
        score_passed = top_score >= self.min_rrf_threshold
        is_grounded = has_chunks and score_passed

        return RetrievalConfidenceResult(
            is_grounded=is_grounded,
            top_rrf_score=top_score,
            confidence_passed=is_grounded,
            retrieved_chunk_count=len(chunks),
            abstention_triggered=not is_grounded,
            abstention_message=None if is_grounded else self.abstention_message,
        )

    def is_grounded(self, chunks: list[RetrievedChunk]) -> bool:
        """Check if chunks clear retrieval confidence gate."""
        return self.evaluate(chunks).is_grounded

    def get_abstention_response_if_ungrounded(
        self,
        chunks: list[RetrievedChunk],
        query: str = "",
    ) -> str | None:
        """Return abstention message if ungrounded, or None if grounded."""
        eval_result = self.evaluate(chunks, query=query)
        if eval_result.abstention_triggered:
            return eval_result.abstention_message
        return None


class CitationVerifier:
    """Layer 3 Anti-Hallucination Verifier validating statutory citations and case laws."""

    # Robust regular expressions for citation extraction
    _CPA_SECTION_PATTERN = re.compile(
        r"\b(?:Section|Sec\.?|s\.)\s*(\d+[A-Z]?(?:\([a-zA-Z0-9]+\))*"
        r"(?:\s*(?:and|&|,)\s*\d+[A-Z]?(?:\([a-zA-Z0-9]+\))*)*)"
        r"|(?:\b(?:Sections|Secs\.?)\s*(\d+[A-Z]?(?:\([a-zA-Z0-9]+\))*(?:\s*(?:and|&|,)\s*\d+[A-Z]?(?:\([a-zA-Z0-9]+\))*)*))",
        re.IGNORECASE,
    )

    _ECOMMERCE_RULE_PATTERN = re.compile(
        r"\b(?:Rules|Rule|r\.)\s*(\d+[A-Z]?(?:\([a-zA-Z0-9]+\))*(?:\s*(?:and|&|,)\s*\d+[A-Z]?(?:\([a-zA-Z0-9]+\))*)*)",
        re.IGNORECASE,
    )

    _CCPA_GUIDELINE_PATTERN = re.compile(
        r"\b(?:CCPA|Central Consumer Protection Authority)\b"
        r"(?:\s+(?:Guidelines|Order|Notification|Regulations|Rules))?(?:\s*,?\s*\d{4})?",
        re.IGNORECASE,
    )

    _REPEALED_ACT_PATTERN = re.compile(
        r"\b(?:Consumer\s+Protection\s+Act,?\s*1986|CPA,?\s*1986|Act\s+of\s+1986)\b",
        re.IGNORECASE,
    )

    _CASE_LAW_PATTERN = re.compile(
        r"\b([A-Z][a-zA-Z0-9\.\s]{2,40}\s+(?:v\.|vs\.?|versus)\s+[A-Z][a-zA-Z0-9\.\s]{2,40}(?:,?\s*(?:\(\d{4}\)|\d{4})[^\.\n;]*)?)"
        r"|(?:(?:\b|\()(?:\d{4}\)|\d{4})|\(\d{4}\))\s*(?:\d+\s+)?(?:SCC|CPJ|CPR|AIR|SCR|SCALE)\s*(?:\d+|[A-Z]+(?:\s*\d+)?)(?:\s+(?:SC|NCDRC|NC|SCDRC|HC|[A-Z]{2,10}))?",
        re.IGNORECASE,
    )

    def __init__(self, default_action: Literal["flag", "strip"] = "flag") -> None:
        """Initialize CitationVerifier.

        Args:
            default_action: Default action for ungrounded citations ('flag' or 'strip').
        """
        self.default_action = default_action

    def verify_response(
        self,
        response_text: str,
        source_chunks: list[RetrievedChunk],
        action: Literal["flag", "strip"] | None = None,
        flag_mode: Literal["flag", "strip"] | None = None,
    ) -> VerifiedResponse:
        """Verify statutory citations in response text against retrieved chunks.

        Extracts all cited Sections, Rules, Guidelines, Repealed Act references,
        and Case Precedents. Checks their physical existence in source_chunks
        metadata and content. Flags or strips ungrounded or fabricated citations.

        Args:
            response_text: Generated response text from LLM.
            source_chunks: Ground-truth RetrievedChunk instances from RAG engine.
            action: 'flag' (wraps with <flag>) or 'strip' (removes citation).
            flag_mode: Alias for action ('flag' or 'strip').

        Returns:
            VerifiedResponse: Sanitized response and citation telemetry.
        """
        act = action or flag_mode or self.default_action
        result = self.verify_citations(response_text, source_chunks, action=act)
        return VerifiedResponse(
            cleaned_text=result.cleaned_text,
            verified_citations=result.verified_citations,
            flagged_citations=result.flagged_citations,
            hallucination_detected=result.hallucination_detected,
            warning_message=result.warning_message,
        )

    def verify_citations(
        self,
        response_text: str,
        source_chunks: list[RetrievedChunk],
        action: Literal["flag", "strip"] | None = None,
        flag_mode: Literal["flag", "strip"] | None = None,
    ) -> CitationVerificationResult:
        """Perform comprehensive citation verification and return CitationVerificationResult.

        Args:
            response_text: Response text to verify.
            source_chunks: Retrieved ground-truth chunks.
            action: Action on invalid citations ('flag' or 'strip').
            flag_mode: Alias for action.

        Returns:
            CitationVerificationResult: Complete verification result with is_valid flag.
        """
        if not response_text or not response_text.strip():
            return CitationVerificationResult(
                is_valid=True,
                cleaned_text=response_text,
                verified_citations=[],
                flagged_citations=[],
                hallucination_detected=False,
                warning_message=None,
            )

        act = action or flag_mode or self.default_action

        # 1. Build Ground Truth Index from source chunks
        ground_truth_sections: set[str] = set()
        ground_truth_contents_lower: list[str] = []

        for chunk in source_chunks:
            sec = str(chunk.section).strip().lower()
            if sec:
                ground_truth_sections.add(sec)
                # Normalize Section 2(47) -> 2(47)
                norm_sec = re.sub(
                    r"^(?:sections?|sec\.?|rules?|r\.)\s*", "", sec, flags=re.I
                ).strip()
                ground_truth_sections.add(norm_sec)
                # Parent section: e.g. 2(47)(viii) -> 2(47)
                parent_match = re.match(r"^(\d+[a-z]?(?:\([a-z0-9]+\)))", norm_sec)
                if parent_match:
                    ground_truth_sections.add(parent_match.group(1))

            content_lower = chunk.content.lower()
            ground_truth_contents_lower.append(content_lower)

        # 2. Extract Citations from text
        extracted_citations = self._extract_citations(response_text)

        verified_citations: list[str] = []
        flagged_citations: list[str] = []
        replacements: list[tuple[int, int, str]] = []

        # 3. Cross-verify each citation against ground truth
        for citation_info in extracted_citations:
            raw_citation = citation_info["raw_text"]
            cit_type = citation_info["type"]
            canonical = citation_info["canonical"]
            start_pos = citation_info["start"]
            end_pos = citation_info["end"]

            is_verified = self._is_citation_grounded(
                cit_type=cit_type,
                canonical=canonical,
                raw_text=raw_citation,
                ground_truth_sections=ground_truth_sections,
                ground_truth_contents=ground_truth_contents_lower,
            )

            if is_verified:
                if raw_citation not in verified_citations:
                    verified_citations.append(raw_citation)
            else:
                if raw_citation not in flagged_citations:
                    flagged_citations.append(raw_citation)

                # Prepare replacement string
                if act == "flag":
                    replacement_str = f"<flag>{raw_citation}: Unverified citation</flag>"
                else:
                    replacement_str = "[Citation omitted - unverified in statutory corpus]"
                replacements.append((start_pos, end_pos, replacement_str))

        # Perform span-based sanitization in reverse start-position order
        # to prevent nested tags or offset corruption
        cleaned_text = response_text
        for start_pos, end_pos, repl_str in sorted(replacements, key=lambda x: x[0], reverse=True):
            cleaned_text = cleaned_text[:start_pos] + repl_str + cleaned_text[end_pos:]

        hallucination_detected = len(flagged_citations) > 0
        warning_msg = (
            f"Warning: {len(flagged_citations)} unverified citation(s) detected and {act}ged."
            if hallucination_detected
            else None
        )

        return CitationVerificationResult(
            is_valid=not hallucination_detected,
            cleaned_text=cleaned_text,
            verified_citations=verified_citations,
            flagged_citations=flagged_citations,
            hallucination_detected=hallucination_detected,
            warning_message=warning_msg,
        )

    def _extract_citations(self, text: str) -> list[ExtractedCitation]:
        """Extract all statutory sections, rules, guidelines, and precedents."""
        citations: list[ExtractedCitation] = []
        seen_spans: list[tuple[int, int]] = []

        def _overlaps(start: int, end: int) -> bool:
            return any(max(start, s) < min(end, e) for s, e in seen_spans)

        # 1. Repealed CPA 1986 references (Always caught)
        for match in self._REPEALED_ACT_PATTERN.finditer(text):
            span = match.span()
            if _overlaps(span[0], span[1]):
                continue
            seen_spans.append(span)
            raw = match.group(0).strip()
            citations.append(
                {
                    "raw_text": raw,
                    "type": "repealed_act",
                    "canonical": raw.lower(),
                    "start": span[0],
                    "end": span[1],
                }
            )

        # 2. Statutory Sections (CPA 2019)
        for match in self._CPA_SECTION_PATTERN.finditer(text):
            span = match.span()
            if _overlaps(span[0], span[1]):
                continue
            seen_spans.append(span)
            raw = match.group(0).strip()
            clean_sec = re.sub(
                r"^(?:sections|section|secs\.?|sec\.?|s\.)\s*", "", raw, flags=re.I
            ).strip()
            citations.append(
                {
                    "raw_text": raw,
                    "type": "section",
                    "canonical": clean_sec.lower(),
                    "start": span[0],
                    "end": span[1],
                }
            )

        # 3. E-Commerce Rules
        for match in self._ECOMMERCE_RULE_PATTERN.finditer(text):
            span = match.span()
            if _overlaps(span[0], span[1]):
                continue
            seen_spans.append(span)
            raw = match.group(0).strip()
            clean_rule = re.sub(r"^(?:rules|rule|r\.)\s*", "", raw, flags=re.I).strip()
            citations.append(
                {
                    "raw_text": raw,
                    "type": "rule",
                    "canonical": clean_rule.lower(),
                    "start": span[0],
                    "end": span[1],
                }
            )

        # 4. CCPA Guidelines / Orders
        for match in self._CCPA_GUIDELINE_PATTERN.finditer(text):
            span = match.span()
            if _overlaps(span[0], span[1]):
                continue
            seen_spans.append(span)
            raw = match.group(0).strip()
            citations.append(
                {
                    "raw_text": raw,
                    "type": "ccpa_guideline",
                    "canonical": raw.lower(),
                    "start": span[0],
                    "end": span[1],
                }
            )

        # 5. Case Laws / Fabricated Precedents
        for match in self._CASE_LAW_PATTERN.finditer(text):
            span = match.span()
            if _overlaps(span[0], span[1]):
                continue
            seen_spans.append(span)
            raw = match.group(0).strip()
            citations.append(
                {
                    "raw_text": raw,
                    "type": "case_law",
                    "canonical": raw.lower(),
                    "start": span[0],
                    "end": span[1],
                }
            )

        return citations

    def _is_citation_grounded(
        self,
        cit_type: str,
        canonical: str,
        raw_text: str,
        ground_truth_sections: set[str],
        ground_truth_contents: list[str],
    ) -> bool:
        """Check if a citation physically exists in the retrieved statutory chunks."""
        # Repealed act is never grounded in modern CPA 2019 corpus
        if cit_type == "repealed_act":
            return False

        # CCPA Guidelines / Orders
        if cit_type == "ccpa_guideline":
            return any(
                "ccpa" in content or "central consumer protection authority" in content
                for content in ground_truth_contents
            )

        # Case Law Precedent Check
        if cit_type == "case_law":
            clean_raw = raw_text.lower().strip()
            return any(clean_raw in content for content in ground_truth_contents)

        # Rule / Section Check
        if cit_type in ("section", "rule"):
            # Check for plural citations: e.g. "35 and 36" or "2(11) and 2(47)"
            sub_canonical = [
                s.strip() for s in re.split(r"\s*(?:and|&|,)\s*", canonical) if s.strip()
            ]
            if len(sub_canonical) > 1:
                return all(
                    self._is_single_provision_grounded(
                        sub, ground_truth_sections, ground_truth_contents
                    )
                    for sub in sub_canonical
                )

            return self._is_single_provision_grounded(
                canonical, ground_truth_sections, ground_truth_contents
            )

        return False

    def _is_single_provision_grounded(
        self,
        canonical: str,
        ground_truth_sections: set[str],
        ground_truth_contents: list[str],
    ) -> bool:
        """Verify an individual section or rule provision."""
        clean_can = canonical.lower().strip()
        norm_can = re.sub(r"^(?:rules?|r\.)\s*", "", clean_can).strip()

        # 1. Exact match in chunk section metadata
        if (
            clean_can in ground_truth_sections
            or norm_can in ground_truth_sections
            or f"section {norm_can}" in ground_truth_sections
            or f"rule {norm_can}" in ground_truth_sections
        ):
            return True

        # 2. Check base section with subclause (e.g. 2(47)(xyz999) vs 2(47))
        base_match = re.match(r"^(\d+[a-z]?(?:\([a-z0-9]+\)))", norm_can)
        if base_match:
            base_sec = base_match.group(1)
            # If citation claims a subclause beyond base section (e.g. 2(47)(xyz999)):
            if len(norm_can) > len(base_sec):
                subclause = norm_can[len(base_sec) :]
                # Base section must be verified in metadata, AND subclause must be in content
                if (
                    base_sec in ground_truth_sections
                    or f"section {base_sec}" in ground_truth_sections
                ):
                    sub_escaped = re.escape(subclause)
                    sub_pat = re.compile(rf"{sub_escaped}(?!\w)", re.I)
                    return any(sub_pat.search(content) for content in ground_truth_contents)
            else:
                # Citation is the base section itself (e.g. 2(47))
                if (
                    base_sec in ground_truth_sections
                    or f"section {base_sec}" in ground_truth_sections
                ):
                    return True

        # 3. Direct mention in chunk content with statutory prefix and word boundary
        escaped = re.escape(norm_can)
        sec_pattern = re.compile(
            rf"\b(?:sections?|sec\.?|s\.|rules?|r\.)\s*{escaped}(?!\w|\()",
            re.I,
        )
        return any(sec_pattern.search(content) for content in ground_truth_contents)
