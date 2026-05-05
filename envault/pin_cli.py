"""CLI commands for pin management."""

import click
from envault.profiles import get_profile_vault_path, load_profile, save_profile
from envault.cli import prompt_password
from envault.pin import pin_variable, unpin_variable, get_pinned, is_pinned


@click.group("pin")
def pin_cmd():
    """Pin or unpin variables to prevent accidental modification."""


@pin_cmd.command("set")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def set_pin_cmd(key: str, profile: str):
    """Pin KEY so it cannot be overwritten or deleted."""
    password = prompt_password(confirm=False)
    vault_path = get_profile_vault_path(profile)
    variables = load_profile(vault_path, password)
    try:
        updated = pin_variable(variables, key)
    except KeyError as exc:
        raise click.ClickException(str(exc))
    save_profile(vault_path, updated, password)
    click.echo(f"Pinned '{key}' in profile '{profile}'.")


@pin_cmd.command("unpin")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def unpin_cmd(key: str, profile: str):
    """Remove the pin from KEY."""
    password = prompt_password(confirm=False)
    vault_path = get_profile_vault_path(profile)
    variables = load_profile(vault_path, password)
    updated = unpin_variable(variables, key)
    save_profile(vault_path, updated, password)
    click.echo(f"Unpinned '{key}' in profile '{profile}'.")


@pin_cmd.command("list")
@click.option("--profile", default="default", show_default=True)
def list_pins_cmd(profile: str):
    """List all pinned variables in a profile."""
    password = prompt_password(confirm=False)
    vault_path = get_profile_vault_path(profile)
    variables = load_profile(vault_path, password)
    pinned = get_pinned(variables)
    if not pinned:
        click.echo("No pinned variables.")
    else:
        for key in pinned:
            click.echo(f"  📌 {key}")


@pin_cmd.command("check")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def check_pin_cmd(key: str, profile: str):
    """Check whether KEY is pinned."""
    password = prompt_password(confirm=False)
    vault_path = get_profile_vault_path(profile)
    variables = load_profile(vault_path, password)
    if is_pinned(variables, key):
        click.echo(f"'{key}' is pinned.")
    else:
        click.echo(f"'{key}' is NOT pinned.")
