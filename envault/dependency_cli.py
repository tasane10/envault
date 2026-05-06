"""CLI commands for variable dependency management."""

from __future__ import annotations

import click

from envault.dependency import (
    get_dependencies,
    remove_dependency,
    resolve_order,
    set_dependency,
)
from envault.profiles import load_profile, save_profile
from envault.cli import prompt_password


@click.group("dependency")
def dependency_cmd() -> None:
    """Manage variable dependencies."""


@dependency_cmd.command("set")
@click.argument("key")
@click.argument("depends_on", nargs=-1, required=True)
@click.option("--profile", default="default", show_default=True)
def set_dep_cmd(key: str, depends_on: tuple, profile: str) -> None:
    """Declare that KEY depends on DEPENDS_ON variables."""
    password = prompt_password()
    try:
        variables = load_profile(profile, password)
        variables = set_dependency(variables, key, list(depends_on))
        save_profile(profile, variables, password)
        click.echo(f"Dependency set: {key} -> {', '.join(sorted(depends_on))}")
    except (KeyError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc


@dependency_cmd.command("remove")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def remove_dep_cmd(key: str, profile: str) -> None:
    """Remove dependency declarations for KEY."""
    password = prompt_password()
    variables = load_profile(profile, password)
    variables = remove_dependency(variables, key)
    save_profile(profile, variables, password)
    click.echo(f"Dependencies removed for '{key}'.")


@dependency_cmd.command("list")
@click.option("--profile", default="default", show_default=True)
def list_deps_cmd(profile: str) -> None:
    """List all declared dependencies."""
    password = prompt_password()
    variables = load_profile(profile, password)
    deps = get_dependencies(variables)
    if not deps:
        click.echo("No dependencies declared.")
        return
    for key, dep_list in sorted(deps.items()):
        click.echo(f"  {key} -> {', '.join(dep_list)}")


@dependency_cmd.command("order")
@click.option("--profile", default="default", show_default=True)
def order_cmd(profile: str) -> None:
    """Show variables in dependency-safe resolution order."""
    password = prompt_password()
    try:
        variables = load_profile(profile, password)
        order = resolve_order(variables)
        for idx, key in enumerate(order, 1):
            click.echo(f"  {idx:>3}. {key}")
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
