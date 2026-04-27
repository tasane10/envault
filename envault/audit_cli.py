"""CLI commands for interacting with the audit log."""

import click
from pathlib import Path
from typing import Optional

from envault.audit import read_events, clear_events, DEFAULT_AUDIT_DIR


@click.group("audit")
def audit_cmd():
    """View and manage the audit log."""


@audit_cmd.command("log")
@click.option("--profile", default="default", show_default=True, help="Profile name.")
@click.option("--limit", default=20, show_default=True, help="Max events to display.")
@click.option(
    "--audit-dir",
    default=None,
    type=click.Path(),
    hidden=True,
    help="Override audit directory (for testing).",
)
def log_cmd(profile: str, limit: int, audit_dir: Optional[str]):
    """Display recent audit log entries for a profile."""
    adir = Path(audit_dir) if audit_dir else DEFAULT_AUDIT_DIR
    events = read_events(profile, adir)
    if not events:
        click.echo(f"No audit events found for profile '{profile}'.")
        return
    recent = events[-limit:]
    click.echo(f"Audit log for profile '{profile}' (showing {len(recent)} of {len(events)}):\n")
    for ev in recent:
        click.echo(
            f"  [{ev['timestamp']}] {ev['action'].upper():8s}  key={ev['key']}  actor={ev['actor']}"
        )


@audit_cmd.command("clear")
@click.option("--profile", default="default", show_default=True, help="Profile name.")
@click.option(
    "--audit-dir",
    default=None,
    type=click.Path(),
    hidden=True,
    help="Override audit directory (for testing).",
)
@click.confirmation_option(prompt="Are you sure you want to clear the audit log?")
def clear_cmd(profile: str, audit_dir: Optional[str]):
    """Clear the audit log for a profile."""
    adir = Path(audit_dir) if audit_dir else DEFAULT_AUDIT_DIR
    count = clear_events(profile, adir)
    click.echo(f"Cleared {count} audit event(s) for profile '{profile}'.")
