"""CLI commands for managing and running envault workflows."""
from __future__ import annotations

import json

import click

from envault.workflow import (
    delete_workflow,
    list_workflows,
    load_workflow,
    run_workflow,
    save_workflow,
)


@click.group(name="workflow")
def workflow_cmd() -> None:
    """Manage named workflow sequences."""


@workflow_cmd.command(name="create")
@click.argument("name")
@click.argument("steps_json")
def create_cmd(name: str, steps_json: str) -> None:
    """Create a workflow from a JSON steps array.

    STEPS_JSON example: '[{"action":"set","key":"FOO","value":"bar"}]'
    """
    try:
        steps = json.loads(steps_json)
    except json.JSONDecodeError as exc:
        raise click.ClickException(f"Invalid JSON: {exc}") from exc
    try:
        path = save_workflow(name, steps)
        click.echo(f"Workflow '{name}' saved to {path}")
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


@workflow_cmd.command(name="list")
def list_cmd() -> None:
    """List available workflows."""
    names = list_workflows()
    if not names:
        click.echo("No workflows defined.")
    else:
        for n in names:
            click.echo(n)


@workflow_cmd.command(name="show")
@click.argument("name")
def show_cmd(name: str) -> None:
    """Show steps of a workflow."""
    try:
        wf = load_workflow(name)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(wf, indent=2))


@workflow_cmd.command(name="delete")
@click.argument("name")
def delete_cmd(name: str) -> None:
    """Delete a workflow."""
    removed = delete_workflow(name)
    if removed:
        click.echo(f"Workflow '{name}' deleted.")
    else:
        raise click.ClickException(f"Workflow '{name}' not found.")


@workflow_cmd.command(name="run")
@click.argument("name")
@click.option("--vars", "vars_json", default="{}", help="Initial variables as JSON object.")
def run_cmd(name: str, vars_json: str) -> None:
    """Run a workflow against a variables dict (dry-run, prints log)."""
    try:
        variables = json.loads(vars_json)
    except json.JSONDecodeError as exc:
        raise click.ClickException(f"Invalid JSON for --vars: {exc}") from exc
    try:
        log = run_workflow(name, variables)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    for entry in log:
        click.echo(f"  [{entry['status'].upper()}] {entry['action']} {entry.get('key', '')}")
    click.echo(f"Result variables: {json.dumps(variables)}")
