"""Entry-point that wires all sub-command groups into the root CLI."""

from __future__ import annotations

import click

from envault.cli import cli
from envault.audit_cli import audit_cmd
from envault.diff_cli import diff_cmd
from envault.rotate_cli import rotate_cmd
from envault.search_cli import search_cmd
from envault.copy_cli import copy_cmd
from envault.snapshot_cli import snapshot_cmd
from envault.tag_cli import tag_cmd
from envault.ttl_cli import ttl_cmd
from envault.template_cli import template_cmd
from envault.lint_cli import lint_cmd
from envault.alias_cli import alias_cmd
from envault.watch_cli import watch_cmd
from envault.schema_cli import schema_cmd
from envault.env_check_cli import check_cmd
from envault.share_cli import share_cmd


cli.add_command(audit_cmd)
cli.add_command(diff_cmd)
cli.add_command(rotate_cmd)
cli.add_command(search_cmd)
cli.add_command(copy_cmd)
cli.add_command(snapshot_cmd)
cli.add_command(tag_cmd)
cli.add_command(ttl_cmd)
cli.add_command(template_cmd)
cli.add_command(lint_cmd)
cli.add_command(alias_cmd)
cli.add_command(watch_cmd)
cli.add_command(schema_cmd)
cli.add_command(check_cmd)
cli.add_command(share_cmd)


def main() -> None:  # pragma: no cover
    cli()
