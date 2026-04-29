"""CLI commands for injecting vault variables into subprocesses."""
from __future__ import annotations

import sys

import click

from envault.cli import prompt_password
from envault.env_inject import build_env, run_with_vault
from envault.profiles import load_profile


@click.group(name="inject")
def inject_cmd():
    """Inject vault variables into a subprocess environment."""


@inject_cmd.command(name="run")
@click.option("--profile", default="default", show_default=True, help="Profile to load.")
@click.option("--no-override", is_flag=True, default=False, help="Don't overwrite existing env vars.")
@click.argument("command", nargs=-1, required=True)
def run_cmd(profile: str, no_override: bool, command: tuple):
    """Run COMMAND with vault variables injected into its environment.

    Example: envault inject run --profile prod -- env
    """
    password = prompt_password()
    try:
        result = run_with_vault(
            list(command),
            password=password,
            profile=profile,
            override=not no_override,
        )
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc
    sys.exit(result.returncode)


@inject_cmd.command(name="env")
@click.option("--profile", default="default", show_default=True, help="Profile to load.")
@click.option("--no-override", is_flag=True, default=False, help="Don't overwrite existing env vars.")
def env_cmd(profile: str, no_override: bool):
    """Print the merged environment that would be injected, one KEY=VALUE per line."""
    password = prompt_password()
    try:
        variables = load_profile(profile, password)
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc
    merged = build_env(variables, override=not no_override)
    for key, value in sorted(merged.items()):
        click.echo(f"{key}={value}")
