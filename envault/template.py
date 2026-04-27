"""Template rendering for environment variable substitution."""
from __future__ import annotations

import re
from typing import Dict, Optional

_PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


def render_template(template: str, variables: Dict[str, str]) -> str:
    """Replace {{KEY}} placeholders in *template* with values from *variables*.

    Unknown placeholders are left unchanged.
    """
    def _replace(match: re.Match) -> str:
        key = match.group(1)
        return variables.get(key, match.group(0))

    return _PLACEHOLDER_RE.sub(_replace, template)


def render_template_strict(template: str, variables: Dict[str, str]) -> str:
    """Like :func:`render_template` but raise *KeyError* for unknown keys."""
    def _replace(match: re.Match) -> str:
        key = match.group(1)
        if key not in variables:
            raise KeyError(f"Template placeholder '{key}' not found in variables")
        return variables[key]

    return _PLACEHOLDER_RE.sub(_replace, template)


def extract_placeholders(template: str) -> list[str]:
    """Return a sorted, deduplicated list of placeholder names in *template*."""
    return sorted(set(_PLACEHOLDER_RE.findall(template)))


def render_file(
    template_path: str,
    variables: Dict[str, str],
    output_path: Optional[str] = None,
    strict: bool = False,
) -> str:
    """Read a template file, render it, optionally write the result.

    Returns the rendered string regardless of whether *output_path* is given.
    """
    with open(template_path, "r", encoding="utf-8") as fh:
        template = fh.read()

    rendered = render_template_strict(template, variables) if strict else render_template(template, variables)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(rendered)

    return rendered
