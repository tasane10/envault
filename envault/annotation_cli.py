"""CLI commands for managing variable annotations (descriptions/notes)."""

from __future__ import annotations

import click

from envault.annotation import (
    filter_annotated,
    get_annotation,
    remove_annotation,
    set_annotation,
)
from envault.cli import prompt_password
from envault.profiles import get_profile_vault_path, load_profile, save_profile


@click.group("annotation")
def annotation_cmd():
    """Manage variable annotations (descriptions / notes)."""


@annotation_cmd.command("set")
@click.argument("key")
@click.argument("description")
@click.option("--profile", default="default", show_default=True)
def set_annotation_cmd(key: str, description: str, profile: str):
    """Attach a DESCRIPTION to KEY."""
    password = prompt_password()
    vault_path = get_profile_vault_path(profile)
    variables = load_profile(vault_path, password)
    try:
        updated = set_annotation(variables, key, description)
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc
    save_profile(vault_path, updated, password)
    click.echo(f"Annotated '{key}'.")


@annotation_cmd.command("remove")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def remove_annotation_cmd(key: str, profile: str):
    """Remove the annotation from KEY."""
    password = prompt_password()
    vault_path = get_profile_vault_path(profile)
    variables = load_profile(vault_path, password)
    updated = remove_annotation(variables, key)
    save_profile(vault_path, updated, password)
    click.echo(f"Annotation removed from '{key}'.")


@annotation_cmd.command("show")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def show_annotation_cmd(key: str, profile: str):
    """Show the annotation for KEY."""
    password = prompt_password()
    vault_path = get_profile_vault_path(profile)
    variables = load_profile(vault_path, password)
    note = get_annotation(variables, key)
    if note is None:
        click.echo(f"No annotation for '{key}'.")
    else:
        click.echo(note)


@annotation_cmd.command("list")
@click.option("--profile", default="default", show_default=True)
def list_annotations_cmd(profile: str):
    """List all annotated variables."""
    password = prompt_password()
    vault_path = get_profile_vault_path(profile)
    variables = load_profile(vault_path, password)
    annotated = filter_annotated(variables)
    if not annotated:
        click.echo("No annotations found.")
        return
    for key, desc in sorted(annotated.items()):
        click.echo(f"{key}: {desc}")
