"""Hybrid BM25 and Dense Vector Retriever with Reciprocal Rank Fusion (RRF).

This module implements a production-grade legal hybrid retriever designed for
Indian consumer law statutes. It combines rank_bm25.BM25Okapi using a specialized
legal tokenizer with dense vector retrieval (Chroma / InMemory), fused via
Reciprocal Rank Fusion (RRF).
"""

from __future__ import annotations

import math
import os
import re
import zlib
from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from typing import Any

import numpy as np
from pydantic import BaseModel, Field
from rank_bm25 import BM25Okapi


class LegalTokenizer:
    """Specialized tokenizer preserving Indian statutory and currency notation."""

    STOPWORDS: frozenset[str] = frozenset(
        {
            "a",
            "about",
            "above",
            "after",
            "again",
            "against",
            "all",
            "am",
            "an",
            "and",
            "any",
            "are",
            "aren't",
            "as",
            "at",
            "be",
            "because",
            "been",
            "before",
            "being",
            "below",
            "between",
            "both",
            "but",
            "by",
            "can",
            "can't",
            "cannot",
            "could",
            "couldn't",
            "did",
            "didn't",
            "do",
            "does",
            "doesn't",
            "doing",
            "don't",
            "down",
            "during",
            "each",
            "few",
            "for",
            "from",
            "further",
            "had",
            "hadn't",
            "has",
            "hasn't",
            "have",
            "haven't",
            "having",
            "he",
            "he'd",
            "he'll",
            "he's",
            "her",
            "here",
            "here's",
            "hers",
            "herself",
            "him",
            "himself",
            "his",
            "how",
            "how's",
            "i",
            "i'd",
            "i'll",
            "i'm",
            "i've",
            "if",
            "in",
            "into",
            "is",
            "isn't",
            "it",
            "it's",
            "its",
            "itself",
            "let's",
            "me",
            "more",
            "most",
            "mustn't",
            "my",
            "myself",
            "no",
            "nor",
            "not",
            "of",
            "off",
            "on",
            "once",
            "only",
            "or",
            "other",
            "ought",
            "our",
            "ours",
            "ourselves",
            "out",
            "over",
            "own",
            "same",
            "shan't",
            "she",
            "she'd",
            "she'll",
            "she's",
            "should",
            "shouldn't",
            "so",
            "some",
            "such",
            "than",
            "that",
            "that's",
            "the",
            "their",
            "theirs",
            "them",
            "themselves",
            "then",
            "there",
            "there's",
            "these",
            "they",
            "they'd",
            "they'll",
            "they're",
            "they've",
            "this",
            "those",
            "through",
            "to",
            "too",
            "under",
            "until",
            "up",
            "very",
            "was",
            "wasn't",
            "we",
            "we'd",
            "we'll",
            "we're",
            "we've",
            "were",
            "weren't",
            "what",
            "what's",
            "when",
            "when's",
            "where",
            "where's",
            "which",
            "while",
            "who",
            "who's",
            "whom",
            "why",
            "why's",
            "with",
            "won't",
            "would",
            "wouldn't",
            "you",
            "you'd",
            "you'll",
            "you're",
            "you've",
            "your",
            "yours",
            "yourself",
            "yourselves",
        }
    )

    _TOKEN_PATTERN = re.compile(
        # 1. Currency (₹4,500, ₹50,000, ₹50L, ₹2Cr, Rs. 5000, Rs.50,000)
        r"(?:₹|Rs\.?)\s*\d+(?:,\d+)*(?:\.\d+)?(?:\s*(?:L|Cr|k|lakhs?|crores?)\b)?"
        # 2. Statutory Section / Rule notation (Section 2(47), Sec. 34(2)(d), Rule 4(5))
        r"|(?:(?:Section|Sec\.?|Rule)\s*)?\b\d+[A-Z]?(?:\([a-zA-Z0-9]+\))+"
        # 3. Hyphenated legal terms (e-commerce, e-daakhil, pro-rata, charge-back)
        r"|\b[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)+\b"
        # 4. Standard words and acronyms (CPA, 2019, NCH, 1915, BNS)
        r"|\b[a-zA-Z0-9_]+\b",
        re.IGNORECASE,
    )

    _SECTION_CANONICAL = re.compile(
        r"^(?:section|sec\.?|rule)\s*(\d+[a-z]?(?:\([a-z0-9]+\))+)$",
        re.IGNORECASE,
    )

    _BARE_SECTION = re.compile(
        r"^\d+[a-z]?(?:\([a-z0-9]+\))+$",
        re.IGNORECASE,
    )

    @classmethod
    def tokenize(cls, text: str) -> list[str]:
        """Tokenize legal text while preserving statutory identifiers and currency.

        Args:
            text: Raw input text query or statutory passage.

        Returns:
            list[str]: Normalized lowercased string tokens.
        """
        if not text or not text.strip():
            return []

        tokens: list[str] = []
        for raw_match in cls._TOKEN_PATTERN.findall(text):
            match_str = raw_match.strip().lower()

            # Canonicalize Section / Rule notation (e.g. 'Section 2(47)' -> '2(47)', 'sec_2(47)')
            sec_match = cls._SECTION_CANONICAL.match(match_str)
            if sec_match:
                sec_num = sec_match.group(1)
                tokens.append(sec_num)
                is_rule = "rule" in match_str
                tokens.append(f"rule_{sec_num}" if is_rule else f"sec_{sec_num}")
                tokens.append("rule" if is_rule else "section")
                continue

            if cls._BARE_SECTION.match(match_str):
                tokens.append(match_str)
                tokens.append(f"sec_{match_str}")
                continue

            # Canonicalize Currency notation (e.g. '₹4,500' -> '₹4,500' and '₹4500')
            if match_str.startswith("₹") or match_str.startswith("rs"):
                collapsed = re.sub(r"[\s,]", "", match_str)
                tokens.append(collapsed)
                if match_str != collapsed:
                    tokens.append(match_str.replace(" ", ""))
                continue

            # Filter standard English stopwords carrying no statutory semantics
            if (
                match_str in cls.STOPWORDS
                and not match_str.startswith("sec_")
                and not match_str.startswith("rule_")
                and not any(ch.isdigit() for ch in match_str)
            ):
                continue

            tokens.append(match_str)

        return tokens


class RetrievedChunk(BaseModel):
    """Normalized statutory chunk retrieved by the hybrid search engine."""

    chunk_id: str = Field(description="Unique identifier for the statutory chunk")
    content: str = Field(description="Full text of statutory chunk with breadcrumb header")
    statute: str = Field(description="Name of statute, e.g. 'Consumer Protection Act, 2019'")
    chapter: str = Field(default="", description="Chapter identifier or title")
    section: str = Field(description="Section or Rule number, e.g. '2(47)', 'Rule 4(5)'")
    title: str = Field(
        default="",
        description="Section or Rule title, e.g. 'Unfair Trade Practice'",
    )
    score: float = Field(description="Fused RRF score")
    rank: int = Field(default=1, description="1-based ordinal rank in final fused list")
    retrieval_method: str = Field(
        default="hybrid_rrf",
        description="Retrieval source: hybrid_rrf, bm25, dense",
    )
    bm25_rank: int | None = Field(default=None, description="Original 1-based rank from BM25")
    dense_rank: int | None = Field(default=None, description="Original 1-based rank from Dense")
    bm25_score: float | None = Field(default=None, description="Raw BM25 Okapi score")
    dense_score: float | None = Field(default=None, description="Cosine similarity score")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional statutory metadata"
    )


class RetrievalConfidenceResult(BaseModel):
    """Confidence evaluation result for Layer 2 Anti-Hallucination Gate."""

    is_grounded: bool = Field(
        description="Whether retrieved chunks provide sufficient legal grounding"
    )
    top_rrf_score: float = Field(description="Top RRF score among retrieved candidates")
    confidence_passed: bool = Field(description="True if top_rrf_score >= confidence_threshold")
    retrieved_chunk_count: int = Field(description="Count of retrieved chunks meeting threshold")
    abstention_triggered: bool = Field(description="True if generation must be halted")
    abstention_message: str | None = Field(
        default=None, description="User-facing refusal notice if abstaining"
    )


def _get_chunk_id(chunk: Any, fallback: str) -> str:
    """Extract canonical chunk identifier from various chunk schemas uniformly.

    Args:
        chunk: Chunk, StatutoryChunk, Document, or compatible object.
        fallback: Fallback identifier if no ID attributes are present.

    Returns:
        str: Canonical chunk identifier.
    """
    meta = getattr(chunk, "metadata", {})
    meta_id = meta.get("chunk_id") if isinstance(meta, dict) else getattr(meta, "chunk_id", None)
    return getattr(chunk, "chunk_id", None) or getattr(chunk, "doc_id", None) or meta_id or fallback


class BaseDenseRetriever(ABC):
    """Abstract interface for dense semantic retrievers."""

    @abstractmethod
    def index(self, chunks: Sequence[Any]) -> None:
        """Index statutory chunks and store vector representations.

        Args:
            chunks: Sequence of statutory chunks or document objects.
        """
        pass

    @abstractmethod
    def search(self, query: str, top_k: int) -> list[tuple[Any, float]]:
        """Search index and return top-k tuples of (chunk, cosine_similarity).

        Args:
            query: User search query.
            top_k: Number of nearest matches to return.

        Returns:
            list[tuple[Any, float]]: Top matches with cosine similarities.
        """
        pass


class InMemoryDenseRetriever(BaseDenseRetriever):
    """Pure Python / NumPy dense retriever for isolated testing and native Windows."""

    def __init__(
        self,
        embed_fn: Callable[[list[str]], list[list[float]]] | None = None,
        embedding_dim: int = 4096,
    ) -> None:
        """Initialize InMemoryDenseRetriever.

        Args:
            embed_fn: Optional custom embedding function. If None, uses
                deterministic hash embedding.
            embedding_dim: Dimensionality for hash embeddings.
        """
        self.embed_fn = embed_fn or self._default_hash_embed
        self.dim = embedding_dim
        self.chunks: list[Any] = []
        self.embeddings: np.ndarray | None = None

    def _default_hash_embed(self, texts: list[str]) -> list[list[float]]:
        """Deterministic N-gram hash embedding for zero-dependency test execution.

        Args:
            texts: List of text strings to embed.

        Returns:
            list[list[float]]: L2-normalized vector embeddings.
        """
        results: list[list[float]] = []
        for text in texts:
            vec = [0.0] * self.dim
            tokens = LegalTokenizer.tokenize(text)
            if not tokens:
                results.append(vec)
                continue
            for token in tokens:
                idx = zlib.crc32(token.encode("utf-8")) % self.dim
                vec[idx] += 1.0
            norm = math.sqrt(sum(x * x for x in vec))
            if norm > 0.0:
                vec = [x / norm for x in vec]
            results.append(vec)
        return results

    def index(self, chunks: Sequence[Any]) -> None:
        """Index statutory chunks into in-memory vector store.

        Args:
            chunks: Sequence of chunk objects to index.
        """
        self.chunks = list(chunks)
        if not self.chunks:
            self.embeddings = None
            return
        texts = [
            getattr(c, "content", None) or getattr(c, "text", None) or str(c) for c in self.chunks
        ]
        emb_list = self.embed_fn(texts)
        self.embeddings = np.array(emb_list, dtype=np.float32)

    def search(self, query: str, top_k: int) -> list[tuple[Any, float]]:
        """Perform cosine similarity search against indexed chunks.

        Args:
            query: Search query text.
            top_k: Number of top results to return.

        Returns:
            list[tuple[Any, float]]: Sorted (chunk, score) pairs.
        """
        if not self.chunks or self.embeddings is None:
            return []

        query_emb = np.array(self.embed_fn([query])[0], dtype=np.float32)
        norm_q = float(np.linalg.norm(query_emb))
        if norm_q > 0.0:
            query_emb = query_emb / norm_q

        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        norms[norms == 0.0] = 1.0
        normalized_embeddings = self.embeddings / norms

        similarities = np.dot(normalized_embeddings, query_emb)
        top_indices = np.argsort(similarities)[::-1][:top_k]

        return [(self.chunks[i], float(similarities[i])) for i in top_indices]


class ChromaDenseRetriever(BaseDenseRetriever):
    """ChromaDB dense retriever compatible with native Windows."""

    def __init__(
        self,
        collection_name: str = "statutory_corpus",
        persist_dir: str | None = None,
        embed_fn: Callable[[list[str]], list[list[float]]] | None = None,
    ) -> None:
        """Initialize ChromaDenseRetriever.

        Args:
            collection_name: Name of Chroma collection.
            persist_dir: Optional path for persistent SQLite storage. If None,
                uses EphemeralClient.
            embed_fn: Optional embedding function. If None, uses fast in-memory
                hash embedder to prevent external ONNX model downloads.
        """
        os.environ["ANONYMIZED_TELEMETRY"] = "False"
        import chromadb
        from chromadb.config import Settings

        # Default to InMemoryDenseRetriever hash embedder to avoid remote model downloads
        if embed_fn is None:
            in_mem = InMemoryDenseRetriever()
            self.embed_fn: Callable[[list[str]], list[list[float]]] = in_mem._default_hash_embed
        else:
            self.embed_fn = embed_fn

        settings = Settings(anonymized_telemetry=False)
        if persist_dir:
            self.client = chromadb.PersistentClient(path=persist_dir, settings=settings)
        else:
            self.client = chromadb.EphemeralClient(settings=settings)

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        self.chunk_map: dict[str, Any] = {}

    def index(self, chunks: Sequence[Any]) -> None:
        """Index chunks into Chroma collection.

        Args:
            chunks: Sequence of chunks to index.
        """
        self.chunk_map.clear()
        if not chunks:
            return

        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict[str, str | int | float | bool]] = []

        for i, chunk in enumerate(chunks):
            cid = _get_chunk_id(chunk, f"chunk_{i}")
            content = getattr(chunk, "content", None) or getattr(chunk, "text", None) or str(chunk)
            self.chunk_map[cid] = chunk

            raw_meta = getattr(chunk, "metadata", {})
            if isinstance(raw_meta, BaseModel):
                meta_dict: dict[str, Any] = raw_meta.model_dump()
            elif isinstance(raw_meta, dict):
                meta_dict = dict(raw_meta)
            else:
                meta_dict = {}

            # Chroma requires string/int/float/bool in metadatas
            clean_meta: dict[str, str | int | float | bool] = {
                k: str(v) for k, v in meta_dict.items() if not isinstance(v, (int, float, bool))
            }
            for k, v in meta_dict.items():
                if isinstance(v, (int, float, bool)):
                    clean_meta[k] = v

            if not clean_meta:
                clean_meta["chunk_id"] = cid

            ids.append(cid)
            documents.append(content)
            metadatas.append(clean_meta)

        embeddings_list: list[list[float]] = self.embed_fn(documents)
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,  # type: ignore[arg-type]
            embeddings=embeddings_list,  # type: ignore[arg-type]
        )

    def search(self, query: str, top_k: int) -> list[tuple[Any, float]]:
        """Query Chroma collection returning top-k nearest neighbors.

        Args:
            query: Search query text.
            top_k: Number of top results to return.

        Returns:
            list[tuple[Any, float]]: Retrieved chunks with cosine similarities.
        """
        query_embeddings = self.embed_fn([query])
        results = self.collection.query(
            query_embeddings=query_embeddings,  # type: ignore[arg-type]
            n_results=top_k,
        )

        if not results["ids"] or not results["ids"][0]:
            return []

        matched_ids = results["ids"][0]
        distances_matrix = results.get("distances")
        distances: list[float] = (
            distances_matrix[0]
            if distances_matrix is not None and len(distances_matrix) > 0
            else [0.0] * len(matched_ids)
        )

        hits: list[tuple[Any, float]] = []
        for cid, dist in zip(matched_ids, distances, strict=False):
            chunk = self.chunk_map.get(cid)
            sim = 1.0 - float(dist)
            hits.append((chunk, sim))

        return hits


class StatutoryHybridRetriever:
    """Hybrid BM25 + Dense vector search with genuine Reciprocal Rank Fusion (RRF)."""

    DEFAULT_ABSTENTION_MESSAGE = (
        "I am unable to locate verified statutory provisions in the Consumer Protection Act, "
        "2019 or the E-Commerce Rules, 2020 directly governing your query. To protect you against "
        "inaccurate legal guidance, I will not generate an unsubstantiated answer. Please seek "
        "guidance from a consumer law advocate or file a query with the "
        "National Consumer Helpline at 1915."
    )

    def __init__(
        self,
        chunks: Sequence[Any] | None = None,
        dense_retriever: BaseDenseRetriever | None = None,
        rrf_k: int = 60,
        w_bm25: float = 1.0,
        w_dense: float = 1.0,
        min_confidence_threshold: float = 0.012,
    ) -> None:
        """Initialize StatutoryHybridRetriever.

        Args:
            chunks: Optional initial statutory chunks to index.
            dense_retriever: Dense retriever instance (InMemoryDenseRetriever if None).
            rrf_k: Reciprocal rank fusion smoothing parameter (default: 60).
            w_bm25: Weight assigned to lexical BM25 ranks (default: 1.0).
            w_dense: Weight assigned to dense semantic ranks (default: 1.0).
            min_confidence_threshold: Minimum top RRF score to clear retrieval
                confidence gate.
        """
        self.rrf_k = rrf_k
        self.w_bm25 = w_bm25
        self.w_dense = w_dense
        self.confidence_threshold = min_confidence_threshold

        self.dense_retriever = dense_retriever or InMemoryDenseRetriever()
        self.bm25_index: BM25Okapi | None = None
        self.indexed_chunks: list[Any] = []
        self.chunk_lookup: dict[str, Any] = {}

        if chunks:
            self.index_chunks(chunks)

    def index_chunks(self, chunks: Sequence[Any]) -> None:
        """Index statutory chunks across BM25 and Dense vector backends.

        Args:
            chunks: Sequence of StatutoryChunk or compatible document objects.
        """
        self.indexed_chunks = list(chunks)
        self.chunk_lookup.clear()

        tokenized_corpus: list[list[str]] = []
        for i, chunk in enumerate(self.indexed_chunks):
            cid = _get_chunk_id(chunk, f"chunk_{i}")
            self.chunk_lookup[cid] = chunk
            content = getattr(chunk, "content", None) or getattr(chunk, "text", None) or str(chunk)
            tokens = LegalTokenizer.tokenize(content)
            tokenized_corpus.append(tokens)

        if tokenized_corpus:
            self.bm25_index = BM25Okapi(tokenized_corpus)
        else:
            self.bm25_index = None

        self.dense_retriever.index(self.indexed_chunks)

    def _extract_chunk_attributes(self, chunk: Any, default_id: str) -> dict[str, Any]:
        """Safely extract statutory metadata from a chunk object.

        Args:
            chunk: Chunk or Document object.
            default_id: Fallback identifier.

        Returns:
            dict[str, Any]: Dictionary of statutory attributes.
        """
        cid = _get_chunk_id(chunk, default_id)
        content = getattr(chunk, "content", None) or getattr(chunk, "text", None) or str(chunk)

        meta = getattr(chunk, "metadata", {})
        if isinstance(meta, BaseModel):
            meta_dict: dict[str, Any] = meta.model_dump()
        elif isinstance(meta, dict):
            meta_dict = dict(meta)
        else:
            meta_dict = {}

        statute = (
            getattr(chunk, "statute", None)
            or meta_dict.get("statute_id")
            or meta_dict.get("statute")
            or "Consumer Protection Law"
        )
        chapter = (
            getattr(chunk, "chapter", None)
            or meta_dict.get("chapter_title")
            or meta_dict.get("chapter_number")
            or meta_dict.get("chapter")
            or ""
        )
        section = (
            getattr(chunk, "section", None)
            or meta_dict.get("section_number")
            or meta_dict.get("section")
            or "General"
        )
        title = (
            getattr(chunk, "title", None)
            or meta_dict.get("section_title")
            or meta_dict.get("title")
            or ""
        )

        return {
            "chunk_id": cid,
            "content": content,
            "statute": str(statute),
            "chapter": str(chapter),
            "section": str(section),
            "title": str(title),
            "metadata": meta_dict,
        }

    @staticmethod
    def _extract_target_sections(query: str) -> list[str]:
        """Extract canonical statutory section citations from a query string.

        Args:
            query: Query string.

        Returns:
            list[str]: Normalized lowercased section citations.
        """
        targets: list[str] = []
        # Matches 'Section 2(47)', 'Sec. 34(2)(d)', 'Rule 4(5)', 'Rule 8', 'Sec 35'
        for m in re.finditer(
            r"(?:section|sec\.?|rule)\s*(\d+[a-z]?(?:\([a-z0-9]+\))*|\d+)",
            query,
            re.IGNORECASE,
        ):
            targets.append(m.group(1).lower().replace(" ", ""))
        # Matches standalone parenthesized section citations like '2(47)', '34(2)(d)', '4(5)'
        for m in re.finditer(r"\b\d+[a-z]?(?:\([a-z0-9]+\))+", query, re.IGNORECASE):
            norm = m.group(0).lower().replace(" ", "")
            if norm not in targets:
                targets.append(norm)
        return targets

    @classmethod
    def _chunk_matches_target_section(cls, chunk: Any, targets: list[str]) -> bool:
        """Check if chunk's primary section matches an exact query section target.

        Args:
            chunk: StatutoryChunk or Document object.
            targets: List of normalized target section citations.

        Returns:
            bool: True if chunk's metadata section matches any target citation.
        """
        if not targets:
            return False
        meta = getattr(chunk, "metadata", {})
        sec = (
            getattr(chunk, "section", None)
            or (meta.get("section") if isinstance(meta, dict) else getattr(meta, "section", None))
            or ""
        )
        sec_str = str(sec).strip().lower()
        chunk_targets = cls._extract_target_sections(sec_str)
        for t in targets:
            if t in chunk_targets or t == sec_str:
                return True
            clean_sec = re.sub(r"^(?:section|sec\.?|rule)\s*", "", sec_str, flags=re.I).strip()
            if t == clean_sec or clean_sec.startswith(t):
                return True
        return False

    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        """Perform hybrid BM25 + Dense retrieval with Reciprocal Rank Fusion.

        Args:
            query: User dispute narrative or statutory section query.
            top_k: Number of fused results to return.

        Returns:
            list[RetrievedChunk]: Normalized chunks ordered by fused score.
        """
        chunks, _ = self.retrieve_with_confidence(query=query, top_k=top_k)
        return chunks

    def retrieve_with_confidence(
        self,
        query: str,
        top_k: int = 5,
        min_score: float | None = None,
    ) -> tuple[list[RetrievedChunk], RetrievalConfidenceResult]:
        """Perform hybrid retrieval and evaluate Layer 2 confidence gate.

        Args:
            query: User dispute narrative or statutory query.
            top_k: Number of statutory sections to retrieve.
            min_score: Optional override for minimum RRF score threshold.

        Returns:
            tuple[list[RetrievedChunk], RetrievalConfidenceResult]: Results and gate status.
        """
        threshold = self.confidence_threshold if min_score is None else min_score

        query_tokens = LegalTokenizer.tokenize(query) if query else []
        if not self.indexed_chunks or not query or not query.strip() or not query_tokens:
            empty_confidence = RetrievalConfidenceResult(
                is_grounded=False,
                top_rrf_score=0.0,
                confidence_passed=False,
                retrieved_chunk_count=0,
                abstention_triggered=True,
                abstention_message=self.DEFAULT_ABSTENTION_MESSAGE,
            )
            return [], empty_confidence

        target_sections = self._extract_target_sections(query)
        candidate_pool_size = max(top_k * 4, 20)

        # 1. Lexical BM25 Ranking
        bm25_ranks: dict[str, int] = {}
        bm25_scores: dict[str, float] = {}
        if self.bm25_index is not None:
            raw_bm25_scores = np.array(self.bm25_index.get_scores(query_tokens), dtype=float)
            if target_sections:
                for idx, chunk in enumerate(self.indexed_chunks):
                    if self._chunk_matches_target_section(chunk, target_sections):
                        raw_bm25_scores[idx] += 15.0

            sorted_bm25_indices = np.argsort(raw_bm25_scores)[::-1][:candidate_pool_size]
            rank = 1
            for idx in sorted_bm25_indices:
                score = float(raw_bm25_scores[idx])
                if score > 0.0:  # Only count positive lexical matches
                    chunk = self.indexed_chunks[idx]
                    cid = _get_chunk_id(chunk, f"chunk_{idx}")

                    # Abstention Guardrail: For multi-token queries (>=3 tokens), require
                    # at least 2 distinct token matches unless chunk matches an exact section query,
                    # preventing isolated common words (e.g. 'change' in automotive queries)
                    # from creating spurious hits.
                    if len(query_tokens) >= 3 and not self._chunk_matches_target_section(
                        chunk, target_sections
                    ):
                        chunk_content = (
                            getattr(chunk, "content", None)
                            or getattr(chunk, "text", None)
                            or str(chunk)
                        )
                        chunk_tokens_set = set(LegalTokenizer.tokenize(chunk_content))
                        matched_query_tokens = [t for t in query_tokens if t in chunk_tokens_set]
                        if len(matched_query_tokens) < 2:
                            continue

                    bm25_ranks[cid] = rank
                    bm25_scores[cid] = score
                    rank += 1

        # 2. Dense Vector Ranking (only count meaningful matches)
        dense_ranks: dict[str, int] = {}
        dense_scores: dict[str, float] = {}
        dense_hits = self.dense_retriever.search(query=query, top_k=candidate_pool_size)
        rank = 1
        for chunk, score in dense_hits:
            is_target = self._chunk_matches_target_section(chunk, target_sections)
            if score > 0.12 or is_target:  # Discard low-similarity random hash noise
                cid = _get_chunk_id(chunk, f"dense_chunk_{rank}")
                dense_ranks[cid] = rank
                dense_scores[cid] = score
                rank += 1

        # 3. Reciprocal Rank Fusion (RRF)
        # Formula: RRF(d) = w_bm25 / (k + rank_bm25(d)) + w_dense / (k + rank_dense(d))
        all_candidate_ids = set(bm25_ranks.keys()) | set(dense_ranks.keys())
        fused_scores: dict[str, float] = {}

        for cid in all_candidate_ids:
            score = 0.0
            if cid in bm25_ranks:
                score += self.w_bm25 / (self.rrf_k + bm25_ranks[cid])
            if cid in dense_ranks:
                score += self.w_dense / (self.rrf_k + dense_ranks[cid])

            chunk_obj = self.chunk_lookup.get(cid)
            if chunk_obj and self._chunk_matches_target_section(chunk_obj, target_sections):
                score += 0.02  # Exact statutory provision match bonus

            fused_scores[cid] = score

        sorted_cids = sorted(all_candidate_ids, key=lambda c: fused_scores[c], reverse=True)[:top_k]

        # 4. Assemble RetrievedChunk instances
        retrieved_results: list[RetrievedChunk] = []
        for ordinal_rank, cid in enumerate(sorted_cids, start=1):
            chunk_obj = self.chunk_lookup.get(cid)
            if not chunk_obj:
                continue

            extracted = self._extract_chunk_attributes(chunk_obj, cid)
            score = fused_scores[cid]

            chunk_res = RetrievedChunk(
                chunk_id=extracted["chunk_id"],
                content=extracted["content"],
                statute=extracted["statute"],
                chapter=extracted["chapter"],
                section=extracted["section"],
                title=extracted["title"],
                score=score,
                rank=ordinal_rank,
                retrieval_method="hybrid_rrf",
                bm25_rank=bm25_ranks.get(cid),
                dense_rank=dense_ranks.get(cid),
                bm25_score=bm25_scores.get(cid),
                dense_score=dense_scores.get(cid),
                metadata=extracted["metadata"],
            )
            retrieved_results.append(chunk_res)

        # 5. Evaluate Retrieval Confidence Gate
        top_score = retrieved_results[0].score if retrieved_results else 0.0
        confidence_passed = top_score >= threshold and len(retrieved_results) > 0

        confidence = RetrievalConfidenceResult(
            is_grounded=confidence_passed,
            top_rrf_score=top_score,
            confidence_passed=confidence_passed,
            retrieved_chunk_count=len(retrieved_results),
            abstention_triggered=not confidence_passed,
            abstention_message=(None if confidence_passed else self.DEFAULT_ABSTENTION_MESSAGE),
        )

        return retrieved_results, confidence
