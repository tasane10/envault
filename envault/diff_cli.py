"""CLI commands for diffing vault profiles."""

import click

from envault.diff import diff_variables, format_diff
from envault.profiles import load_profile
from envault.cli import prompt_password


@click.group()
def diff_cmd():
    """Diff environment variables between profiles."""


@diff_cmd.command("profiles")
@click.argument("base_profile")
@click.argument("target_profile")
@click.option("--show-values", is_flag=True, default=False, help="Show actual values (not masked).")
def diff_profiles_cmd(base_profile: str, target_profile: str, show_values: bool):
    """Show differences between BASE_PROFILE and TARGET_PROFILE."""
    password = prompt_password(confirm=False)

    try:
        base_vars = load_profile(base_profile, password)
    except Exception as exc:
        raise click.ClickException(f"Could not load profile '{base_profile}': {exc}") from exc

    try:
        target_vars = load_profile(target_profile, password)
    except Exception as exc:
        raise click.ClickException(f"Could not load profile '{target_profile}': {exc}") from exc

    diff = diff_variables(base_vars, target_vars)

    click.echo(f"Diff: {base_profile} -> {target_profile}")
    click.echo(format_diff(diff, show_values=show_values))
    if diff:
        click.echo(f"\n{len(diff)} variable(s) differ.")
