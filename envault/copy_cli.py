import click
from envault.profiles import list_profiles, load_profile, save_profile, copy_profile
from envault.cli import prompt_password


@click.group("copy")
def copy_cmd():
    """Commands for copying variables between profiles."""
    pass


@copy_cmd.command("profile")
@click.argument("source_profile")
@click.argument("dest_profile")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys in destination.")
def copy_profile_cmd(source_profile, dest_profile, overwrite):
    """Copy all variables from SOURCE_PROFILE to DEST_PROFILE."""
    src_password = prompt_password(f"Password for source profile '{source_profile}': ")
    dest_password = prompt_password(f"Password for destination profile '{dest_profile}': ")

    try:
        copied, skipped = copy_profile(
            source_profile, src_password,
            dest_profile, dest_password,
            overwrite=overwrite
        )
        click.echo(f"Copied {copied} variable(s) to '{dest_profile}'.")
        if skipped:
            click.echo(f"Skipped {skipped} existing key(s) (use --overwrite to replace).")
    except ValueError as e:
        raise click.ClickException(str(e))


@copy_cmd.command("var")
@click.argument("key")
@click.argument("source_profile")
@click.argument("dest_profile")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite if key exists in destination.")
def copy_var_cmd(key, source_profile, dest_profile, overwrite):
    """Copy a single KEY from SOURCE_PROFILE to DEST_PROFILE."""
    src_password = prompt_password(f"Password for source profile '{source_profile}': ")
    dest_password = prompt_password(f"Password for destination profile '{dest_profile}': ")

    try:
        src_vars = load_profile(source_profile, src_password)
    except ValueError as e:
        raise click.ClickException(f"Could not load source profile: {e}")

    if key not in src_vars:
        raise click.ClickException(f"Key '{key}' not found in profile '{source_profile}'.")

    try:
        dest_vars = load_profile(dest_profile, dest_password)
    except FileNotFoundError:
        dest_vars = {}
    except ValueError as e:
        raise click.ClickException(f"Could not load destination profile: {e}")

    if key in dest_vars and not overwrite:
        raise click.ClickException(
            f"Key '{key}' already exists in '{dest_profile}'. Use --overwrite to replace."
        )

    dest_vars[key] = src_vars[key]
    save_profile(dest_profile, dest_vars, dest_password)
    click.echo(f"Copied '{key}' from '{source_profile}' to '{dest_profile}'.")
