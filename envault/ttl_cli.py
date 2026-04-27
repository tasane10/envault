"""CLI commands for managing variable TTLs."""

import click
from datetime import datetime, timezone

from envault.profiles import get_profile_vault_path, load_profile, save_profile
from envault.ttl import set_ttl, get_ttl, remove_ttl, purge_expired
from envault.cli import prompt_password


@click.group(name="ttl")
def ttl_cmd():
    """Manage variable expiry (TTL)."""


@ttl_cmd.command(name="set")
@click.argument("key")
@click.argument("seconds", type=int)
@click.option("--profile", default="default", show_default=True)
def set_ttl_cmd(key: str, seconds: int, profile: str):
    """Set a TTL in SECONDS on KEY."""
    password = prompt_password(confirm=False)
    vault_path = get_profile_vault_path(profile)
    variables = load_profile(vault_path, password)
    if key not in variables:
        raise click.ClickException(f"Variable '{key}' not found.")
    variables = set_ttl(variables, key, seconds)
    save_profile(vault_path, variables, password)
    expiry = get_ttl(variables, key)
    dt = datetime.fromtimestamp(expiry, tz=timezone.utc).isoformat()
    click.echo(f"TTL set for '{key}': expires at {dt}")


@ttl_cmd.command(name="show")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def show_ttl_cmd(key: str, profile: str):
    """Show the TTL for KEY."""
    password = prompt_password(confirm=False)
    vault_path = get_profile_vault_path(profile)
    variables = load_profile(vault_path, password)
    expiry = get_ttl(variables, key)
    if expiry is None:
        click.echo(f"No TTL set for '{key}'.")
    else:
        dt = datetime.fromtimestamp(expiry, tz=timezone.utc).isoformat()
        now = datetime.now(timezone.utc).timestamp()
        remaining = max(0.0, expiry - now)
        click.echo(f"'{key}' expires at {dt} ({remaining:.0f}s remaining)")


@ttl_cmd.command(name="remove")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def remove_ttl_cmd(key: str, profile: str):
    """Remove the TTL from KEY."""
    password = prompt_password(confirm=False)
    vault_path = get_profile_vault_path(profile)
    variables = load_profile(vault_path, password)
    variables = remove_ttl(variables, key)
    save_profile(vault_path, variables, password)
    click.echo(f"TTL removed from '{key}'.")


@ttl_cmd.command(name="purge")
@click.option("--profile", default="default", show_default=True)
def purge_cmd(profile: str):
    """Delete all variables that have expired."""
    password = prompt_password(confirm=False)
    vault_path = get_profile_vault_path(profile)
    variables = load_profile(vault_path, password)
    updated, removed = purge_expired(variables)
    if not removed:
        click.echo("No expired variables found.")
        return
    save_profile(vault_path, updated, password)
    for k in removed:
        click.echo(f"Removed expired variable: {k}")
    click.echo(f"Purged {len(removed)} variable(s).")
