"""Comprehensive unit and integration tests for Indian Consumer Law benchmark scenarios.

Validates the Pydantic schema structure of data/test_cases/benchmark_scenarios.json,
verifies all 5 dispute scenarios across statutory coverage and jurisdictional scopes,
and exercises the complete offline benchmark pipeline runner end-to-end.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel, ConfigDict, Field
from scripts.generate_raw_outputs import (
    BenchmarkPipelineRunner,
    BenchmarkSummary,
    ScenarioExecutionArtifacts,
    load_benchmark_scenarios,
    should_use_mock_llm,
)

from legal_assistant.rag.chunker import StatutoryChunker
from legal_assistant.rag.hybrid_retriever import InMemoryDenseRetriever, StatutoryHybridRetriever


class ExpectedComplainantSchema(BaseModel):
    """Schema for complainant in expected parties."""

    model_config = ConfigDict(extra="ignore")

    name: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1)
    state: str = Field(..., min_length=1)
    contact: str = Field(..., min_length=1)


class ExpectedOppositePartySchema(BaseModel):
    """Schema for opposite parties in expected parties."""

    model_config = ConfigDict(extra="ignore")

    name: str = Field(..., min_length=1)
    role: str = Field(..., min_length=1)
    entity_type: str = Field(..., min_length=1)


class ExpectedPartiesSchema(BaseModel):
    """Schema for expected parties involved in dispute."""

    model_config = ConfigDict(extra="ignore")

    complainant: ExpectedComplainantSchema
    opposite_parties: list[ExpectedOppositePartySchema] = Field(..., min_length=1)


class ExpectedEscalationSchema(BaseModel):
    """Schema for expected escalation forum and pathway."""

    model_config = ConfigDict(extra="ignore")

    forum: str = Field(..., min_length=1)
    out_of_scope_category: str | None = None
    advocate_required: bool
    statutory_court_fee_inr: float = Field(..., ge=0.0)
    resolution_ladder: list[str] = Field(..., min_length=1)


class BenchmarkScenarioSchema(BaseModel):
    """Pydantic validation schema for benchmark scenario records."""

    model_config = ConfigDict(extra="ignore")

    id: str = Field(..., pattern=r"^scenario_\d+$")
    title: str = Field(..., min_length=5)
    category: str = Field(..., min_length=3)
    language: str = Field(default="en")
    dispute_amount_inr: float = Field(..., ge=0.0)
    user_narrative: str = Field(..., min_length=50)
    expected_parties: ExpectedPartiesSchema
    expected_statutory_sections: list[str] = Field(..., min_length=3)
    expected_remedies: list[str] = Field(..., min_length=1)
    expected_in_scope: bool
    expected_escalation: ExpectedEscalationSchema


@pytest.fixture
def benchmark_file_path(project_root: Path) -> Path:
    """Return path to benchmark_scenarios.json file.

    Args:
        project_root: Pytest fixture for project root.

    Returns:
        Path to benchmark_scenarios.json.
    """
    return project_root / "data" / "test_cases" / "benchmark_scenarios.json"


@pytest.fixture
def raw_scenarios_data(benchmark_file_path: Path) -> list[dict[str, Any]]:
    """Load raw scenario dictionaries from benchmark JSON.

    Args:
        benchmark_file_path: Fixture providing path to benchmark JSON file.

    Returns:
        List of raw scenario dictionary objects.
    """
    return load_benchmark_scenarios(benchmark_file_path)


@pytest.fixture
def in_memory_hybrid_retriever(statutes_dir: Path) -> StatutoryHybridRetriever:
    """Build fast in-memory StatutoryHybridRetriever for testing.

    Args:
        statutes_dir: Path to directory containing statutory txt files.

    Returns:
        Indexed StatutoryHybridRetriever instance.
    """
    chunker = StatutoryChunker()
    all_chunks = []
    for txt_file in sorted(statutes_dir.glob("*.txt")):
        all_chunks.extend(chunker.split_text(txt_file.read_text(encoding="utf-8")))

    retriever = StatutoryHybridRetriever(
        chunks=all_chunks,
        dense_retriever=InMemoryDenseRetriever(),
    )
    return retriever


# ==============================================================================
# 1. Pydantic Schema Validation & File Integrity Tests
# ==============================================================================


def test_benchmark_scenarios_file_exists(benchmark_file_path: Path) -> None:
    """Verify data/test_cases/benchmark_scenarios.json physically exists on disk.

    Args:
        benchmark_file_path: Fixture providing benchmark JSON path.
    """
    assert benchmark_file_path.is_file()
    assert benchmark_file_path.stat().st_size > 0


def test_benchmark_scenarios_pydantic_schema_validation(
    raw_scenarios_data: list[dict[str, Any]],
) -> None:
    """Validate all 5 benchmark scenarios strictly conform to Pydantic schema.

    Args:
        raw_scenarios_data: Fixture providing loaded raw scenario dicts.
    """
    assert len(raw_scenarios_data) == 5

    scenario_ids = set()
    for sc_raw in raw_scenarios_data:
        scenario = BenchmarkScenarioSchema.model_validate(sc_raw)
        assert scenario.id not in scenario_ids
        scenario_ids.add(scenario.id)
        assert scenario.dispute_amount_inr >= 0.0
        assert len(scenario.user_narrative) > 50
        assert len(scenario.expected_statutory_sections) >= 3


def test_load_benchmark_scenarios_error_handling(tmp_path: Path) -> None:
    """Verify load_benchmark_scenarios raises appropriate errors for missing or corrupt files.

    Args:
        tmp_path: Temporary path fixture.
    """
    non_existent = tmp_path / "does_not_exist.json"
    with pytest.raises(FileNotFoundError):
        load_benchmark_scenarios(non_existent)

    corrupt_json = tmp_path / "corrupt.json"
    corrupt_json.write_text("{invalid json", encoding="utf-8")
    with pytest.raises(ValueError, match="Malformed JSON"):
        load_benchmark_scenarios(corrupt_json)

    empty_json = tmp_path / "empty.json"
    empty_json.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="Expected non-empty list"):
        load_benchmark_scenarios(empty_json)


# ==============================================================================
# 2. Specific Scenario Field & Statutory Requirements
# ==============================================================================


def test_scenario_1_ecommerce_defective_laptop_specifications(
    raw_scenarios_data: list[dict[str, Any]],
) -> None:
    """Verify Scenario 1 (Laptop defect & unlawful warranty shifting) requirements.

    Args:
        raw_scenarios_data: Fixture providing benchmark scenarios.
    """
    sc = next(s for s in raw_scenarios_data if s["id"] == "scenario_1")
    assert sc["category"] == "ecommerce_defective_goods"
    assert sc["dispute_amount_inr"] == 89999.0
    assert sc["expected_in_scope"] is True
    assert sc["expected_escalation"]["advocate_required"] is False
    assert "District Consumer Disputes Redressal Commission" in sc["expected_escalation"]["forum"]

    # Check key statutory provisions
    statutes_str = " ".join(sc["expected_statutory_sections"])
    assert "Section 2(7)" in statutes_str
    assert "Section 2(10)" in statutes_str or "Section 2(11)" in statutes_str
    assert "E-Commerce" in statutes_str


def test_scenario_2_instagram_upi_scam_specifications(
    raw_scenarios_data: list[dict[str, Any]],
) -> None:
    """Verify Scenario 2 (Instagram thrift store UPI fraud) requirements.

    Args:
        raw_scenarios_data: Fixture providing benchmark scenarios.
    """
    sc = next(s for s in raw_scenarios_data if s["id"] == "scenario_2")
    assert sc["category"] == "social_commerce_fraud"
    assert sc["dispute_amount_inr"] == 4500.0
    assert sc["expected_in_scope"] is True
    assert sc["expected_escalation"]["advocate_required"] is False

    statutes_str = " ".join(sc["expected_statutory_sections"])
    assert "Section 2(47)" in statutes_str  # Unfair trade practice
    assert "Section 2(11)" in statutes_str  # Deficiency in service
    assert "E-Commerce" in statutes_str


def test_scenario_3_edtech_subscription_trap_specifications(
    raw_scenarios_data: list[dict[str, Any]],
) -> None:
    """Verify Scenario 3 (EdTech free trial auto-debit trap) requirements.

    Args:
        raw_scenarios_data: Fixture providing benchmark scenarios.
    """
    sc = next(s for s in raw_scenarios_data if s["id"] == "scenario_3")
    assert sc["category"] == "edtech_subscription_trap"
    assert sc["dispute_amount_inr"] == 60000.0
    assert sc["expected_in_scope"] is True
    assert sc["expected_escalation"]["advocate_required"] is False

    statutes_str = " ".join(sc["expected_statutory_sections"])
    assert "Section 2(46)" in statutes_str  # Unfair contract
    assert "Section 2(47)" in statutes_str  # Unfair trade practice


def test_scenario_4_quickcommerce_short_delivery_specifications(
    raw_scenarios_data: list[dict[str, Any]],
) -> None:
    """Verify Scenario 4 (Quick-commerce missing items & chatbot stonewalling) requirements.

    Args:
        raw_scenarios_data: Fixture providing benchmark scenarios.
    """
    sc = next(s for s in raw_scenarios_data if s["id"] == "scenario_4")
    assert sc["category"] == "quick_commerce_short_delivery"
    assert sc["dispute_amount_inr"] == 1800.0
    assert sc["expected_in_scope"] is True
    assert sc["expected_escalation"]["advocate_required"] is False

    statutes_str = " ".join(sc["expected_statutory_sections"])
    assert "Section 2(11)" in statutes_str  # Deficiency in service
    assert "Rule 4(4)" in statutes_str or "Rule 7(4)" in statutes_str


def test_scenario_5_commercial_cheque_bounce_outofscope_specifications(
    raw_scenarios_data: list[dict[str, Any]],
) -> None:
    """Verify Scenario 5 (Commercial B2B, NI Act 138, and criminal intimidation) requirements.

    Args:
        raw_scenarios_data: Fixture providing benchmark scenarios.
    """
    sc = next(s for s in raw_scenarios_data if s["id"] == "scenario_5")
    assert sc["category"] == "commercial_b2b_cheque_bounce"
    assert sc["dispute_amount_inr"] == 25000000.0
    assert sc["expected_in_scope"] is False
    assert sc["expected_escalation"]["advocate_required"] is True
    assert sc["expected_escalation"]["out_of_scope_category"] == "cheque_bounce"

    statutes_str = " ".join(sc["expected_statutory_sections"])
    assert "Negotiable Instruments Act" in statutes_str
    assert "Section 138" in statutes_str


# ==============================================================================
# 3. Pipeline Execution Integration Tests (Mock / Offline Mode)
# ==============================================================================


def test_mock_llm_auto_detection_helpers() -> None:
    """Verify should_use_mock_llm properly evaluates provider configuration."""
    # Explicit mock requested
    assert should_use_mock_llm(True, "groq", "groq") is True

    # Cloud providers without keys default to mock
    assert should_use_mock_llm(False, "openai", "openai") is True
    assert should_use_mock_llm(False, "gemini", "gemini") is True


def test_benchmark_pipeline_runner_in_scope_execution(
    in_memory_hybrid_retriever: StatutoryHybridRetriever,
    raw_scenarios_data: list[dict[str, Any]],
) -> None:
    """Verify PipelineRunner executes in-scope scenario (Scenario 1) through all 4 modes.

    Args:
        in_memory_hybrid_retriever: In-memory hybrid retriever fixture.
        raw_scenarios_data: Benchmark scenario data fixture.
    """
    sc_1 = next(s for s in raw_scenarios_data if s["id"] == "scenario_1")
    runner = BenchmarkPipelineRunner(
        retriever=in_memory_hybrid_retriever,
        mock_llm=True,
    )

    art: ScenarioExecutionArtifacts = runner.run_scenario(sc_1)

    assert art.scenario_id == "scenario_1"
    assert art.is_in_scope is True
    assert art.guardrail_blocked is False

    # Mode 1: Case Builder
    assert art.case_file is not None
    assert art.case_file.complainant.name == "Rohan Sen"
    assert len(art.case_file.opposite_parties) >= 1
    assert len(art.case_file.timeline) >= 1

    # Mode 2: Legal Advisor
    assert art.legal_standing is not None
    assert art.legal_standing.is_consumer is True
    assert "District" in art.legal_standing.pecuniary_commission_forum
    assert "Commission" in art.legal_standing.pecuniary_commission_forum

    # Mode 3: Document Drafter
    assert len(art.drafted_documents) == 3
    assert "grievance_email" in art.drafted_documents
    assert "legal_notice" in art.drafted_documents
    assert "edaakhil_complaint" in art.drafted_documents

    # Mode 4: Opposing Counsel Simulator
    assert len(art.simulation_turns) >= 2
    assert art.simulation_score >= 80.0


def test_benchmark_pipeline_runner_out_of_scope_interception(
    in_memory_hybrid_retriever: StatutoryHybridRetriever,
    raw_scenarios_data: list[dict[str, Any]],
) -> None:
    """Verify PipelineRunner intercepts out-of-scope scenario (Scenario 5) at Layer 1.

    Args:
        in_memory_hybrid_retriever: In-memory hybrid retriever fixture.
        raw_scenarios_data: Benchmark scenario data fixture.
    """
    sc_5 = next(s for s in raw_scenarios_data if s["id"] == "scenario_5")
    runner = BenchmarkPipelineRunner(
        retriever=in_memory_hybrid_retriever,
        mock_llm=True,
    )

    art: ScenarioExecutionArtifacts = runner.run_scenario(sc_5)

    assert art.scenario_id == "scenario_5"
    assert art.is_in_scope is False
    assert art.guardrail_blocked is True
    assert art.case_file is None
    assert len(art.drafted_documents) == 0
    assert art.scope_result.out_of_scope_category == "cheque_bounce"
    assert art.scope_result.escalation_advice is not None
    assert "Advocate" in art.scope_result.escalation_advice


def test_benchmark_pipeline_runner_run_all_and_artifacts_generation(
    tmp_path: Path,
    in_memory_hybrid_retriever: StatutoryHybridRetriever,
    raw_scenarios_data: list[dict[str, Any]],
) -> None:
    """Verify runner.run_all generates all required files and achieves 100% scope accuracy.

    Args:
        tmp_path: Pytest temporary directory fixture.
        in_memory_hybrid_retriever: In-memory hybrid retriever fixture.
        raw_scenarios_data: Benchmark scenario data fixture.
    """
    runner = BenchmarkPipelineRunner(
        retriever=in_memory_hybrid_retriever,
        mock_llm=True,
    )

    summary: BenchmarkSummary = runner.run_all(
        scenarios=raw_scenarios_data,
        output_dir=tmp_path,
    )

    assert summary.total_scenarios_evaluated == 5
    assert summary.in_scope_scenarios_count == 4
    assert summary.out_of_scope_scenarios_count == 1
    assert summary.scope_detection_accuracy == 100.0
    assert summary.document_drafting_completeness == 100.0

    # Verify canonical deliverable files exist
    expected_files = [
        "scenario_1.json",
        "scenario_1.md",
        "scenario_2.json",
        "scenario_2.md",
        "scenario_3.json",
        "scenario_3.md",
        "scenario_4.json",
        "scenario_4.md",
        "scenario_5.json",
        "scenario_5.md",
        "BENCHMARK_EVALUATION.md",
    ]
    for filename in expected_files:
        f_path = tmp_path / filename
        assert f_path.is_file(), f"Expected artifact {filename} missing"
        assert f_path.stat().st_size > 0

    # Verify JSON content is valid
    for i in range(1, 6):
        json_path = tmp_path / f"scenario_{i}.json"
        data = json.loads(json_path.read_text(encoding="utf-8"))
        assert data["scenario_id"] == f"scenario_{i}"
        assert "scope_guardrail" in data
        assert "telemetry" in data


# ==============================================================================
# 4. Verified Repository Raw Outputs Directory Tests
# ==============================================================================


def test_repository_raw_outputs_canonical_deliverables_present(
    raw_outputs_dir: Path,
) -> None:
    """Verify that root raw_outputs directory contains all 11 required deliverable artifacts.

    Args:
        raw_outputs_dir: Fixture pointing to project root raw_outputs directory.
    """
    assert raw_outputs_dir.is_dir()

    required_artifacts = [
        "scenario_1.json",
        "scenario_1.md",
        "scenario_2.json",
        "scenario_2.md",
        "scenario_3.json",
        "scenario_3.md",
        "scenario_4.json",
        "scenario_4.md",
        "scenario_5.json",
        "scenario_5.md",
        "BENCHMARK_EVALUATION.md",
    ]

    for artifact in required_artifacts:
        art_path = raw_outputs_dir / artifact
        assert art_path.is_file(), f"Canonical deliverable {artifact} missing from raw_outputs/"
        assert art_path.stat().st_size > 0


def test_repository_raw_outputs_evaluation_report_content(
    raw_outputs_dir: Path,
) -> None:
    """Verify BENCHMARK_EVALUATION.md in repository has executive dashboard and formulas.

    Args:
        raw_outputs_dir: Fixture pointing to raw_outputs directory.
    """
    eval_file = raw_outputs_dir / "BENCHMARK_EVALUATION.md"
    assert eval_file.is_file()
    content = eval_file.read_text(encoding="utf-8")

    assert "# Legal Saathi — Master Benchmark Evaluation Report" in content
    assert "Executive Performance Dashboard" in content
    assert "Scope Detection Accuracy" in content
    assert "100.0% (5/5)" in content
    assert "Document Drafting Completeness" in content
    assert "Multi-Scenario Benchmark Results Matrix" in content
    assert "Mathematical Metric Definitions & Evaluation Formulas" in content
    assert "scenario_1" in content
    assert "scenario_5" in content
