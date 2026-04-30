import click
from envault.remote import push_variables, pull_variables, RemoteError
from envault.profiles import load_profile, save_profile
from envault.cli import prompt_password


@click.group(name="remote")
def remote_cmd():
    """Push and pull variables to/from a remote envault server."""


@remote_cmd.command(name="push")
@click.option("--profile", default="default", show_default=True, help="Profile to push.")
@click.option("--url", required=True, envvar="ENVAULT_REMOTE_URL", help="Remote server URL.")
@click.option("--token", required=True, envvar="ENVAULT_REMOTE_TOKEN", help="Auth token.")
@click.option("--keys", default=None, help="Comma-separated list of keys to push (default: all).")
def push_cmd(profile, url, token, keys):
    """Push local vault variables to a remote server."""
    password = prompt_password(confirm=False)
    try:
        variables = load_profile(profile, password)
    except Exception as exc:
        raise click.ClickException(f"Failed to load profile '{profile}': {exc}")

    whitelist = [k.strip() for k in keys.split(",")] if keys else None

    try:
        result = push_variables(url, token, profile, variables, keys=whitelist)
    except RemoteError as exc:
        raise click.ClickException(str(exc))

    pushed = result.get("pushed", 0)
    skipped = result.get("skipped", 0)
    click.echo(f"Pushed {pushed} variable(s) to '{url}' (profile: {profile}).")
    if skipped:
        click.echo(f"Skipped {skipped} metadata key(s).")


@remote_cmd.command(name="pull")
@click.option("--profile", default="default", show_default=True, help="Profile to pull into.")
@click.option("--url", required=True, envvar="ENVAULT_REMOTE_URL", help="Remote server URL.")
@click.option("--token", required=True, envvar="ENVAULT_REMOTE_TOKEN", help="Auth token.")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys.")
def pull_cmd(profile, url, token, overwrite):
    """Pull variables from a remote server into the local vault."""
    password = prompt_password(confirm=False)
    try:
        existing = load_profile(profile, password)
    except Exception:
        existing = {}

    try:
        remote_vars = pull_variables(url, token, profile)
    except RemoteError as exc:
        raise click.ClickException(str(exc))

    added = 0
    skipped = 0
    for key, value in remote_vars.items():
        if key.startswith("__"):
            continue
        if key in existing and not overwrite:
            skipped += 1
            continue
        existing[key] = value
        added += 1

    try:
        save_profile(profile, existing, password)
    except Exception as exc:
        raise click.ClickException(f"Failed to save profile: {exc}")

    click.echo(f"Pulled {added} variable(s) into profile '{profile}'.")
    if skipped:
        click.echo(f"Skipped {skipped} existing key(s) (use --overwrite to replace).")
