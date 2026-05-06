"""CLI commands for alias management."""

from __future__ import annotations

import click

from envault.alias import list_aliases, remove_alias, set_alias
from envault.cli import prompt_password
from envault.profiles import get_profile_vault_path, load_profile, save_profile


@click.group("alias")
def alias_cmd():
    """Manage variable aliases."""


@alias_cmd.command("set")
@click.argument("alias")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def set_alias_cmd(alias: str, key: str, profile: str):
    """Create or update ALIAS pointing to KEY."""
    password = prompt_password(confirm=False)
    vault_path = get_profile_vault_path(profile)
    variables = load_profile(vault_path, password)
    try:
        variables = set_alias(variables, alias, key)
    except (KeyError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
    save_profile(vault_path, variables, password)
    click.echo(f"Alias '{alias}' -> '{key}' saved in profile '{profile}'.")


@alias_cmd.command("remove")
@click.argument("alias")
@click.option("--profile", default="default", show_default=True)
def remove_alias_cmd(alias: str, profile: str):
    """Remove ALIAS from the vault."""
    password = prompt_password(confirm=False)
    vault_path = get_profile_vault_path(profile)
    variables = load_profile(vault_path, password)
    try:
        variables = remove_alias(variables, alias)
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc
    save_profile(vault_path, variables, password)
    click.echo(f"Alias '{alias}' removed from profile '{profile}'.")


@alias_cmd.command("list")
@click.option("--profile", default="default", show_default=True)
@click.option("--verbose", "-v", is_flag=True, default=False, help="Show the resolved value for each alias.")
def list_aliases_cmd(profile: str, verbose: bool):
    """List all aliases in the vault."""
    password = prompt_password(confirm=False)
    vault_path = get_profile_vault_path(profile)
    variables = load_profile(vault_path, password)
    pairs = list_aliases(variables)
    if not pairs:
        click.echo("No aliases defined.")
        return
    for alias, key in pairs:
        if verbose:
            resolved = variables.get(key, {}).get("value", "<unresolved>")
            click.echo(f"  {alias} -> {key} (value: {resolved})")
        else:
            click.echo(f"  {alias} -> {key}")
