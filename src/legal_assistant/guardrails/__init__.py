"""Anti-hallucination and scope guardrails package for Legal Saathi."""

from legal_assistant.guardrails.scope_checker import (
    ScopeChecker,
    ScopeClassificationOutput,
)
from legal_assistant.guardrails.verifier import (
    CitationVerificationResult,
    CitationVerifier,
    RetrievalConfidenceGate,
    RetrievalUngroundedError,
)
from legal_assistant.rag.hybrid_retriever import (
    RetrievalConfidenceResult,
)
from legal_assistant.schemas import (
    ScopeCategory,
    ScopeResult,
    VerifiedResponse,
)

__all__ = [
    "CitationVerificationResult",
    "CitationVerifier",
    "RetrievalConfidenceGate",
    "RetrievalConfidenceResult",
    "RetrievalUngroundedError",
    "ScopeCategory",
    "ScopeChecker",
    "ScopeClassificationOutput",
    "ScopeResult",
    "VerifiedResponse",
]
