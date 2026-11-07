"""Robust JSON extraction, cleaning, and schema repair utilities.

This module provides deterministic multi-pass extraction and syntax repair for
LLM-generated JSON strings, handling markdown fences, trailing commas, single-key
envelope wrappers, and Pydantic v2 model validation.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def clean_markdown_fences(text: str) -> str:
    """Strip markdown code block fences and surrounding explanatory text.

    Args:
        text: Raw text string from LLM response.

    Returns:
        Stripped string with code fences removed.
    """
    text = text.strip()
    fence_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    match = re.search(fence_pattern, text)
    if match:
        return match.group(1).strip()
    return text


def extract_outermost_json(text: str) -> str:
    """Locate the outermost JSON object or array substring within text.

    Strictly pairs opening braces `{` with closing braces `}` and opening
    brackets `[` with closing brackets `]`, preventing mismatched delimiter
    trapping.

    Args:
        text: Text containing potential JSON data.

    Returns:
        Substring from the first opening delimiter to its matching last closing delimiter.
    """
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    brace_valid = first_brace != -1 and last_brace > first_brace

    first_bracket = text.find("[")
    last_bracket = text.rfind("]")
    bracket_valid = first_bracket != -1 and last_bracket > first_bracket

    if brace_valid and bracket_valid:
        if first_brace < first_bracket:
            return text[first_brace : last_brace + 1]
        return text[first_bracket : last_bracket + 1]
    elif brace_valid:
        return text[first_brace : last_brace + 1]
    elif bracket_valid:
        return text[first_bracket : last_bracket + 1]

    return text


# Alias for backward compatibility
extract_outermost_json_substring = extract_outermost_json


def fix_trailing_commas(text: str) -> str:
    """Remove trailing commas preceding closing braces or brackets.

    Args:
        text: JSON-like string.

    Returns:
        String with trailing commas removed.
    """
    return re.sub(r",\s*([}\]])", r"\1", text)


def repair_json_string(text: str) -> str:
    """Execute a multi-pass repair pipeline on an LLM-generated JSON string.

    Args:
        text: Raw generated output from an LLM.

    Returns:
        Cleaned JSON string ready for parsing.
    """
    cleaned = clean_markdown_fences(text)
    cleaned = extract_outermost_json(cleaned)
    cleaned = fix_trailing_commas(cleaned)
    return cleaned.strip()


def parse_and_unwrap_dict(raw_json: str, schema: type[T]) -> dict[str, Any]:
    """Parse JSON string and unwrap single-key envelope wrappers if necessary.

    Args:
        raw_json: Cleaned JSON string.
        schema: Target Pydantic model class.

    Returns:
        Parsed dictionary ready for schema validation.

    Raises:
        json.JSONDecodeError: If string is fundamentally unparseable as JSON.
        ValueError: If parsed JSON is not a JSON object (dict).
    """
    data = json.loads(raw_json)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object (dict), got {type(data).__name__}")

    schema_fields = set(schema.model_fields.keys())

    # If the dictionary already contains matching fields, return directly
    if bool(schema_fields.intersection(data.keys())):
        return data

    # Check if data has a single envelope key wrapping the payload (e.g. {"CaseFile": {...}})
    if len(data) == 1:
        key, inner_value = next(iter(data.items()))
        if isinstance(inner_value, dict) and bool(schema_fields.intersection(inner_value.keys())):
            logger.debug("Unwrapped single-key envelope wrapper: %s", key)
            return inner_value

    return data


def repair_and_parse_json(text: str, schema: type[T] | None = None) -> Any:
    """Execute multi-pass repair and parse text into Python object/dict.

    Args:
        text: Raw generated text.
        schema: Optional Pydantic model for envelope unwrapping.

    Returns:
        Parsed Python dictionary, list, or primitive.
    """
    repaired = repair_json_string(text)
    if schema is not None:
        return parse_and_unwrap_dict(repaired, schema)
    return json.loads(repaired)


def parse_and_validate(text: str, schema: type[T]) -> T:
    """Parse, repair, and validate an LLM text output into a Pydantic model instance.

    Args:
        text: Raw text string from the LLM.
        schema: Target Pydantic model class.

    Returns:
        Validated instance of model schema T.

    Raises:
        ValidationError: If validated data violates Pydantic constraints.
        json.JSONDecodeError: If JSON decoding fails after all repair passes.
        ValueError: If repaired JSON payload is not an object.
    """
    # Attempt 1: Direct validation if string is already clean JSON
    try:
        return schema.model_validate_json(text)
    except (ValidationError, ValueError):
        pass

    # Attempt 2: Multi-pass string repair
    repaired_text = repair_json_string(text)
    try:
        data_dict = parse_and_unwrap_dict(repaired_text, schema)
        return schema.model_validate(data_dict)
    except (ValidationError, ValueError) as exc:
        logger.warning("Local JSON repair failed to validate against %s: %s", schema.__name__, exc)
        raise
