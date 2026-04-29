"""CLI commands for environment health checks."""

from __future__ import annotations

import os

import click

from envault.env_check import check_variables, format_check_results
from envault.profiles import load_profile
from envault.cli import prompt_password


@click.group(name="check")
def check_cmd() -> None:
    """Check vault variables against the current environment."""


@check_cmd.command(name="run")
@click.option("--profile", default="default", show_default=True, help="Profile to check.")
@click.option("--status", type=click.Choice(["ok", "missing", "mismatch"]), default=None,
              help="Filter output to a specific status.")
@click.option("--fail-on-missing", is_flag=True, default=False,
              help="Exit with non-zero code if any variables are missing.")
@click.option("--fail-on-mismatch", is_flag=True, default=False,
              help="Exit with non-zero code if any variables are mismatched.")
def run_cmd(
    profile: str,
    status: str | None,
    fail_on_missing: bool,
    fail_on_mismatch: bool,
) -> None:
    """Compare vault variables for PROFILE against the current shell environment."""
    password = prompt_password(confirm=False)
    try:
        vault_vars = load_profile(profile, password)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc

    results = check_variables(vault_vars, dict(os.environ))

    if status:
        results = [r for r in results if r["status"] == status]

    click.echo(format_check_results(results))

    has_missing = any(r["status"] == "missing" for r in results)
    has_mismatch = any(r["status"] == "mismatch" for r in results)

    if (fail_on_missing and has_missing) or (fail_on_mismatch and has_mismatch):
        raise SystemExit(1)


@check_cmd.command(name="summary")
@click.option("--profile", default="default", show_default=True, help="Profile to check.")
def summary_cmd(profile: str) -> None:
    """Print a one-line summary of vault vs environment health."""
    password = prompt_password(confirm=False)
    try:
        vault_vars = load_profile(profile, password)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc

    results = check_variables(vault_vars, dict(os.environ))
    ok = sum(1 for r in results if r["status"] == "ok")
    missing = sum(1 for r in results if r["status"] == "missing")
    mismatched = sum(1 for r in results if r["status"] == "mismatch")
    total = len(results)
    click.echo(
        f"Profile '{profile}': {total} variables — "
        f"{ok} ok, {missing} missing, {mismatched} mismatched"
    )
