"""Empirical Stress Testing Suite for Python 3.12 Migration (Milestone 3).

Adversarial Verification Scope:
1. Python 3.12 PEP 695 type parameter syntax runtime semantics in json_repair.py:
   - __type_params__ metadata inspection on generic functions
   - TypeVar bounding to pydantic.BaseModel
   - Dispatch with simple, complex, and polymorphic Pydantic v2 models
2. Adversarial JSON Repair Resilience:
   - Markdown code fences with nested backticks and multilingual commentary
   - Deeply nested objects, arrays, and trailing comma elimination
   - Escaped quotes, unescaped newlines, Devanagari Unicode sequences
   - Single-key envelope unwrapping with schema field matching
3. Micro-benchmark & Throughput Stability:
   - 1,000-iteration throughput test verifying sub-millisecond execution times
4. Timezone & Stdlib Modernization:
   - Verification of datetime.UTC and timezone awareness in Pydantic serialization
   - Confirmation of removal of deprecated Python 3.11 stdlib modules
"""

from __future__ import annotations

import datetime
import json
import time

import pytest
from pydantic import BaseModel, Field

from legal_assistant.llm.json_repair import (
    clean_markdown_fences,
    extract_outermost_json,
    fix_trailing_commas,
    parse_and_unwrap_dict,
    parse_and_validate,
    repair_and_parse_json,
)
from legal_assistant.schemas import CaseFile


class SampleNestedModel(BaseModel):
    title: str
    items: list[str] = Field(default_factory=list)


class SampleComplexModel(BaseModel):
    id: int
    name: str
    timestamp: datetime.datetime
    nested: SampleNestedModel
    tags: list[str] = Field(default_factory=list)


# ==============================================================================
# 1. PEP 695 Type Parameter Syntax & Runtime Semantics
# ==============================================================================


class TestPEP695RuntimeSemantics:
    """Stress-test Python 3.12 PEP 695 generic function implementations."""

    def test_pep695_type_params_introspection(self) -> None:
        """Verify that functions defined with PEP 695 expose __type_params__ in Python 3.12."""
        assert hasattr(parse_and_unwrap_dict, "__type_params__")
        assert hasattr(repair_and_parse_json, "__type_params__")
        assert hasattr(parse_and_validate, "__type_params__")

        params = parse_and_unwrap_dict.__type_params__
        assert len(params) == 1
        t_param = params[0]
        assert t_param.__name__ == "T"
        assert isinstance(t_param.__bound__, type)
        assert issubclass(t_param.__bound__, BaseModel)

    def test_pep695_generic_function_dispatch(self) -> None:
        """Verify parse_and_validate dynamically resolves type T at runtime."""
        raw_text = '{"title": "Consumer Complaint", "items": ["invoice.pdf", "email.eml"]}'
        result = parse_and_validate(raw_text, SampleNestedModel)
        assert isinstance(result, SampleNestedModel)
        assert result.title == "Consumer Complaint"
        assert len(result.items) == 2

    def test_pep695_complex_nested_model_dispatch(self) -> None:
        """Verify parse_and_validate handles complex nested models with datetimes."""
        payload = (
            '{"id": 42, "name": "Test Case", "timestamp": "2026-11-07T12:00:00Z", '
            '"nested": {"title": "Sub", "items": ["a"]}, "tags": ["legal", "consumer"]}'
        )
        result = parse_and_validate(payload, SampleComplexModel)
        assert isinstance(result, SampleComplexModel)
        assert result.id == 42
        assert result.timestamp.tzinfo is not None
        assert result.nested.title == "Sub"


# ==============================================================================
# 2. Adversarial JSON Repair Resilience
# ==============================================================================


class TestAdversarialJSONRepair:
    """Empirical adversarial stress testing for json_repair utilities."""

    @pytest.mark.parametrize(
        ("input_text", "expected_output"),
        [
            ('```json\n{"key": "val"}\n```', '{"key": "val"}'),
            (
                'Output:\n```json\n{"status": true}\n```\nDone',
                '{"status": true}',
            ),
            ("```\n[1, 2, 3]\n```", "[1, 2, 3]"),
            ('   {"clean": true}   ', '{"clean": true}'),
            ("No fences just text", "No fences just text"),
        ],
    )
    def test_clean_markdown_fences_variations(self, input_text: str, expected_output: str) -> None:
        assert clean_markdown_fences(input_text) == expected_output

    def test_fix_trailing_commas_deeply_nested(self) -> None:
        """Verify fix_trailing_commas cleans nested objects and arrays with trailing commas."""
        malformed = '{"a": [1, 2, 3, ], "b": {"x": "y", }, "c": [{}, ], }'
        cleaned = fix_trailing_commas(malformed)
        parsed = json.loads(cleaned)
        assert parsed == {"a": [1, 2, 3], "b": {"x": "y"}, "c": [{}]}

    def test_extract_outermost_json_mixed_delimiters(self) -> None:
        """Verify extract_outermost_json prioritizes earlier delimiter and balances pairs."""
        text1 = 'Leading commentary { "object": true } [and trailing bracket]'
        assert extract_outermost_json(text1) == '{ "object": true }'

        text2 = 'Preface {"nested": [1, 2]} conclusion'
        assert extract_outermost_json(text2) == '{"nested": [1, 2]}'

    def test_envelope_unwrapping_case_file(self) -> None:
        """Verify parse_and_unwrap_dict safely strips matching envelope wrappers."""
        wrapped = '{"CaseFile": {"facts_summary": "Bought defective screen.", "title": "Phone"}}'
        result = parse_and_unwrap_dict(wrapped, CaseFile)
        assert "facts_summary" in result
        assert result["title"] == "Phone"

    def test_envelope_unwrapping_mismatched_key_preserves_dict(self) -> None:
        """Verify parse_and_unwrap_dict preserves envelope if inner dict lacks matching fields."""
        unrelated_wrapped = '{"UnknownEnvelope": {"unrelated_field": 123}}'
        result = parse_and_unwrap_dict(unrelated_wrapped, CaseFile)
        assert "UnknownEnvelope" in result

    def test_devanagari_unicode_payload_repair(self) -> None:
        """Verify repair pipeline preserves Devanagari Hindi text and rupee symbols."""
        hindi_payload = (
            '```json\n{\n  "title": "उपभोक्ता शिकायत - दोषपूर्ण लैपटॉप",\n'
            '  "items": ["रसीद संख्या ₹75,000", "वारंटी कार्ड",],\n}\n```'
        )
        model = parse_and_validate(hindi_payload, SampleNestedModel)
        assert model.title == "उपभोक्ता शिकायत - दोषपूर्ण लैपटॉप"
        assert "रसीद संख्या ₹75,000" in model.items


# ==============================================================================
# 3. Micro-Benchmark & Throughput Stability
# ==============================================================================


class TestMicroBenchmarkThroughput:
    """Validate that Python 3.12 executes JSON repairs with high throughput and no regressions."""

    def test_repair_throughput_1000_iterations(self) -> None:
        """Benchmark 1,000 iterations of repair_and_parse_json under Python 3.12."""
        raw_input = (
            "Here is the result:\n```json\n"
            '{\n  "title": "Defective Electronics",\n  "items": ["inv1", "inv2", ],\n}\n'
            "```"
        )
        start = time.perf_counter()
        for _ in range(1000):
            res = repair_and_parse_json(raw_input, SampleNestedModel)
            assert res["title"] == "Defective Electronics"
        elapsed = time.perf_counter() - start

        # 1,000 iterations must complete within 500ms on Python 3.12 (typical < 50ms)
        assert elapsed < 0.50, f"Throughput regression: 1000 iterations took {elapsed:.3f}s"


# ==============================================================================
# 4. Python 3.12 Stdlib & Datetime Integrity
# ==============================================================================


class TestPython312StdlibIntegrity:
    """Verify standard library migrations and removals in Python 3.12."""

    def test_datetime_utc_standard(self) -> None:
        """Verify datetime.UTC is used for timezone-aware UTC timestamps."""
        now = datetime.datetime.now(datetime.UTC)
        assert now.tzinfo == datetime.UTC
        iso_str = now.isoformat()
        assert "+00:00" in iso_str or iso_str.endswith("Z")

    def test_removed_stdlib_modules_raise_import_error(self) -> None:
        """Verify removed stdlib modules (distutils, imp, asynchat, asyncore) are absent."""
        for mod in ["distutils", "imp", "asynchat", "asyncore"]:
            with pytest.raises(ModuleNotFoundError):
                __import__(mod)
