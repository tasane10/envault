"""Tests for envault.template."""
from __future__ import annotations

import pytest

from envault.template import (
    extract_placeholders,
    render_template,
    render_template_strict,
    render_file,
)

VARS = {"HOST": "localhost", "PORT": "5432", "DB": "mydb"}


def test_render_template_basic():
    result = render_template("{{HOST}}:{{PORT}}/{{DB}}", VARS)
    assert result == "localhost:5432/mydb"


def test_render_template_unknown_placeholder_left_unchanged():
    result = render_template("{{HOST}}:{{UNKNOWN}}", VARS)
    assert result == "localhost:{{UNKNOWN}}"


def test_render_template_whitespace_inside_braces():
    result = render_template("{{ HOST }} and {{ PORT }}", VARS)
    assert result == "localhost and 5432"


def test_render_template_no_placeholders():
    text = "plain text without any placeholders"
    assert render_template(text, VARS) == text


def test_render_template_empty_variables():
    result = render_template("{{HOST}}", {})
    assert result == "{{HOST}}"


def test_render_template_strict_raises_on_unknown():
    with pytest.raises(KeyError, match="UNKNOWN"):
        render_template_strict("{{HOST}}:{{UNKNOWN}}", VARS)


def test_render_template_strict_succeeds_when_all_known():
    result = render_template_strict("{{HOST}}:{{PORT}}", VARS)
    assert result == "localhost:5432"


def test_extract_placeholders_returns_sorted_unique():
    template = "{{B}} {{A}} {{B}} {{C}}"
    assert extract_placeholders(template) == ["A", "B", "C"]


def test_extract_placeholders_empty_when_none():
    assert extract_placeholders("no placeholders here") == []


def test_render_file_reads_and_renders(tmp_path):
    tmpl = tmp_path / "app.conf"
    tmpl.write_text("host={{HOST}} port={{PORT}}")
    result = render_file(str(tmpl), VARS)
    assert result == "host=localhost port=5432"


def test_render_file_writes_output(tmp_path):
    tmpl = tmp_path / "app.conf"
    out = tmp_path / "app.rendered.conf"
    tmpl.write_text("db={{DB}}")
    render_file(str(tmpl), VARS, output_path=str(out))
    assert out.read_text() == "db=mydb"


def test_render_file_strict_raises(tmp_path):
    tmpl = tmp_path / "app.conf"
    tmpl.write_text("{{MISSING}}")
    with pytest.raises(KeyError):
        render_file(str(tmpl), VARS, strict=True)
