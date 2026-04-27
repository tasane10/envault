"""CLI commands for snapshot management."""

import click
from envault.snapshot import create_snapshot, list_snapshots, restore_snapshot, delete_snapshot
from envault.cli import prompt_password


@click.group("snapshot")
def snapshot_cmd():
    """Manage vault snapshots."""


@snapshot_cmd.command("save")
@click.option("--profile", default="default", show_default=True, help="Profile name.")
@click.option("--label", default=None, help="Optional human-readable snapshot label.")
def save_cmd(profile: str, label: str):
    """Save the current vault state as a snapshot."""
    password = prompt_password(confirm=False)
    try:
        meta = create_snapshot(password, profile=profile, label=label)
        click.echo(f"Snapshot saved: {meta['id']} ({meta['key_count']} keys)")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@snapshot_cmd.command("list")
@click.option("--profile", default="default", show_default=True, help="Profile name.")
def list_cmd(profile: str):
    """List all snapshots for a profile."""
    snapshots = list_snapshots(profile=profile)
    if not snapshots:
        click.echo("No snapshots found.")
        return
    click.echo(f"{'ID':<30} {'Keys':>6}  Timestamp")
    click.echo("-" * 55)
    for s in snapshots:
        click.echo(f"{s['id']:<30} {s['key_count']:>6}  {s['timestamp']}")


@snapshot_cmd.command("restore")
@click.argument("snapshot_id")
@click.option("--profile", default="default", show_default=True, help="Profile name.")
def restore_cmd(snapshot_id: str, profile: str):
    """Restore vault from SNAPSHOT_ID."""
    password = prompt_password(confirm=False)
    try:
        variables = restore_snapshot(snapshot_id, password, profile=profile)
        click.echo(f"Restored {len(variables)} variable(s) from snapshot '{snapshot_id}'.")
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@snapshot_cmd.command("delete")
@click.argument("snapshot_id")
@click.option("--profile", default="default", show_default=True, help="Profile name.")
def delete_cmd(snapshot_id: str, profile: str):
    """Delete a snapshot by SNAPSHOT_ID."""
    deleted = delete_snapshot(snapshot_id, profile=profile)
    if deleted:
        click.echo(f"Snapshot '{snapshot_id}' deleted.")
    else:
        click.echo(f"Snapshot '{snapshot_id}' not found.", err=True)
        raise SystemExit(1)
