"""CLI commands for managing variable expiry policies."""

from __future__ import annotations

import time
from datetime import datetime, timezone

import click

from envault.expiry import get_expiry, set_expiry, remove_expiry, list_expiring, purge_expired
from envault.storage import get_vault_path, load_vault, save_vault
from envault.cli import prompt_password


@click.group("expiry")
def expiry_cmd() -> None:
    """Manage variable expiry dates."""


@expiry_cmd.command("set")
@click.argument("key")
@click.argument("expires_at")
@click.option("--profile", default="default", show_default=True)
def set_expiry_cmd(key: str, expires_at: str, profile: str) -> None:
    """Set expiry for KEY as an ISO datetime or UNIX timestamp."""
    try:
        ts = float(expires_at)
    except ValueError:
        try:
            dt = datetime.fromisoformat(expires_at)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            ts = dt.timestamp()
        except ValueError:
            raise click.BadParameter(f"Cannot parse datetime: {expires_at!r}", param_hint="expires_at")

    password = prompt_password()
    path = get_vault_path(profile)
    variables = load_vault(path, password)
    try:
        updated = set_expiry(variables, key, ts)
    except ValueError as exc:
        raise click.ClickException(str(exc))
    save_vault(path, updated, password)
    readable = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
    click.echo(f"Expiry set for {key!r}: {readable}")


@expiry_cmd.command("remove")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def remove_expiry_cmd(key: str, profile: str) -> None:
    """Remove expiry for KEY."""
    password = prompt_password()
    path = get_vault_path(profile)
    variables = load_vault(path, password)
    updated = remove_expiry(variables, key)
    save_vault(path, updated, password)
    click.echo(f"Expiry removed for {key!r}.")


@expiry_cmd.command("list")
@click.option("--profile", default="default", show_default=True)
def list_expiry_cmd(profile: str) -> None:
    """List all variables with expiry dates."""
    password = prompt_password()
    path = get_vault_path(profile)
    variables = load_vault(path, password)
    entries = list_expiring(variables)
    if not entries:
        click.echo("No variables with expiry set.")
        return
    for entry in entries:
        readable = datetime.fromtimestamp(entry["expires_at"], tz=timezone.utc).isoformat()
        status = "EXPIRED" if entry["expired"] else "ok"
        click.echo(f"{entry['key']:<30} {readable}  [{status}]")


@expiry_cmd.command("purge")
@click.option("--profile", default="default", show_default=True)
@click.option("--dry-run", is_flag=True, default=False)
def purge_cmd(profile: str, dry_run: bool) -> None:
    """Remove all expired variables from the vault."""
    password = prompt_password()
    path = get_vault_path(profile)
    variables = load_vault(path, password)
    updated, removed = purge_expired(variables)
    if not removed:
        click.echo("No expired variables found.")
        return
    if dry_run:
        click.echo(f"Would remove {len(removed)} expired variable(s): {', '.join(removed)}")
    else:
        save_vault(path, updated, password)
        click.echo(f"Removed {len(removed)} expired variable(s): {', '.join(removed)}")
