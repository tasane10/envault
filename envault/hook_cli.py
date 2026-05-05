"""CLI commands for managing envault hooks."""

from __future__ import annotations

import sys

import click

from envault.hook import (
    HOOK_EVENTS,
    get_hook_path,
    install_hook,
    list_hooks,
    remove_hook,
    run_hook,
)


@click.group(name="hook")
def hook_cmd() -> None:
    """Manage lifecycle hooks for vault events."""


@hook_cmd.command(name="install")
@click.argument("event")
@click.argument("script_file", type=click.Path(exists=True, readable=True))
@click.option("--profile", default="default", show_default=True, help="Vault profile.")
def install_cmd(event: str, script_file: str, profile: str) -> None:
    """Install a hook script for EVENT from SCRIPT_FILE."""
    try:
        with open(script_file) as fh:
            script = fh.read()
        path = install_hook(event, script, profile=profile)
        click.echo(f"Hook '{event}' installed at {path}")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@hook_cmd.command(name="remove")
@click.argument("event")
@click.option("--profile", default="default", show_default=True, help="Vault profile.")
def remove_cmd(event: str, profile: str) -> None:
    """Remove the hook for EVENT."""
    removed = remove_hook(event, profile=profile)
    if removed:
        click.echo(f"Hook '{event}' removed.")
    else:
        click.echo(f"No hook found for event '{event}'.", err=True)
        sys.exit(1)


@hook_cmd.command(name="list")
@click.option("--profile", default="default", show_default=True, help="Vault profile.")
def list_cmd(profile: str) -> None:
    """List installed hooks."""
    hooks = list_hooks(profile=profile)
    if not hooks:
        click.echo("No hooks installed.")
        return
    click.echo(f"Installed hooks for profile '{profile}':")
    for event in hooks:
        path = get_hook_path(event, profile)
        click.echo(f"  {event:20s}  {path}")


@hook_cmd.command(name="show-events")
def show_events_cmd() -> None:
    """Show all supported hook events."""
    click.echo("Supported hook events:")
    for event in HOOK_EVENTS:
        click.echo(f"  {event}")


@hook_cmd.command(name="run")
@click.argument("event")
@click.option("--profile", default="default", show_default=True, help="Vault profile.")
def run_cmd(event: str, profile: str) -> None:
    """Manually run the hook for EVENT."""
    code = run_hook(event, profile=profile)
    if code is None:
        click.echo(f"No hook installed for event '{event}'.")
    elif code == 0:
        click.echo(f"Hook '{event}' completed successfully.")
    else:
        click.echo(f"Hook '{event}' exited with code {code}.", err=True)
        sys.exit(code)
