"""Retrieval-Augmented Generation (RAG) module for Indian Consumer Law.

Provides structure-aware statutory chunking, hybrid BM25 + dense retrieval with
Reciprocal Rank Fusion (RRF), confidence-gated abstention, and a Kotaemon
theflow-compatible bridge adapter with dual-channel streaming.
"""

from __future__ import annotations

from legal_assistant.rag.chunker import (
    BaseSplitter,
    Document,
    StatutoryChunk,
    StatutoryChunker,
    StatutoryChunkMetadata,
)
from legal_assistant.rag.hybrid_retriever import (
    BaseDenseRetriever,
    ChromaDenseRetriever,
    InMemoryDenseRetriever,
    LegalTokenizer,
    RetrievalConfidenceResult,
    RetrievedChunk,
    StatutoryHybridRetriever,
)
from legal_assistant.rag.kotaemon_bridge import (
    KotaemonDocument,
    KotaemonLegalBridge,
    KotaemonRetrievedDocument,
    RetrievedDocument,
)

__all__ = [
    "BaseDenseRetriever",
    "BaseSplitter",
    "ChromaDenseRetriever",
    "Document",
    "InMemoryDenseRetriever",
    "KotaemonDocument",
    "KotaemonLegalBridge",
    "KotaemonRetrievedDocument",
    "LegalTokenizer",
    "RetrievalConfidenceResult",
    "RetrievedChunk",
    "RetrievedDocument",
    "StatutoryChunk",
    "StatutoryChunkMetadata",
    "StatutoryChunker",
    "StatutoryHybridRetriever",
]
