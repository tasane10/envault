"""CLI commands for key rotation."""

import click
from envault.rotate import rotate_key, rotate_key_all_profiles
from envault.cli import prompt_password


@click.group("rotate")
def rotate_cmd():
    """Rotate encryption keys for one or all profiles."""


@rotate_cmd.command("key")
@click.option("--profile", default="default", show_default=True, help="Profile to rotate.")
@click.option("--all-profiles", "all_profiles", is_flag=True, default=False, help="Rotate all profiles.")
def rotate_key_cmd(profile: str, all_profiles: bool):
    """Re-encrypt vault(s) with a new master password."""
    old_password = prompt_password("Current master password")
    new_password = prompt_password("New master password")
    confirm = click.prompt("Confirm new master password", hide_input=True)

    if new_password != confirm:
        click.echo("Error: new passwords do not match.", err=True)
        raise SystemExit(1)

    if old_password == new_password:
        click.echo("Error: new password must differ from the current password.", err=True)
        raise SystemExit(1)

    try:
        if all_profiles:
            results = rotate_key_all_profiles(old_password, new_password)
            for r in results:
                click.echo(f"Rotated profile '{r['profile']}' ({r['rotated']} variable(s)).")
        else:
            result = rotate_key(old_password, new_password, profile=profile)
            click.echo(
                f"Key rotated for profile '{result['profile']}' "
                f"({result['rotated']} variable(s))."
            )
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
