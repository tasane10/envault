"""Unified CLI entry-point that registers all command groups.

This module wires together every sub-command group so that the project
has a single ``envault`` binary defined in pyproject.toml::

    [project.scripts]
    envault = "envault.cli_main:main"
"""

import click
from envault.cli import cli  # base group + set/get/list/delete
from envault.audit_cli import audit_cmd
from envault.diff_cli import diff_cmd, diff_profiles_cmd
from envault.rotate_cli import rotate_cmd


# Attach sub-command groups to the root CLI
cli.add_command(audit_cmd, name="audit")
cli.add_command(diff_cmd, name="diff")
cli.add_command(diff_profiles_cmd, name="diff-profiles")
cli.add_command(rotate_cmd, name="rotate")


def main():
    """Entry-point for the ``envault`` binary."""
    cli()


if __name__ == "__main__":  # pragma: no cover
    main()
