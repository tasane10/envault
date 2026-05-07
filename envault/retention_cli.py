"""CLI commands for managing variable retention policies."""

from __future__ import annotations

import click

from envault.cli import cli, prompt_password
from envault.profiles import get_profile_vault_path, load_profile, save_profile
from envault.retention import find_expired, get_retention, purge_expired, remove_retention, set_retention


@cli.group("retention")
def retention_cmd() -> None:
    """Manage variable retention policies."""


@retention_cmd.command("set")
@click.argument("key")
@click.argument("days", type=int)
@click.option("--profile", default="default", show_default=True)
def set_retention_cmd(key: str, days: int, profile: str) -> None:
    """Set a retention policy of DAYS days on KEY."""
    password = prompt_password()
    vault_path = get_profile_vault_path(profile)
    variables = load_profile(vault_path, password)
    try:
        variables = set_retention(variables, key, days)
    except (KeyError, ValueError) as exc:
        raise click.ClickException(str(exc))
    save_profile(vault_path, variables, password)
    click.echo(f"Retention policy set: '{key}' will expire after {days} day(s).")


@retention_cmd.command("remove")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def remove_retention_cmd(key: str, profile: str) -> None:
    """Remove the retention policy from KEY."""
    password = prompt_password()
    vault_path = get_profile_vault_path(profile)
    variables = load_profile(vault_path, password)
    variables = remove_retention(variables, key)
    save_profile(vault_path, variables, password)
    click.echo(f"Retention policy removed from '{key}'.")


@retention_cmd.command("show")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def show_retention_cmd(key: str, profile: str) -> None:
    """Show the retention policy for KEY."""
    password = prompt_password()
    vault_path = get_profile_vault_path(profile)
    variables = load_profile(vault_path, password)
    days = get_retention(variables, key)
    if days is None:
        click.echo(f"No retention policy set for '{key}'.")
    else:
        click.echo(f"'{key}' expires after {days} day(s).")


@retention_cmd.command("purge")
@click.option("--profile", default="default", show_default=True)
@click.option("--dry-run", is_flag=True, help="List expired keys without deleting.")
def purge_cmd(profile: str, dry_run: bool) -> None:
    """Delete all variables whose retention period has elapsed."""
    password = prompt_password()
    vault_path = get_profile_vault_path(profile)
    variables = load_profile(vault_path, password)
    expired = find_expired(variables)
    if not expired:
        click.echo("No expired variables found.")
        return
    for key in expired:
        click.echo(f"  {'[dry-run] would remove' if dry_run else 'removing'}: {key}")
    if not dry_run:
        variables, _ = purge_expired(variables)
        save_profile(vault_path, variables, password)
        click.echo(f"Purged {len(expired)} variable(s).")
