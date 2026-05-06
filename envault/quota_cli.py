"""CLI commands for quota management."""

from __future__ import annotations

import click

from envault.cli import prompt_password
from envault.profiles import get_profile_vault_path, load_profile, save_profile
from envault.quota import set_quota, remove_quota, check_quota, get_quota


@click.group("quota")
def quota_cmd() -> None:
    """Manage variable quota limits for a profile."""


@quota_cmd.command("set")
@click.argument("limit", type=int)
@click.option("--profile", default="default", show_default=True)
def set_quota_cmd(limit: int, profile: str) -> None:
    """Set the maximum number of variables allowed in PROFILE."""
    password = prompt_password()
    variables = load_profile(profile, password)
    try:
        updated = set_quota(variables, limit)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    save_profile(profile, updated, password)
    click.echo(f"Quota set to {limit} for profile '{profile}'.")


@quota_cmd.command("remove")
@click.option("--profile", default="default", show_default=True)
def remove_quota_cmd(profile: str) -> None:
    """Remove the quota limit from PROFILE."""
    password = prompt_password()
    variables = load_profile(profile, password)
    updated = remove_quota(variables)
    save_profile(profile, updated, password)
    click.echo(f"Quota removed for profile '{profile}'.")


@quota_cmd.command("show")
@click.option("--profile", default="default", show_default=True)
def show_quota_cmd(profile: str) -> None:
    """Show quota usage for PROFILE."""
    password = prompt_password()
    variables = load_profile(profile, password)
    info = check_quota(variables)
    limit_str = str(info["limit"]) if info["limit"] is not None else "unlimited"
    remaining_str = str(info["remaining"]) if info["remaining"] is not None else "N/A"
    click.echo(f"Profile : {profile}")
    click.echo(f"Current : {info['current']}")
    click.echo(f"Limit   : {limit_str}")
    click.echo(f"Remaining: {remaining_str}")
