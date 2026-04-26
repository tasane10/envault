"""Command-line interface for envault.

Provides commands to manage encrypted environment variables:
  set   - Store a variable in the vault
  get   - Retrieve a variable from the vault
  list  - List all variable names in the vault
  remove - Delete a variable from the vault
"""

import sys
import click
from getpass import getpass

from envault.storage import (
    load_vault,
    save_vault,
    set_variable,
    get_variable,
    delete_variable,
    get_vault_path,
)


def prompt_password(confirm: bool = False) -> str:
    """Prompt the user for a master password.

    Args:
        confirm: If True, ask the user to confirm the password.

    Returns:
        The entered password string.
    """
    password = getpass("Master password: ")
    if confirm:
        confirmation = getpass("Confirm master password: ")
        if password != confirmation:
            click.echo("Error: Passwords do not match.", err=True)
            sys.exit(1)
    return password


@click.group()
@click.version_option(package_name="envault")
def cli():
    """envault — securely manage environment variables with encrypted local storage."""
    pass


@cli.command("set")
@click.argument("key")
@click.argument("value", required=False)
@click.option("--vault", default=None, help="Path to the vault file.")
def set_cmd(key: str, value: str | None, vault: str | None):
    """Store KEY=VALUE in the vault.

    If VALUE is omitted, it will be read from stdin interactively.
    """
    if value is None:
        value = click.prompt(f"Value for {key}", hide_input=True)

    vault_path = get_vault_path(vault)
    password = prompt_password(confirm=not vault_path.exists())

    data = load_vault(vault_path, password)
    set_variable(data, key, value)
    save_vault(vault_path, data, password)
    click.echo(f"✓ Set '{key}' in vault at {vault_path}")


@cli.command("get")
@click.argument("key")
@click.option("--vault", default=None, help="Path to the vault file.")
def get_cmd(key: str, vault: str | None):
    """Retrieve the value of KEY from the vault."""
    vault_path = get_vault_path(vault)

    if not vault_path.exists():
        click.echo(f"Error: No vault found at {vault_path}.", err=True)
        sys.exit(1)

    password = prompt_password()
    data = load_vault(vault_path, password)
    value = get_variable(data, key)

    if value is None:
        click.echo(f"Error: Key '{key}' not found in vault.", err=True)
        sys.exit(1)

    click.echo(value)


@cli.command("list")
@click.option("--vault", default=None, help="Path to the vault file.")
def list_cmd(vault: str | None):
    """List all variable names stored in the vault."""
    vault_path = get_vault_path(vault)

    if not vault_path.exists():
        click.echo(f"Error: No vault found at {vault_path}.", err=True)
        sys.exit(1)

    password = prompt_password()
    data = load_vault(vault_path, password)

    if not data:
        click.echo("Vault is empty.")
        return

    click.echo(f"Variables in vault ({vault_path}):")
    for key in sorted(data.keys()):
        click.echo(f"  {key}")


@cli.command("remove")
@click.argument("key")
@click.option("--vault", default=None, help="Path to the vault file.")
@click.confirmation_option(prompt="Are you sure you want to delete this variable?")
def remove_cmd(key: str, vault: str | None):
    """Remove KEY from the vault."""
    vault_path = get_vault_path(vault)

    if not vault_path.exists():
        click.echo(f"Error: No vault found at {vault_path}.", err=True)
        sys.exit(1)

    password = prompt_password()
    data = load_vault(vault_path, password)

    if get_variable(data, key) is None:
        click.echo(f"Error: Key '{key}' not found in vault.", err=True)
        sys.exit(1)

    delete_variable(data, key)
    save_vault(vault_path, data, password)
    click.echo(f"✓ Removed '{key}' from vault.")


if __name__ == "__main__":
    cli()
