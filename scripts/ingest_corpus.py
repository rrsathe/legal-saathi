"""Statutory corpus ingestion CLI for Legal Saathi AI Consumer Lawyer.

Reads Indian statutory corpus text files (CPA 2019, E-Commerce Rules 2020,
and e-Daakhil / NCH guidelines), splits them into structure-aware hierarchical
statutory chunks using `StatutoryChunker`, and indexes them into
`StatutoryHybridRetriever` (BM25Okapi + Chroma / InMemory dense vector store).
"""

from __future__ import annotations

import argparse
import logging
import os
import pickle
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from legal_assistant.config import get_settings
from legal_assistant.rag.chunker import StatutoryChunk, StatutoryChunker
from legal_assistant.rag.hybrid_retriever import (
    BaseDenseRetriever,
    ChromaDenseRetriever,
    InMemoryDenseRetriever,
    StatutoryHybridRetriever,
)

# Silence chromadb telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "false"
logging.getLogger("chromadb.telemetry.posthog").setLevel(logging.CRITICAL)

logger = logging.getLogger("legal_assistant.ingest")

CORE_STATUTE_FILES: list[str] = [
    "cpa_2019_core.txt",
    "ecommerce_rules_2020.txt",
    "edaakhil_nch_procedures.txt",
]


@dataclass
class IngestionMetrics:
    """Summary metrics captured during statutory corpus ingestion."""

    total_files: int
    file_names: list[str]
    total_raw_chars: int
    total_chunks: int
    unique_statutes: int
    unique_chapters: int
    unique_sections: int
    chunking_time_seconds: float
    indexing_time_seconds: float
    total_time_seconds: float
    persist_dir: Path | None
    bm25_path: Path | None
    dense_backend: str
    validation_passed: bool


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments for corpus ingestion.

    Args:
        args: Command line argument tokens (defaults to sys.argv[1:]).

    Returns:
        argparse.Namespace: Parsed CLI options.
    """
    settings = get_settings()

    parser = argparse.ArgumentParser(
        description="Ingest Indian Consumer Law statutory texts into hybrid BM25 + vector index.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--corpus-dir",
        type=Path,
        default=Path("data/statutes"),
        help="Directory containing statutory text corpus files (*.txt).",
    )
    parser.add_argument(
        "--persist-dir",
        type=Path,
        default=settings.vector_db_path,
        help="Target directory for persistent Chroma vector database.",
    )
    parser.add_argument(
        "--bm25-path",
        type=Path,
        default=settings.bm25_index_path,
        help="Target file path for serializing BM25 Okapi index pickle.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size for dense embedding and vector storage.",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        default=False,
        help="Wipe existing persistent vector DB and BM25 index before indexing.",
    )
    parser.add_argument(
        "--in-memory",
        action="store_true",
        default=False,
        help="Use ephemeral in-memory dense store (disables Chroma disk persistence).",
    )
    parser.add_argument(
        "--no-validate",
        dest="validate",
        action="store_false",
        default=True,
        help="Skip post-ingestion retrieval validation probes.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Enable verbose debug logging.",
    )
    return parser.parse_args(args)


def load_and_chunk_corpus(
    corpus_dir: Path,
    chunker: StatutoryChunker | None = None,
) -> tuple[list[StatutoryChunk], dict[str, int], int]:
    """Discover and chunk all statutory text files in the target directory.

    Args:
        corpus_dir: Filesystem path to directory containing statutory texts.
        chunker: Configured StatutoryChunker instance (defaults to StatutoryChunker()).

    Returns:
        tuple[list[StatutoryChunk], dict[str, int], int]:
            - Accumulated list of StatutoryChunk instances.
            - Mapping of filename to count of extracted chunks.
            - Total raw characters read from disk.

    Raises:
        FileNotFoundError: If corpus_dir does not exist or contains no text files.
    """
    if not corpus_dir.exists() or not corpus_dir.is_dir():
        raise FileNotFoundError(f"Corpus directory not found: {corpus_dir}")

    # Discover and sort files, ensuring core statutory files are prioritized
    all_files = sorted(corpus_dir.glob("*.txt"))
    if not all_files:
        raise FileNotFoundError(f"No .txt statutory files found in: {corpus_dir}")

    prioritized_files: list[Path] = []
    # Add core files in declared order if present
    for core_name in CORE_STATUTE_FILES:
        core_path = corpus_dir / core_name
        if core_path.exists():
            prioritized_files.append(core_path)

    # Add any additional .txt files not in core list
    for f in all_files:
        if f not in prioritized_files:
            prioritized_files.append(f)

    active_chunker = chunker or StatutoryChunker()
    all_chunks: list[StatutoryChunk] = []
    chunks_per_file: dict[str, int] = {}
    total_chars = 0

    for file_path in prioritized_files:
        raw_text = file_path.read_text(encoding="utf-8")
        total_chars += len(raw_text)

        chunks = active_chunker.split_text(raw_text)
        chunks_per_file[file_path.name] = len(chunks)
        all_chunks.extend(chunks)
        logger.debug(
            "Parsed %d chunks from %s (%d chars)", len(chunks), file_path.name, len(raw_text)
        )

    return all_chunks, chunks_per_file, total_chars


def setup_dense_backend(
    persist_dir: Path | None,
    rebuild: bool = False,
    in_memory: bool = False,
    collection_name: str = "statutory_corpus",
) -> tuple[BaseDenseRetriever, str]:
    """Initialize dense retriever backend based on CLI parameters.

    Args:
        persist_dir: Target path for SQLite/Chroma persistence.
        rebuild: Whether to wipe existing persistent store before initialization.
        in_memory: Force in-memory dense vector store (zero disk persistence).
        collection_name: Name of ChromaDB collection.

    Returns:
        tuple[BaseDenseRetriever, str]:
            - Configured BaseDenseRetriever instance.
            - Name of the backend ('chroma_persistent' or 'in_memory').
    """
    if in_memory or persist_dir is None:
        return InMemoryDenseRetriever(), "in_memory"

    if rebuild and persist_dir.exists():
        logger.info("Wiping existing persistent vector DB at %s", persist_dir)
        try:
            shutil.rmtree(persist_dir)
        except OSError as e:
            logger.warning("Could not fully remove %s: %s", persist_dir, e)

    persist_dir.mkdir(parents=True, exist_ok=True)
    dense_retriever = ChromaDenseRetriever(
        collection_name=collection_name,
        persist_dir=str(persist_dir),
    )
    return dense_retriever, "chroma_persistent"


def save_bm25_store(
    retriever: StatutoryHybridRetriever,
    bm25_path: Path,
    rebuild: bool = False,
) -> None:
    """Serialize BM25 index and statutory chunks to disk.

    Args:
        retriever: Indexed StatutoryHybridRetriever instance.
        bm25_path: Target pickle file destination.
        rebuild: Whether to overwrite existing file.
    """
    if rebuild and bm25_path.exists():
        bm25_path.unlink()

    bm25_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "bm25_index": retriever.bm25_index,
        "chunks": retriever.indexed_chunks,
        "chunk_lookup": retriever.chunk_lookup,
        "total_chunks": len(retriever.indexed_chunks),
        "created_at": time.time(),
    }
    with bm25_path.open("wb") as f:
        pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)
    logger.debug("Serialized BM25 index to %s", bm25_path)


def validate_index(retriever: StatutoryHybridRetriever) -> bool:
    """Validate hybrid retrieval recall on benchmark consumer law test queries.

    Args:
        retriever: Indexed StatutoryHybridRetriever instance.

    Returns:
        bool: True if all validation probes passed confidence gate and retrieved
            expected statutory provisions.
    """
    probes: list[tuple[str, str, str]] = [
        (
            "Section 2(47)",
            "2(47)",
            "Exact statutory section lookup",
        ),
        (
            "refusal to refund consideration paid for defective goods",
            "2(47)",
            "Colloquial CPA refund query",
        ),
        (
            "e-commerce grievance officer acknowledgement within 48 hours",
            "Rule 4",
            "E-Commerce Rules grievance probe",
        ),
    ]

    all_passed = True
    print("\n--- Running Retrieval Validation Probes ---")
    for query, expected_fragment, label in probes:
        results, conf = retriever.retrieve_with_confidence(query, top_k=3)
        top_section = results[0].section if results else "None"
        top_title = results[0].title if results else "None"
        top_score = conf.top_rrf_score

        # Check if expected provision is in top-3 candidates
        sections_found = [r.section for r in results]
        matched = any(expected_fragment in sec for sec in sections_found)

        status_str = "[PASS]" if (matched and conf.is_grounded) else "[FAIL]"
        if not (matched and conf.is_grounded):
            all_passed = False

        print(
            f"  {status_str} {label}: '{query[:40]}...'\n"
            f"         Top Hit: {top_section} ({top_title}) | Score: {top_score:.4f} | "
            f"Grounded: {conf.is_grounded}"
        )

    return all_passed


def format_report(metrics: IngestionMetrics, chunks_per_file: dict[str, int]) -> str:
    """Format human-readable summary report table.

    Args:
        metrics: Populated IngestionMetrics container.
        chunks_per_file: Mapping of filename to chunk count.

    Returns:
        str: Multi-line formatted console summary.
    """
    status_label = "SUCCESS" if metrics.validation_passed else "WARNING (Validation Failed)"
    pdir_str = str(metrics.persist_dir) if metrics.persist_dir else "N/A (in-memory)"
    bm25_str = str(metrics.bm25_path) if metrics.bm25_path else "N/A"
    lines = [
        "=" * 80,
        "             LEGAL SAATHI: CORPUS INGESTION SUMMARY REPORT",
        "=" * 80,
        f" Status:                  {status_label}",
        f" Dense Backend:           {metrics.dense_backend}",
        f" Persist Directory:       {pdir_str}",
        f" BM25 Store Path:         {bm25_str}",
        "-" * 80,
        f" Files Processed:       {metrics.total_files} ({metrics.total_raw_chars:,} chars)",
    ]
    for fname, count in chunks_per_file.items():
        lines.append(f"   - {fname:<30}: {count:>3} chunks")

    lines.extend(
        [
            "-" * 80,
            " Hierarchical Index Statistics:",
            f"   - Total Chunks Indexed:           {metrics.total_chunks:>5}",
            f"   - Unique Statutes:                {metrics.unique_statutes:>5}",
            f"   - Unique Chapters:                {metrics.unique_chapters:>5}",
            f"   - Unique Sections / Rules:        {metrics.unique_sections:>5}",
            f"   - Total Characters in Chunks:     {metrics.total_raw_chars:>5,}",
            "-" * 80,
            " Performance Telemetry:",
            f"   - Chunking Time:                  {metrics.chunking_time_seconds:>7.3f}s",
            f"   - Indexing Time:                  {metrics.indexing_time_seconds:>7.3f}s",
            f"   - Total Elapsed Time:             {metrics.total_time_seconds:>7.3f}s",
            "=" * 80,
        ]
    )
    return "\n".join(lines)


def run_ingestion(args: argparse.Namespace) -> IngestionMetrics:
    """Execute complete corpus ingestion workflow.

    Args:
        args: Parsed CLI options.

    Returns:
        IngestionMetrics: Metrics captured during ingestion.
    """
    total_start = time.perf_counter()

    # 1. Chunking
    chunk_start = time.perf_counter()
    chunker = StatutoryChunker()
    chunks, chunks_per_file, total_chars = load_and_chunk_corpus(
        corpus_dir=args.corpus_dir,
        chunker=chunker,
    )
    chunking_time = time.perf_counter() - chunk_start

    # Unique statutory metadata counters
    unique_statutes = len({c.metadata.statute for c in chunks})
    unique_chapters = len({c.metadata.chapter for c in chunks})
    unique_sections = len({c.metadata.section for c in chunks})

    # 2. Dense backend initialization
    dense_retriever, backend_name = setup_dense_backend(
        persist_dir=args.persist_dir,
        rebuild=args.rebuild,
        in_memory=args.in_memory,
    )

    # 3. Hybrid Indexing
    index_start = time.perf_counter()
    retriever = StatutoryHybridRetriever(
        chunks=chunks,
        dense_retriever=dense_retriever,
    )
    indexing_time = time.perf_counter() - index_start

    # 4. Save BM25 serialization if path provided
    if args.bm25_path and not args.in_memory:
        save_bm25_store(
            retriever=retriever,
            bm25_path=args.bm25_path,
            rebuild=args.rebuild,
        )

    # 5. Validation Probes
    validation_passed = True
    if args.validate:
        validation_passed = validate_index(retriever)

    total_time = time.perf_counter() - total_start

    metrics = IngestionMetrics(
        total_files=len(chunks_per_file),
        file_names=list(chunks_per_file.keys()),
        total_raw_chars=total_chars,
        total_chunks=len(chunks),
        unique_statutes=unique_statutes,
        unique_chapters=unique_chapters,
        unique_sections=unique_sections,
        chunking_time_seconds=chunking_time,
        indexing_time_seconds=indexing_time,
        total_time_seconds=total_time,
        persist_dir=args.persist_dir if not args.in_memory else None,
        bm25_path=args.bm25_path if not args.in_memory else None,
        dense_backend=backend_name,
        validation_passed=validation_passed,
    )

    print(format_report(metrics, chunks_per_file))
    return metrics


def main() -> None:
    """CLI entry point for corpus ingestion."""
    args = parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    try:
        metrics = run_ingestion(args)
        if not metrics.validation_passed:
            sys.exit(1)
    except Exception as exc:
        logger.exception("Ingestion failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
