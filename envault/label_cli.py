"""CLI commands for managing variable labels."""
from __future__ import annotations

import click

from envault.cli import prompt_password
from envault.label import filter_by_label, get_labels, list_labels, remove_labels, set_labels
from envault.profiles import get_profile_vault_path, load_profile, save_profile


@click.group("label")
def label_cmd() -> None:
    """Manage labels attached to variables."""


@label_cmd.command("set")
@click.argument("key")
@click.argument("labels", nargs=-1, required=True)
@click.option("--profile", default="default", show_default=True)
def set_label_cmd(key: str, labels: tuple[str, ...], profile: str) -> None:
    """Attach one or more LABELS to KEY."""
    password = prompt_password()
    vault_path = get_profile_vault_path(profile)
    variables = load_profile(vault_path, password)
    try:
        variables = set_labels(variables, key, list(labels))
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc
    save_profile(vault_path, variables, password)
    click.echo(f"Labels set on '{key}': {', '.join(sorted(set(labels)))}")


@label_cmd.command("remove")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def remove_label_cmd(key: str, profile: str) -> None:
    """Remove all labels from KEY."""
    password = prompt_password()
    vault_path = get_profile_vault_path(profile)
    variables = load_profile(vault_path, password)
    try:
        variables = remove_labels(variables, key)
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc
    save_profile(vault_path, variables, password)
    click.echo(f"Labels removed from '{key}'.")


@label_cmd.command("list")
@click.option("--profile", default="default", show_default=True)
def list_labels_cmd(profile: str) -> None:
    """List all labels in use across the profile."""
    password = prompt_password()
    vault_path = get_profile_vault_path(profile)
    variables = load_profile(vault_path, password)
    labels = list_labels(variables)
    if not labels:
        click.echo("No labels defined.")
    else:
        for label in labels:
            click.echo(label)


@label_cmd.command("filter")
@click.argument("label")
@click.option("--profile", default="default", show_default=True)
def filter_label_cmd(label: str, profile: str) -> None:
    """Show variables that have LABEL attached."""
    password = prompt_password()
    vault_path = get_profile_vault_path(profile)
    variables = load_profile(vault_path, password)
    matching = filter_by_label(variables, label)
    if not matching:
        click.echo(f"No variables with label '{label}'.")
    else:
        for key in sorted(matching):
            click.echo(key)
