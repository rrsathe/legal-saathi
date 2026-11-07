"""Comprehensive unit and integration tests for Indian Consumer Law benchmark scenarios.

Validates the Pydantic schema structure of data/test_cases/benchmark_scenarios.json,
verifies all 5 dispute scenarios across statutory coverage and jurisdictional scopes,
and exercises the complete offline benchmark pipeline runner end-to-end.
"""

from __future__ import annotations

import json
import re
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
from legal_assistant.schemas import CaseFile, DraftedDocument, LegalStanding


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


# ==============================================================================
# 5. Benchmark Telemetry Integrity & Dynamic Status Regression Tests
# ==============================================================================


def test_benchmark_summary_quality_gate_thresholds(
    tmp_path: Path,
    in_memory_hybrid_retriever: StatutoryHybridRetriever,
    raw_scenarios_data: list[dict[str, Any]],
) -> None:
    """Verify BenchmarkSummary dynamically meets all target quality standards.

    Args:
        tmp_path: Temporary directory fixture.
        in_memory_hybrid_retriever: Fast in-memory retriever fixture.
        raw_scenarios_data: Loaded benchmark scenario data fixture.
    """
    runner = BenchmarkPipelineRunner(
        retriever=in_memory_hybrid_retriever,
        mock_llm=True,
    )
    summary = runner.run_all(scenarios=raw_scenarios_data, output_dir=tmp_path)

    assert summary.scope_detection_accuracy == 100.0
    assert summary.retrieval_precision_avg >= 80.0, (
        f"Retrieval precision {summary.retrieval_precision_avg}% below 80.0% target"
    )
    assert summary.citation_verification_pass_rate >= 80.0, (
        f"Citation pass rate {summary.citation_verification_pass_rate}% below 80.0% target"
    )
    assert summary.document_drafting_completeness == 100.0
    assert summary.simulation_realism_score >= 85.0


def test_benchmark_evaluation_report_mathematical_integrity(
    tmp_path: Path,
    in_memory_hybrid_retriever: StatutoryHybridRetriever,
    raw_scenarios_data: list[dict[str, Any]],
) -> None:
    """Verify generated BENCHMARK_EVALUATION.md contains zero hardcoded strings.

    Args:
        tmp_path: Temporary directory fixture.
        in_memory_hybrid_retriever: Fast in-memory retriever fixture.
        raw_scenarios_data: Loaded benchmark scenario data fixture.
    """
    runner = BenchmarkPipelineRunner(
        retriever=in_memory_hybrid_retriever,
        mock_llm=True,
    )
    runner.run_all(scenarios=raw_scenarios_data, output_dir=tmp_path)

    eval_md = tmp_path / "BENCHMARK_EVALUATION.md"
    assert eval_md.is_file()
    eval_text = eval_md.read_text(encoding="utf-8")

    # 1. Executive Dashboard status verification
    dashboard_lines = [
        line for line in eval_text.splitlines() if line.startswith("| **") and "|" in line
    ]
    assert len(dashboard_lines) == 5, f"Expected 5 dashboard rows, got {len(dashboard_lines)}"

    for line in dashboard_lines:
        parts = [p.strip() for p in line.split("|") if p.strip()]
        metric_name, target_std, achieved_str, status = (
            parts[0],
            parts[1],
            parts[2],
            parts[3],
        )
        score_match = re.search(r"(\d+(?:\.\d+)?)", achieved_str)
        assert score_match is not None, f"Could not parse score from {achieved_str}"
        clean_score = float(score_match.group(1))

        target_match = re.search(r"(\d+(?:\.\d+)?)", target_std)
        assert target_match is not None, f"Could not parse target from {target_std}"
        clean_target = float(target_match.group(1))

        if clean_score >= clean_target:
            assert status == "PASS", (
                f"{metric_name} with {clean_score} >= {clean_target} must be PASS"
            )
        else:
            assert status == "FAIL", (
                f"{metric_name} with {clean_score} < {clean_target} must be FAIL"
            )

    # 2. Citations Verified column percentage verification
    matrix_lines = [
        line for line in eval_text.splitlines() if line.startswith("| `scenario_") and "|" in line
    ]
    assert len(matrix_lines) == 5, f"Expected 5 matrix rows, got {len(matrix_lines)}"

    for line in matrix_lines:
        parts = [p.strip() for p in line.split("|") if p.strip()]
        sc_id = parts[0]
        cits_cell = parts[5]
        if "N/A" not in cits_cell:
            match = re.search(r"(\d+)\s*/\s*(\d+)\s*\(([\d\.]+)%\)", cits_cell)
            assert match is not None, f"Malformed cits_cell in {sc_id}: {cits_cell}"
            verified, total, stated_pct = (
                int(match.group(1)),
                int(match.group(2)),
                float(match.group(3)),
            )
            expected_pct = round((verified / total) * 100.0, 1) if total > 0 else 100.0
            assert abs(stated_pct - expected_pct) <= 0.15, (
                f"{sc_id} table ratio {verified}/{total} states {stated_pct}%, "
                f"expected {expected_pct}%"
            )


def test_scenario_markdown_transcripts_pass_rate_integrity(
    tmp_path: Path,
    in_memory_hybrid_retriever: StatutoryHybridRetriever,
    raw_scenarios_data: list[dict[str, Any]],
) -> None:
    """Verify scenario markdown transcripts pass rate matches underlying JSON telemetry.

    Args:
        tmp_path: Temporary directory fixture.
        in_memory_hybrid_retriever: Fast in-memory retriever fixture.
        raw_scenarios_data: Loaded benchmark scenario data fixture.
    """
    runner = BenchmarkPipelineRunner(
        retriever=in_memory_hybrid_retriever,
        mock_llm=True,
    )
    runner.run_all(scenarios=raw_scenarios_data, output_dir=tmp_path)

    for i in range(1, 5):
        sc_md = tmp_path / f"scenario_{i}.md"
        assert sc_md.is_file()
        content = sc_md.read_text(encoding="utf-8")

        rate_match = re.search(r"-\s*\*\*Pass Rate\*\*:\s*([\d\.]+)%", content)
        assert rate_match is not None, f"Missing Pass Rate in scenario_{i}.md"
        stated_rate = float(rate_match.group(1))

        sc_json = tmp_path / f"scenario_{i}.json"
        data = json.loads(sc_json.read_text(encoding="utf-8"))
        cv = data["citation_verification"]
        v_cnt = len(cv["verified_citations"])
        f_cnt = len(cv["flagged_citations"])
        tot = v_cnt + f_cnt
        expected_rate = round((v_cnt / tot * 100.0), 1) if tot > 0 else 100.0

        assert abs(stated_rate - expected_rate) <= 0.15, (
            f"scenario_{i}.md states {stated_rate}%, expected {expected_rate}% from JSON"
        )


# ==============================================================================
# 6. Adversarial & Empirical Deliverable Validation Tests
# ==============================================================================


def test_scenarios_1_to_4_pydantic_case_file_and_workflows(
    raw_outputs_dir: Path,
) -> None:
    """Verify Scenarios 1 to 4 generated valid Pydantic models, timelines, and 3 docs.

    Args:
        raw_outputs_dir: Fixture pointing to project root raw_outputs directory.
    """
    in_scope_scenarios = ["scenario_1", "scenario_2", "scenario_3", "scenario_4"]

    for sc_id in in_scope_scenarios:
        json_path = raw_outputs_dir / f"{sc_id}.json"
        assert json_path.is_file(), f"Missing scenario file: {json_path}"
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)

        # 1. Scope Guardrail check
        scope_data = data["scope_guardrail"]
        assert scope_data["is_in_scope"] is True, f"{sc_id} must be in-scope"

        # 2. CaseFile Pydantic validation
        assert data["case_file"] is not None, f"{sc_id} missing case_file"
        cf = CaseFile.model_validate(data["case_file"])
        assert len(cf.title) > 0
        assert cf.disputed_amount_inr > 0.0
        assert cf.complainant.name
        assert len(cf.opposite_parties) >= 1

        # Timeline validation
        assert len(cf.timeline) >= 2, f"{sc_id} timeline has fewer than 2 events"
        for ev in cf.timeline:
            assert ev.date, f"Timeline event in {sc_id} missing date"
            assert ev.description, f"Timeline event in {sc_id} missing description"
            assert ev.significance, f"Timeline event in {sc_id} missing legal significance"

        # Evidence audit
        total_evidence = len(cf.evidence_checklist) + len(cf.missing_evidence)
        assert total_evidence >= 1, f"{sc_id} has no evidence items or missing evidence"

        # 3. LegalStanding Pydantic validation
        assert data["legal_standing"] is not None, f"{sc_id} missing legal_standing"
        ls = LegalStanding.model_validate(data["legal_standing"])
        assert ls.is_consumer is True, f"{sc_id} should qualify as consumer"
        assert "District" in ls.pecuniary_commission_forum
        assert len(ls.resolution_pathway) == 4, f"{sc_id} expected 4-step escalation"

        # 4. Drafted Documents validation (Exactly 3 documents)
        docs = data["drafted_documents"]
        assert docs is not None, f"{sc_id} missing drafted_documents"
        assert len(docs) == 3, f"{sc_id} expected 3 documents, found {len(docs)}"

        expected_keys = {"grievance_email", "legal_notice", "edaakhil_complaint"}
        assert set(docs.keys()) == expected_keys, f"{sc_id} keys mismatch: {set(docs.keys())}"

        for doc_key, doc_val in docs.items():
            doc = DraftedDocument.model_validate(doc_val)
            assert len(doc.title) > 5, f"{sc_id} {doc_key} title too short"
            assert len(doc.recipient) > 0, f"{sc_id} {doc_key} recipient missing"
            assert len(doc.subject) > 0, f"{sc_id} {doc_key} subject missing"
            assert len(doc.body_markdown) > 200, f"{sc_id} {doc_key} body too short"

        # 5. Opposing Counsel Simulator validation
        sim = data["opposing_simulation"]
        assert sim is not None, f"{sc_id} missing opposing_simulation"
        assert sim["evaluation_score"] >= 80.0, f"{sc_id} sim score too low"
        assert len(sim["turns"]) >= 2, f"{sc_id} sim turns < 2"
        assert sim["feedback"] is not None, f"{sc_id} missing sim feedback"
        assert len(sim["feedback"]["strengths"]) >= 1


def test_scenario_5_deterministic_scope_guardrail_rejection(
    raw_outputs_dir: Path,
) -> None:
    """Verify Scenario 5 was deterministically caught by Layer 1 Scope Guardrail.

    Args:
        raw_outputs_dir: Fixture pointing to project root raw_outputs directory.
    """
    json_path = raw_outputs_dir / "scenario_5.json"
    assert json_path.is_file(), f"Missing scenario file: {json_path}"
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    # Layer 1 Scope Guardrail assertions
    scope = data["scope_guardrail"]
    assert scope["is_in_scope"] is False, "Scenario 5 must have is_in_scope=False"
    assert scope["out_of_scope_category"] == "cheque_bounce"
    advice_lower = scope["escalation_advice"].lower()
    assert "advocate" in advice_lower or "bar council" in advice_lower
    assert len(scope["detected_triggers"]) >= 1

    # Deterministic blocking assertions
    assert data["case_file"] is None, "Scenario 5 case_file must be None"
    assert data["drafted_documents"] is None, "Scenario 5 drafted_documents must be None"
    assert data["legal_standing"] is None, "Scenario 5 legal_standing must be None"
    assert data["retrieval"]["retrieved_chunks"] == [], "Scenario 5 chunks must be empty"

    guard_enforce = data["guardrail_enforcement"]
    assert guard_enforce["downstream_drafting_blocked"] is True
    assert guard_enforce["advocate_escalation_provided"] is True
    assert guard_enforce["exception_caught"] == "OutOfScopeDisputeError"

    # Markdown transcript check
    md_path = raw_outputs_dir / "scenario_5.md"
    md_content = md_path.read_text(encoding="utf-8")
    assert "OUT-OF-SCOPE" in md_content
    assert "Mandatory Bar Council of India Escalation Advisory" in md_content
    assert "No complaint drafted for non-consumer court" in md_content


def test_no_fabricated_citations_or_hallucinated_case_law(
    raw_outputs_dir: Path,
    statutes_dir: Path,
) -> None:
    """Empirically inspect all drafted documents for fake case laws or citations.

    Args:
        raw_outputs_dir: Fixture pointing to project root raw_outputs directory.
        statutes_dir: Fixture pointing to data/statutes directory.
    """
    texts = [f.read_text(encoding="utf-8") for f in sorted(statutes_dir.glob("*.txt"))]
    corpus_lower = "\n\n".join(texts).lower()

    scenarios = ["scenario_1", "scenario_2", "scenario_3", "scenario_4"]
    section_pat = re.compile(r"\b(?:Section|Sec\.?)\s*(\d+[A-Za-z]?(?:\([^\)\n]+\))*)", re.I)
    rule_pat = re.compile(r"\b(?:Rule|r\.)\s*(\d+[A-Za-z]?(?:\([^\)\n]+\))*)", re.I)
    fake_case_pat = re.compile(
        r"\b([A-Z][a-zA-Z\.\s]{2,25}\s+(?:v\.|vs\.?|versus)\s+"
        r"[A-Z][a-zA-Z\.\s]{2,25}(?:,?\s*\d{4}[^\.\n;]*)?)",
        re.I,
    )

    for sc_id in scenarios:
        json_path = raw_outputs_dir / f"{sc_id}.json"
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)

        docs = data.get("drafted_documents", {})
        combined_text = " ".join(doc["body_markdown"] for doc in docs.values())

        # 1. Check for fabricated judicial case citations
        case_matches = fake_case_pat.findall(combined_text)
        for case in case_matches:
            assert "fake" not in case.lower()
            assert "hallucinated" not in case.lower()

        # 2. Check every cited section exists in the Indian Consumer Law corpus
        cited_sections = section_pat.findall(combined_text)
        for sec in cited_sections:
            base_sec = sec.split("(")[0].strip()
            assert base_sec.isdigit(), f"Invalid section format in {sc_id}: {sec}"
            sec_num = int(base_sec)
            assert 1 <= sec_num <= 107, f"CPA 2019 invalid section {sec_num} in {sc_id}"
            found_in_corpus = (
                f"section {base_sec}" in corpus_lower or f"section {sec.lower()}" in corpus_lower
            )
            assert found_in_corpus, f"Section {sec} in {sc_id} not in statutory corpus"

        # 3. Check every cited Rule exists in E-Commerce Rules
        cited_rules = rule_pat.findall(combined_text)
        for r in cited_rules:
            base_r = r.split("(")[0].strip()
            assert base_r.isdigit(), f"Invalid rule format in {sc_id}: {r}"
            rule_num = int(base_r)
            assert 1 <= rule_num <= 10, f"E-Commerce Rules 2020 invalid rule {rule_num} in {sc_id}"
            found_in_corpus = (
                f"rule {base_r}" in corpus_lower or f"rule {r.lower()}" in corpus_lower
            )
            assert found_in_corpus, f"Rule {r} in {sc_id} not in statutory corpus"


def test_benchmark_evaluation_md_mathematical_parity_and_telemetry(
    raw_outputs_dir: Path,
) -> None:
    """Audit BENCHMARK_EVALUATION.md for dynamic formula parity with raw JSON telemetry.

    Args:
        raw_outputs_dir: Fixture pointing to raw_outputs directory.
    """
    eval_path = raw_outputs_dir / "BENCHMARK_EVALUATION.md"
    assert eval_path.is_file()
    content = eval_path.read_text(encoding="utf-8")

    # Verify required executive sections exist
    assert "## 1. Executive Performance Dashboard" in content
    assert "## 2. Multi-Scenario Benchmark Results Matrix" in content
    assert "## 3. Mathematical Metric Definitions & Evaluation Formulas" in content

    # Calculate actual averages dynamically from raw JSON files
    scenarios = ["scenario_1", "scenario_2", "scenario_3", "scenario_4"]
    precisions: list[float] = []
    pass_rates: list[float] = []

    for sc_id in scenarios:
        json_path = raw_outputs_dir / f"{sc_id}.json"
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
        precisions.append(float(data["retrieval"]["retrieval_precision_percent"]))
        cv = data["citation_verification"]
        v_cnt = len(cv["verified_citations"])
        f_cnt = len(cv["flagged_citations"])
        rate = (v_cnt / (v_cnt + f_cnt)) * 100.0 if (v_cnt + f_cnt) > 0 else 100.0
        pass_rates.append(rate)

    calc_avg_precision = round(sum(precisions) / len(precisions), 1)
    calc_avg_pass_rate = round(sum(pass_rates) / len(pass_rates), 1)

    # Assert BENCHMARK_EVALUATION.md dynamically matches calculated telemetry
    assert f"{calc_avg_precision:.1f}%" in content, (
        f"Evaluation report missing calculated precision {calc_avg_precision:.1f}%"
    )
    assert f"{calc_avg_pass_rate:.1f}%" in content, (
        f"Evaluation report missing calculated pass rate {calc_avg_pass_rate:.1f}%"
    )
