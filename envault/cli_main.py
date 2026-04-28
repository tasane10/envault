"""Entry point that assembles all CLI command groups."""

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


cli.add_command(audit_cmd, name="audit")
cli.add_command(diff_cmd, name="diff")
cli.add_command(rotate_cmd, name="rotate")
cli.add_command(search_cmd, name="search")
cli.add_command(copy_cmd, name="copy")
cli.add_command(snapshot_cmd, name="snapshot")
cli.add_command(tag_cmd, name="tag")
cli.add_command(ttl_cmd, name="ttl")
cli.add_command(template_cmd, name="template")
cli.add_command(lint_cmd, name="lint")
cli.add_command(alias_cmd, name="alias")
cli.add_command(watch_cmd, name="watch")


def main():
    cli()


if __name__ == "__main__":
    main()
