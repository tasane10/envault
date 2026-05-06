"""CLI commands for variable group management."""
import click
from envault.group import set_group, remove_from_group, filter_by_group, list_groups
from envault.profiles import get_profile_vault_path, load_profile, save_profile
from envault.cli import prompt_password


@click.group("group")
def group_cmd():
    """Manage variable groups."""


@group_cmd.command("set")
@click.argument("key")
@click.argument("group")
@click.option("--profile", default="default", show_default=True)
def set_group_cmd(key: str, group: str, profile: str):
    """Assign KEY to GROUP."""
    password = prompt_password()
    path = get_profile_vault_path(profile)
    variables = load_profile(path, password)
    try:
        variables = set_group(variables, key, group)
    except KeyError as exc:
        raise click.ClickException(str(exc))
    save_profile(path, variables, password)
    click.echo(f"Key '{key}' assigned to group '{group}'.")


@group_cmd.command("remove")
@click.argument("key")
@click.argument("group")
@click.option("--profile", default="default", show_default=True)
def remove_group_cmd(key: str, group: str, profile: str):
    """Remove KEY from GROUP."""
    password = prompt_password()
    path = get_profile_vault_path(profile)
    variables = load_profile(path, password)
    variables = remove_from_group(variables, key, group)
    save_profile(path, variables, password)
    click.echo(f"Key '{key}' removed from group '{group}'.")


@group_cmd.command("list")
@click.option("--profile", default="default", show_default=True)
def list_groups_cmd(profile: str):
    """List all groups and their members."""
    password = prompt_password()
    path = get_profile_vault_path(profile)
    variables = load_profile(path, password)
    names = list_groups(variables)
    if not names:
        click.echo("No groups defined.")
        return
    from envault.group import get_groups
    groups = get_groups(variables)
    for name in names:
        members = ", ".join(groups[name])
        click.echo(f"{name}: {members}")


@group_cmd.command("filter")
@click.argument("group")
@click.option("--profile", default="default", show_default=True)
def filter_group_cmd(group: str, profile: str):
    """Show variables belonging to GROUP."""
    password = prompt_password()
    path = get_profile_vault_path(profile)
    variables = load_profile(path, password)
    subset = filter_by_group(variables, group)
    if not subset:
        click.echo(f"No variables found in group '{group}'.")
        return
    for key, value in sorted(subset.items()):
        click.echo(f"{key}={value}")
