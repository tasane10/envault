"""CLI commands for managing variable priorities."""

from __future__ import annotations

import click

from envault.cli import prompt_password
from envault.priority import (
    get_priority,
    list_priorities,
    remove_priority,
    set_priority,
    sort_by_priority,
)
from envault.storage import get_variable, load_vault, save_vault


@click.group("priority")
def priority_cmd() -> None:
    """Manage variable priority levels."""


@priority_cmd.command("set")
@click.argument("key")
@click.argument("level", type=int)
@click.option("--profile", default="default", show_default=True)
def set_priority_cmd(key: str, level: int, profile: str) -> None:
    """Assign a numeric LEVEL to KEY (higher = more important)."""
    password = prompt_password()
    variables = load_vault(password, profile=profile)
    try:
        updated = set_priority(variables, key, level)
    except (KeyError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
    save_vault(updated, password, profile=profile)
    click.echo(f"Priority for '{key}' set to {level}.")


@priority_cmd.command("remove")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def remove_priority_cmd(key: str, profile: str) -> None:
    """Remove the priority assignment from KEY."""
    password = prompt_password()
    variables = load_vault(password, profile=profile)
    updated = remove_priority(variables, key)
    save_vault(updated, password, profile=profile)
    click.echo(f"Priority removed from '{key}'.")


@priority_cmd.command("show")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def show_priority_cmd(key: str, profile: str) -> None:
    """Show the priority level assigned to KEY."""
    password = prompt_password()
    variables = load_vault(password, profile=profile)
    level = get_priority(variables, key)
    if level is None:
        click.echo(f"No priority set for '{key}'.")
    else:
        click.echo(f"{key}: {level}")


@priority_cmd.command("list")
@click.option("--profile", default="default", show_default=True)
@click.option("--sorted", "sorted_", is_flag=True, default=False, help="Sort by priority.")
def list_priorities_cmd(profile: str, sorted_: bool) -> None:
    """List all variables with assigned priorities."""
    password = prompt_password()
    variables = load_vault(password, profile=profile)
    if sorted_:
        keys = sort_by_priority(variables)
        priorities = list_priorities(variables)
        rows = [(k, priorities.get(k, "")) for k in keys if k in priorities]
    else:
        rows = sorted(list_priorities(variables).items())
    if not rows:
        click.echo("No priorities set.")
        return
    for key, level in rows:
        click.echo(f"{key}: {level}")
