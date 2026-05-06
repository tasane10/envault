"""CLI commands for managing variable-level access control lists."""

from __future__ import annotations

import click

from envault.acl import check_access, list_acl, remove_acl, set_acl
from envault.cli import prompt_password
from envault.storage import get_vault_path, load_vault, save_vault


@click.group("acl")
def acl_cmd():
    """Manage access control for vault variables."""


@acl_cmd.command("set")
@click.argument("key")
@click.option("--role", "-r", multiple=True, required=True, help="Role(s) to grant access (reader/writer/admin).")
@click.option("--profile", default="default", show_default=True)
def set_acl_cmd(key: str, role: tuple, profile: str):
    """Set ACL roles for a variable KEY."""
    password = prompt_password()
    vault_path = get_vault_path(profile)
    variables = load_vault(vault_path, password)
    try:
        updated = set_acl(variables, key, list(role))
    except (KeyError, ValueError) as exc:
        raise click.ClickException(str(exc))
    save_vault(vault_path, updated, password)
    click.echo(f"ACL set for '{key}': {', '.join(sorted(set(role)))}")


@acl_cmd.command("remove")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def remove_acl_cmd(key: str, profile: str):
    """Remove ACL restrictions from variable KEY."""
    password = prompt_password()
    vault_path = get_vault_path(profile)
    variables = load_vault(vault_path, password)
    updated = remove_acl(variables, key)
    save_vault(vault_path, updated, password)
    click.echo(f"ACL removed for '{key}'.")


@acl_cmd.command("list")
@click.option("--profile", default="default", show_default=True)
def list_acl_cmd(profile: str):
    """List all ACL entries in the vault."""
    password = prompt_password()
    vault_path = get_vault_path(profile)
    variables = load_vault(vault_path, password)
    entries = list_acl(variables)
    if not entries:
        click.echo("No ACL entries found.")
        return
    for entry in entries:
        click.echo(f"  {entry['key']}: {', '.join(entry['roles'])}")


@acl_cmd.command("check")
@click.argument("key")
@click.argument("role")
@click.option("--profile", default="default", show_default=True)
def check_acl_cmd(key: str, role: str, profile: str):
    """Check whether ROLE can access KEY."""
    password = prompt_password()
    vault_path = get_vault_path(profile)
    variables = load_vault(vault_path, password)
    allowed = check_access(variables, key, role)
    if allowed:
        click.echo(f"✓ Role '{role}' has access to '{key}'.")
    else:
        click.echo(f"✗ Role '{role}' does NOT have access to '{key}'.")
        raise SystemExit(1)
