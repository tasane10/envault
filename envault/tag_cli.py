"""CLI commands for tagging environment variables."""

import click
from envault.tag import (
    get_tags,
    set_tags,
    remove_tags,
    filter_by_tag,
    TAGS_META_KEY,
)
from envault.profiles import load_profile, save_profile
from envault.cli import prompt_password


@click.group("tag")
def tag_cmd() -> None:
    """Manage tags on environment variables."""


@tag_cmd.command("set")
@click.argument("var_name")
@click.argument("tags", nargs=-1, required=True)
@click.option("--profile", default="default", show_default=True)
def set_tag_cmd(var_name: str, tags: tuple, profile: str) -> None:
    """Assign TAGS to VAR_NAME (replaces existing tags)."""
    password = prompt_password()
    variables = load_profile(profile, password)
    if var_name not in variables:
        raise click.ClickException(f"Variable '{var_name}' not found.")
    updated = set_tags(variables, var_name, list(tags))
    save_profile(profile, updated, password)
    final = get_tags(updated, var_name)
    click.echo(f"Tags for '{var_name}': {', '.join(final)}")


@tag_cmd.command("remove")
@click.argument("var_name")
@click.argument("tags", nargs=-1)
@click.option("--all", "remove_all", is_flag=True, default=False)
@click.option("--profile", default="default", show_default=True)
def remove_tag_cmd(var_name: str, tags: tuple, remove_all: bool, profile: str) -> None:
    """Remove specific TAGS (or --all) from VAR_NAME."""
    password = prompt_password()
    variables = load_profile(profile, password)
    updated = remove_tags(variables, var_name, None if remove_all else list(tags))
    save_profile(profile, updated, password)
    click.echo(f"Tags updated for '{var_name}'.")


@tag_cmd.command("list")
@click.argument("var_name")
@click.option("--profile", default="default", show_default=True)
def list_tags_cmd(var_name: str, profile: str) -> None:
    """List all tags on VAR_NAME."""
    password = prompt_password()
    variables = load_profile(profile, password)
    tags = get_tags(variables, var_name)
    if tags:
        click.echo("  ".join(tags))
    else:
        click.echo(f"No tags set for '{var_name}'.")


@tag_cmd.command("filter")
@click.argument("tag")
@click.option("--profile", default="default", show_default=True)
def filter_tag_cmd(tag: str, profile: str) -> None:
    """List all variables that carry TAG."""
    password = prompt_password()
    variables = load_profile(profile, password)
    matches = filter_by_tag(variables, tag)
    if not matches:
        click.echo(f"No variables tagged '{tag}'.")
        return
    for key in sorted(matches):
        click.echo(key)
