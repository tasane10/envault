"""Schema validation for environment variable keys and values."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class FieldSchema:
    """Schema definition for a single environment variable."""
    required: bool = False
    pattern: Optional[str] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    allowed_values: Optional[List[str]] = None
    description: str = ""


@dataclass
class ValidationError:
    key: str
    message: str
    severity: str = "error"  # "error" or "warning"


def validate_variables(
    variables: Dict[str, Any],
    schema: Dict[str, FieldSchema],
) -> List[ValidationError]:
    """Validate variables against a schema. Returns a list of ValidationErrors."""
    errors: List[ValidationError] = []
    data = {k: v for k, v in variables.items() if not k.startswith("__")}

    for key, field_schema in schema.items():
        if field_schema.required and key not in data:
            errors.append(ValidationError(key=key, message=f"Required variable '{key}' is missing."))
            continue

        value = data.get(key)
        if value is None:
            continue

        if field_schema.min_length is not None and len(value) < field_schema.min_length:
            errors.append(ValidationError(
                key=key,
                message=f"Value too short (min {field_schema.min_length} chars).",
            ))

        if field_schema.max_length is not None and len(value) > field_schema.max_length:
            errors.append(ValidationError(
                key=key,
                message=f"Value too long (max {field_schema.max_length} chars).",
            ))

        if field_schema.pattern is not None and not re.fullmatch(field_schema.pattern, value):
            errors.append(ValidationError(
                key=key,
                message=f"Value does not match required pattern '{field_schema.pattern}'.",
            ))

        if field_schema.allowed_values is not None and value not in field_schema.allowed_values:
            allowed = ", ".join(field_schema.allowed_values)
            errors.append(ValidationError(
                key=key,
                message=f"Value '{value}' not in allowed values: [{allowed}].",
            ))

    return errors


def format_validation_results(errors: List[ValidationError]) -> str:
    """Format validation errors into a human-readable string."""
    if not errors:
        return "All variables passed schema validation."
    lines = []
    for err in errors:
        prefix = "ERROR" if err.severity == "error" else "WARN"
        lines.append(f"[{prefix}] {err.key}: {err.message}")
    return "\n".join(lines)
