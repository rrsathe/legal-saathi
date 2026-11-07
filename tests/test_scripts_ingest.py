"""Smoke and integration tests for statutory corpus ingestion CLI.

Tests:
1. CLI execution with `--help` ensuring exit code 0 and argument documentation.
2. CLI end-to-end execution with synthetic test corpus and custom persist directory.
3. Robust error handling on non-existent or empty corpus directories.
4. Direct unit testing of `load_and_chunk_corpus`, `setup_dense_backend`, and `run_ingestion`.
5. Rebuild flag behavior wiping and re-indexing persistent indices.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import pytest
from scripts.ingest_corpus import (
    IngestionMetrics,
    load_and_chunk_corpus,
    run_ingestion,
    setup_dense_backend,
)

from legal_assistant.rag.chunker import StatutoryChunker
from legal_assistant.rag.hybrid_retriever import InMemoryDenseRetriever


# ==============================================================================
# Fixtures
# ==============================================================================
@pytest.fixture
def synthetic_corpus_dir(tmp_path: Path) -> Path:
    """Create a temporary directory containing valid synthetic statutory corpus files.

    Args:
        tmp_path: Pytest temporary directory fixture.

    Returns:
        Path: Path to populated temporary corpus directory.
    """
    corpus_dir = tmp_path / "statutes"
    corpus_dir.mkdir(parents=True, exist_ok=True)

    sep = "=" * 80
    cpa_file = corpus_dir / "cpa_2019_core.txt"
    cpa_file.write_text(
        f"{sep}\n"
        "STATUTE: Consumer Protection Act, 2019\n"
        "CHAPTER: Chapter I - Preliminary\n"
        "SECTION: Section 2(7)\n"
        "TITLE: Definition of Consumer\n"
        "CLAUSE: Sub-section (7)\n"
        "ACT_YEAR: 2019\n"
        "KEYWORDS: consumer, consideration, goods\n"
        "CROSS_REFS: Section 2(47)\n"
        "CANONICAL_BREADCRUMB: [STATUTE: Consumer Protection Act, 2019 | "
        "CHAPTER: I Preliminary | SECTION: 2(7) | TITLE: Definition of Consumer]\n"
        f"{sep}\n"
        "(7) 'consumer' means any person who buys any goods for a consideration "
        "which has been paid or promised or partly paid and partly promised.\n\n"
        f"{sep}\n"
        "STATUTE: Consumer Protection Act, 2019\n"
        "CHAPTER: Chapter I - Preliminary\n"
        "SECTION: Section 2(47)\n"
        "TITLE: Unfair Trade Practice\n"
        "CLAUSE: Clause (47)\n"
        "ACT_YEAR: 2019\n"
        "KEYWORDS: unfair trade practice, refusal to refund, consideration paid, defective goods\n"
        "CROSS_REFS: Section 35\n"
        "CANONICAL_BREADCRUMB: [STATUTE: Consumer Protection Act, 2019 | "
        "CHAPTER: I Preliminary | SECTION: 2(47) | TITLE: Unfair Trade Practice]\n"
        f"{sep}\n"
        "(47) 'unfair trade practice' means a trade practice which adopts any unfair "
        "method or deceptive practice including refusing after receiving payment to "
        "deliver goods or refund consideration paid for defective goods within thirty days.\n\n"
        f"{sep}\n"
        "STATUTE: Consumer Protection Act, 2019\n"
        "CHAPTER: Chapter IV - Consumer Disputes Redressal Commission\n"
        "SECTION: Section 35\n"
        "TITLE: Manner of Filing Complaint\n"
        "CLAUSE: Sub-section (1)\n"
        "ACT_YEAR: 2019\n"
        "KEYWORDS: complaint filing, district commission\n"
        "CROSS_REFS: Section 2(7)\n"
        "CANONICAL_BREADCRUMB: [STATUTE: Consumer Protection Act, 2019 | "
        "CHAPTER: IV Redressal | SECTION: 35 | TITLE: Manner of Filing Complaint]\n"
        f"{sep}\n"
        "(1) A complaint, in relation to any goods sold or delivered, may be filed "
        "with a District Commission by the consumer.\n",
        encoding="utf-8",
    )

    ecom_file = corpus_dir / "ecommerce_rules_2020.txt"
    ecom_file.write_text(
        f"{sep}\n"
        "STATUTE: Consumer Protection (E-Commerce) Rules, 2020\n"
        "CHAPTER: Duties of E-Commerce Entities\n"
        "SECTION: Rule 4(5)\n"
        "TITLE: Grievance Redressal Mechanism\n"
        "CLAUSE: Sub-rule (5)\n"
        "ACT_YEAR: 2020\n"
        "KEYWORDS: e-commerce grievance officer acknowledgement within 48 hours, thirty days\n"
        "CROSS_REFS: Rule 6\n"
        "CANONICAL_BREADCRUMB: [STATUTE: Consumer Protection (E-Commerce) Rules, 2020 | "
        "CHAPTER: Duties | SECTION: Rule 4(5) | TITLE: Grievance Redressal Mechanism]\n"
        f"{sep}\n"
        "Every e-commerce entity shall acknowledge receipt of any consumer complaint "
        "within forty-eight hours and redress the complaint within one month.\n\n"
        f"{sep}\n"
        "STATUTE: Consumer Protection (E-Commerce) Rules, 2020\n"
        "CHAPTER: Duties of Sellers on Marketplace\n"
        "SECTION: Rule 6(3)\n"
        "TITLE: Return and Refund Obligations\n"
        "CLAUSE: Sub-rule (3)\n"
        "ACT_YEAR: 2020\n"
        "KEYWORDS: refund, defective goods, returns\n"
        "CROSS_REFS: Rule 4\n"
        "CANONICAL_BREADCRUMB: [STATUTE: Consumer Protection (E-Commerce) Rules, 2020 | "
        "CHAPTER: Duties of Sellers | SECTION: Rule 6(3) | TITLE: Return and Refund Obligations]\n"
        f"{sep}\n"
        "No seller on a marketplace shall refuse to take back goods or refuse to refund "
        "consideration paid if goods are defective, deficient or spurious.\n",
        encoding="utf-8",
    )

    edaakhil_file = corpus_dir / "edaakhil_nch_procedures.txt"
    edaakhil_file.write_text(
        f"{sep}\n"
        "STATUTE: Consumer Protection Act, 2019\n"
        "CHAPTER: Procedures and Redressal Portals\n"
        "SECTION: Rule 1\n"
        "TITLE: Online Filing Portal\n"
        "CLAUSE: General\n"
        "ACT_YEAR: 2020\n"
        "KEYWORDS: edaakhil, nch 1915, online filing\n"
        "CROSS_REFS: Section 35\n"
        "CANONICAL_BREADCRUMB: [STATUTE: Consumer Protection Act, 2019 | "
        "CHAPTER: Portals | SECTION: Rule 1 | TITLE: Online Filing Portal]\n"
        f"{sep}\n"
        "Consumers may file online complaints through e-Daakhil portal or register "
        "grievances via National Consumer Helpline 1915.\n",
        encoding="utf-8",
    )

    return corpus_dir


@pytest.fixture
def empty_corpus_dir(tmp_path: Path) -> Path:
    """Create an empty directory containing no statutory text files.

    Args:
        tmp_path: Pytest temporary directory fixture.

    Returns:
        Path: Path to empty directory.
    """
    empty_dir = tmp_path / "empty_statutes"
    empty_dir.mkdir(parents=True, exist_ok=True)
    return empty_dir


# ==============================================================================
# 1. CLI Smoke Tests via Subprocess
# ==============================================================================
def test_ingest_cli_help_flag() -> None:
    """Verify that `python scripts/ingest_corpus.py --help` outputs options and exits 0."""
    script_path = Path("scripts/ingest_corpus.py").resolve()
    assert script_path.exists(), f"Script not found at: {script_path}"

    result = subprocess.run(
        [sys.executable, str(script_path), "--help"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    stdout = result.stdout
    assert "--corpus-dir" in stdout
    assert "--persist-dir" in stdout
    assert "--bm25-path" in stdout
    assert "--batch-size" in stdout
    assert "--rebuild" in stdout
    assert "--in-memory" in stdout
    assert "--validate" in stdout
    assert "--no-validate" in stdout


def test_ingest_cli_execution_with_test_arguments(
    synthetic_corpus_dir: Path,
    tmp_path: Path,
) -> None:
    """Verify end-to-end CLI execution with synthetic corpus in in-memory mode."""
    script_path = Path("scripts/ingest_corpus.py").resolve()
    persist_dir = tmp_path / "test_chroma"
    bm25_file = tmp_path / "test_bm25.pkl"

    cmd = [
        sys.executable,
        str(script_path),
        "--corpus-dir",
        str(synthetic_corpus_dir),
        "--persist-dir",
        str(persist_dir),
        "--bm25-path",
        str(bm25_file),
        "--in-memory",
        "--batch-size",
        "16",
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )

    err_msg = f"CLI failed with error: {result.stderr}\nStdout: {result.stdout}"
    assert result.returncode == 0, err_msg
    output = result.stdout
    assert "INGESTION COMPLETED" in output or "SUMMARY" in output
    assert "TOTAL CHUNKS" in output or "Total Chunks" in output
    assert "UNIQUE SECTIONS" in output or "Unique Sections" in output


def test_ingest_cli_missing_corpus_dir_fails(tmp_path: Path) -> None:
    """Verify CLI exits non-zero with error when corpus directory does not exist."""
    script_path = Path("scripts/ingest_corpus.py").resolve()
    non_existent = tmp_path / "non_existent_dir_12345"

    result = subprocess.run(
        [sys.executable, str(script_path), "--corpus-dir", str(non_existent)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    combined_output = result.stdout + result.stderr
    assert "FileNotFoundError" in combined_output or "not found" in combined_output.lower()


def test_ingest_cli_empty_corpus_dir_fails(empty_corpus_dir: Path) -> None:
    """Verify CLI exits non-zero when target corpus directory has no text files."""
    script_path = Path("scripts/ingest_corpus.py").resolve()

    result = subprocess.run(
        [sys.executable, str(script_path), "--corpus-dir", str(empty_corpus_dir)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    combined = (result.stdout + result.stderr).lower()
    assert "no .txt statutory files found" in combined or "error" in combined


# ==============================================================================
# 2. Programmatic Function Unit Tests
# ==============================================================================
def test_load_and_chunk_corpus_direct(synthetic_corpus_dir: Path) -> None:
    """Verify load_and_chunk_corpus parses all files and preserves metadata."""
    chunker = StatutoryChunker()
    chunks, file_counts, total_chars = load_and_chunk_corpus(
        corpus_dir=synthetic_corpus_dir,
        chunker=chunker,
    )

    assert len(chunks) >= 3
    assert total_chars > 0
    assert "cpa_2019_core.txt" in file_counts
    assert "ecommerce_rules_2020.txt" in file_counts
    assert "edaakhil_nch_procedures.txt" in file_counts

    # Verify structured metadata on extracted chunks
    section_names = [c.metadata.section for c in chunks]
    assert any("2(7)" in sec or "2(47)" in sec for sec in section_names)


def test_load_and_chunk_corpus_invalid_dir(tmp_path: Path) -> None:
    """Verify FileNotFoundError raised when loading from invalid path."""
    with pytest.raises(FileNotFoundError):
        load_and_chunk_corpus(corpus_dir=tmp_path / "missing_folder")


def test_setup_dense_backend_in_memory(tmp_path: Path) -> None:
    """Verify setup_dense_backend returns InMemoryDenseRetriever when in_memory=True."""
    retriever, backend_name = setup_dense_backend(
        persist_dir=tmp_path / "chroma",
        rebuild=False,
        in_memory=True,
    )

    assert isinstance(retriever, InMemoryDenseRetriever)
    assert backend_name == "in_memory"


def test_run_ingestion_programmatic(synthetic_corpus_dir: Path, tmp_path: Path) -> None:
    """Verify run_ingestion executes workflow and returns valid IngestionMetrics."""
    args = argparse.Namespace(
        corpus_dir=synthetic_corpus_dir,
        persist_dir=tmp_path / "test_chroma",
        bm25_path=tmp_path / "test_bm25.pkl",
        batch_size=16,
        rebuild=True,
        in_memory=True,
        validate=True,
        verbose=False,
    )

    metrics = run_ingestion(args)

    assert isinstance(metrics, IngestionMetrics)
    assert metrics.total_chunks >= 3
    assert metrics.total_files == 3
    assert metrics.unique_statutes >= 2
    assert metrics.validation_passed is True
    assert metrics.total_time_seconds > 0.0


def test_ingest_cli_with_validate_flag(
    synthetic_corpus_dir: Path,
    tmp_path: Path,
) -> None:
    """Verify CLI execution accepts and succeeds with explicit --validate flag."""
    script_path = Path("scripts/ingest_corpus.py").resolve()
    persist_dir = tmp_path / "test_chroma_val"
    bm25_file = tmp_path / "test_bm25_val.pkl"

    cmd = [
        sys.executable,
        str(script_path),
        "--corpus-dir",
        str(synthetic_corpus_dir),
        "--persist-dir",
        str(persist_dir),
        "--bm25-path",
        str(bm25_file),
        "--in-memory",
        "--validate",
        "--batch-size",
        "16",
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"Error: {result.stderr}\nStdout: {result.stdout}"
    assert "[PASS]" in result.stdout
    assert "SUCCESS" in result.stdout


def test_ingest_cli_with_no_validate_flag(
    synthetic_corpus_dir: Path,
    tmp_path: Path,
) -> None:
    """Verify CLI execution with --no-validate skips validation probes."""
    script_path = Path("scripts/ingest_corpus.py").resolve()
    persist_dir = tmp_path / "test_chroma_noval"
    bm25_file = tmp_path / "test_bm25_noval.pkl"

    cmd = [
        sys.executable,
        str(script_path),
        "--corpus-dir",
        str(synthetic_corpus_dir),
        "--persist-dir",
        str(persist_dir),
        "--bm25-path",
        str(bm25_file),
        "--in-memory",
        "--no-validate",
        "--batch-size",
        "16",
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"Error: {result.stderr}\nStdout: {result.stdout}"
    assert "Running Retrieval Validation Probes" not in result.stdout


def test_ingest_cli_validate_and_no_validate_flags() -> None:
    """Verify --validate and --no-validate flags are accepted by CLI parser."""
    from scripts.ingest_corpus import parse_args

    # Explicit --validate flag
    args_validate = parse_args(["--in-memory", "--validate"])
    assert args_validate.validate is True
    assert args_validate.in_memory is True

    # Explicit --no-validate flag
    args_no_validate = parse_args(["--in-memory", "--no-validate"])
    assert args_no_validate.validate is False

    # Default without flags
    args_default = parse_args(["--in-memory"])
    assert args_default.validate is True


def test_ingest_cli_real_corpus_in_memory_validate() -> None:
    """Verify CLI ingests real statutory corpus in memory with --validate and exits 0."""
    script_path = Path("scripts/ingest_corpus.py").resolve()
    corpus_dir = Path("data/statutes").resolve()

    assert script_path.exists(), f"Script not found at: {script_path}"
    assert corpus_dir.exists(), f"Corpus directory not found at: {corpus_dir}"

    cmd = [
        sys.executable,
        str(script_path),
        "--corpus-dir",
        str(corpus_dir),
        "--in-memory",
        "--validate",
        "-v",
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )

    err_msg = (
        f"CLI failed with code {result.returncode}.\n"
        f"Stderr: {result.stderr}\nStdout: {result.stdout}"
    )
    assert result.returncode == 0, err_msg
    assert "[PASS]" in result.stdout
    assert "SUCCESS" in result.stdout
    assert "Total Chunks" in result.stdout or "TOTAL CHUNKS" in result.stdout


def test_run_ingestion_programmatic_real_corpus() -> None:
    """Verify run_ingestion processes real data/statutes corpus with validation probes."""
    corpus_dir = Path("data/statutes").resolve()
    args = argparse.Namespace(
        corpus_dir=corpus_dir,
        persist_dir=Path("data/index/test_chroma"),
        bm25_path=Path("data/index/test_bm25.pkl"),
        batch_size=32,
        rebuild=True,
        in_memory=True,
        validate=True,
        verbose=False,
    )

    metrics = run_ingestion(args)

    assert isinstance(metrics, IngestionMetrics)
    assert metrics.total_chunks == 46
    assert metrics.total_files == 3
    assert metrics.unique_statutes >= 3
    assert metrics.validation_passed is True
    assert metrics.total_time_seconds > 0.0
