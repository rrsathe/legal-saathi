"""Pytest fixtures and test environment configuration for Legal Saathi."""

from pathlib import Path

import pytest


@pytest.fixture
def project_root() -> Path:
    """Return the absolute path to the project root directory.

    Returns:
        Path: Absolute path of the project root directory.
    """
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def data_dir(project_root: Path) -> Path:
    """Return the path to the project data directory.

    Args:
        project_root: Fixture providing the root directory path.

    Returns:
        Path: Path to the data directory.
    """
    return project_root / "data"


@pytest.fixture
def statutes_dir(data_dir: Path) -> Path:
    """Return the path to the statutes directory.

    Args:
        data_dir: Fixture providing the data directory path.

    Returns:
        Path: Path to the statutes directory.
    """
    return data_dir / "statutes"


@pytest.fixture
def test_cases_dir(data_dir: Path) -> Path:
    """Return the path to the test cases directory.

    Args:
        data_dir: Fixture providing the data directory path.

    Returns:
        Path: Path to the test cases directory.
    """
    return data_dir / "test_cases"


@pytest.fixture
def raw_outputs_dir(project_root: Path) -> Path:
    """Return the path to the raw outputs evaluation directory.

    Args:
        project_root: Fixture providing the root directory path.

    Returns:
        Path: Path to the raw outputs directory.
    """
    return project_root / "raw_outputs"
