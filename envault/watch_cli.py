"""CLI commands for the vault watch feature."""

import sys
import click

from envault.profiles import load_profile
from envault.watch import get_changed_keys, watch_profile
from envault.cli import prompt_password


@click.group("watch")
def watch_cmd():
    """Watch a vault profile for live changes."""


@watch_cmd.command("start")
@click.option("--profile", default="default", show_default=True, help="Profile to watch.")
@click.option("--interval", default=2.0, show_default=True, type=float, help="Poll interval in seconds.")
def start_cmd(profile: str, interval: float):
    """Start watching a profile and print a diff whenever it changes."""
    password = prompt_password(confirm=False)

    try:
        current_vars = load_profile(profile, password)
    except Exception as exc:
        click.echo(f"Error loading profile '{profile}': {exc}", err=True)
        sys.exit(1)

    click.echo(f"Watching profile '{profile}' every {interval}s — press Ctrl+C to stop.")

    def on_change(prof: str, new_vars: dict):
        nonlocal current_vars
        diff = get_changed_keys(current_vars, new_vars)
        if diff["added"]:
            click.echo(f"  [+] Added:   {', '.join(diff['added'])}")
        if diff["removed"]:
            click.echo(f"  [-] Removed: {', '.join(diff['removed'])}")
        if diff["changed"]:
            click.echo(f"  [~] Changed: {', '.join(diff['changed'])}")
        current_vars = new_vars

    try:
        watch_profile(profile, password, interval=interval, on_change=on_change)
    except KeyboardInterrupt:
        click.echo("\nStopped watching.")


@watch_cmd.command("diff")
@click.option("--profile", default="default", show_default=True, help="Profile to inspect.")
@click.option("--snapshot", required=True, help="Snapshot name to compare against.")
def diff_cmd(profile: str, snapshot: str):
    """Show the diff between the current vault and a saved snapshot."""
    from envault.snapshot import restore_snapshot, list_snapshots
    from envault.diff import diff_variables, format_diff

    password = prompt_password(confirm=False)

    snapshots = list_snapshots(profile)
    if snapshot not in snapshots:
        click.echo(f"Snapshot '{snapshot}' not found for profile '{profile}'.", err=True)
        sys.exit(1)

    try:
        current = load_profile(profile, password)
        snap_vars = restore_snapshot(profile, snapshot, password, dry_run=True)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    results = diff_variables(snap_vars, current)
    if not results:
        click.echo("No differences found.")
    else:
        click.echo(format_diff(results))
