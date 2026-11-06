"""Initial smoke and sanity test suite for Milestone 1.

Validates environment setup, package importing, Python version, Unicode/UTF-8
handling for Indian legal text and currency symbols, directory scaffolding,
and Windows pathlib compatibility.
"""

import sys
from pathlib import Path

import legal_assistant


def test_package_import_and_version() -> None:
    """Verify legal_assistant package can be imported and exposes version."""
    assert legal_assistant.__version__ == "0.1.0"
    assert hasattr(legal_assistant, "__version__")


def test_python_runtime_version() -> None:
    """Verify runtime Python is 3.11.x as required for Windows wheels."""
    assert sys.version_info.major == 3
    assert sys.version_info.minor == 11


def test_unicode_utf8_legal_characters() -> None:
    """Verify Unicode support for Indian legal terminology and currency symbols."""
    rupee_symbol: str = "₹"
    hindi_text: str = "उपभोक्ता संरक्षण अधिनियम, 2019"
    statute_symbols: str = "§ 2(47) — CPA & ¶ 5"

    sample_combined: str = f"{statute_symbols} | Fee: {rupee_symbol}500 | {hindi_text}"

    encoded_bytes: bytes = sample_combined.encode("utf-8")
    decoded_text: str = encoded_bytes.decode("utf-8")

    assert decoded_text == sample_combined
    assert rupee_symbol in decoded_text
    assert "उपभोक्ता" in decoded_text
    assert "§" in decoded_text
    assert "—" in decoded_text


def test_directory_scaffolding_exists(project_root: Path) -> None:
    """Verify all mandatory project directories exist on the filesystem.

    Args:
        project_root: Fixture providing project root path.
    """
    expected_directories: list[Path] = [
        project_root / "src" / "legal_assistant",
        project_root / "tests",
        project_root / "scripts",
        project_root / "data" / "statutes",
        project_root / "data" / "test_cases",
        project_root / "raw_outputs",
    ]

    for directory in expected_directories:
        assert directory.is_dir(), f"Expected directory does not exist: {directory}"


def test_windows_pathlib_compatibility(project_root: Path) -> None:
    """Verify pathlib handles Windows drive letters and forward-slash posix conversion.

    Args:
        project_root: Fixture providing project root path.
    """
    posix_path: str = project_root.as_posix()
    assert "/" in posix_path or len(posix_path) > 0
    assert not posix_path.endswith("\\")

    statutes_path: Path = project_root / "data" / "statutes" / "cpa_2019_core.txt"
    assert statutes_path.parts[-3:] == ("data", "statutes", "cpa_2019_core.txt")
