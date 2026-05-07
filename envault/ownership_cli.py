"""CLI commands for variable ownership management."""

from __future__ import annotations

import click

from envault.ownership import (
    filter_by_owner,
    get_owner,
    list_owners,
    remove_owner,
    set_owner,
)
from envault.cli import prompt_password
from envault.storage import get_vault_path, load_vault, save_vault


@click.group("ownership")
def ownership_cmd() -> None:
    """Manage variable ownership."""


@ownership_cmd.command("set")
@click.argument("key")
@click.argument("owner")
@click.option("--profile", default="default", show_default=True)
def set_owner_cmd(key: str, owner: str, profile: str) -> None:
    """Assign OWNER to KEY."""
    password = prompt_password()
    path = get_vault_path(profile)
    variables = load_vault(path, password)
    try:
        updated = set_owner(variables, key, owner)
    except (KeyError, ValueError) as exc:
        raise click.ClickException(str(exc))
    save_vault(path, updated, password)
    click.echo(f"Owner of '{key}' set to '{owner}'.")


@ownership_cmd.command("remove")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def remove_owner_cmd(key: str, profile: str) -> None:
    """Remove ownership from KEY."""
    password = prompt_password()
    path = get_vault_path(profile)
    variables = load_vault(path, password)
    updated = remove_owner(variables, key)
    save_vault(path, updated, password)
    click.echo(f"Ownership removed from '{key}'.")


@ownership_cmd.command("show")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def show_owner_cmd(key: str, profile: str) -> None:
    """Show the owner of KEY."""
    password = prompt_password()
    path = get_vault_path(profile)
    variables = load_vault(path, password)
    owner = get_owner(variables, key)
    if owner:
        click.echo(f"{key}: {owner}")
    else:
        click.echo(f"'{key}' has no owner.")


@ownership_cmd.command("list")
@click.option("--profile", default="default", show_default=True)
@click.option("--owner", default=None, help="Filter by owner name.")
def list_owners_cmd(profile: str, owner: str | None) -> None:
    """List all variable owners."""
    password = prompt_password()
    path = get_vault_path(profile)
    variables = load_vault(path, password)
    if owner:
        keys = filter_by_owner(variables, owner)
        if keys:
            for k in keys:
                click.echo(f"  {k}")
        else:
            click.echo(f"No variables owned by '{owner}'.")
    else:
        owners = list_owners(variables)
        if owners:
            for k, v in owners.items():
                click.echo(f"  {k}: {v}")
        else:
            click.echo("No ownership records found.")
