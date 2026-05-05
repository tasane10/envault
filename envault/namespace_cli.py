"""CLI commands for namespace management."""

import click

from envault.cli import prompt_password
from envault.namespace import (
    filter_by_namespace,
    list_namespaces,
    move_namespace,
    strip_namespace,
)
from envault.profiles import load_profile, save_profile


@click.group("namespace")
def namespace_cmd():
    """Manage variable namespaces (key prefixes)."""


@namespace_cmd.command("list")
@click.option("--profile", default="default", show_default=True)
def list_cmd(profile: str):
    """List all namespaces present in the vault."""
    password = prompt_password()
    variables = load_profile(profile, password)
    namespaces = list_namespaces(variables)
    if not namespaces:
        click.echo("No namespaces found.")
        return
    for ns in namespaces:
        click.echo(ns)


@namespace_cmd.command("filter")
@click.argument("namespace")
@click.option("--profile", default="default", show_default=True)
@click.option("--strip", is_flag=True, help="Strip namespace prefix from output keys.")
def filter_cmd(namespace: str, profile: str, strip: bool):
    """List variables belonging to a namespace."""
    password = prompt_password()
    variables = load_profile(profile, password)
    filtered = filter_by_namespace(variables, namespace)
    if strip:
        filtered = strip_namespace(filtered, namespace)
    if not filtered:
        click.echo(f"No variables found in namespace '{namespace}'.")
        return
    for key, value in sorted(filtered.items()):
        click.echo(f"{key}={value}")


@namespace_cmd.command("move")
@click.argument("src")
@click.argument("dst")
@click.option("--profile", default="default", show_default=True)
def move_cmd(src: str, dst: str, profile: str):
    """Rename all variables from SRC namespace to DST namespace."""
    password = prompt_password()
    variables = load_profile(profile, password)
    updated, count = move_namespace(variables, src, dst)
    if count == 0:
        click.echo(f"No variables found in namespace '{src}'.")
        return
    save_profile(profile, updated, password)
    click.echo(f"Moved {count} variable(s) from '{src}' to '{dst}'.")
