"""CLI commands for the template rendering feature."""
from __future__ import annotations

import click

from envault.profiles import get_profile_vault_path, load_profile
from envault.template import extract_placeholders, render_file


@click.group("template")
def template_cmd() -> None:
    """Render templates using stored environment variables."""


@template_cmd.command("render")
@click.argument("template_file", type=click.Path(exists=True, dir_okay=False))
@click.option("-o", "--output", default=None, help="Write rendered output to this file.")
@click.option("-p", "--profile", default="default", show_default=True, help="Vault profile to use.")
@click.option("--strict", is_flag=True, default=False, help="Fail on unknown placeholders.")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def render_cmd(template_file: str, output: str | None, profile: str, strict: bool, password: str) -> None:
    """Render TEMPLATE_FILE substituting {{KEY}} placeholders from the vault."""
    vault_path = get_profile_vault_path(profile)
    variables = load_profile(vault_path, password)

    try:
        rendered = render_file(template_file, variables, output_path=output, strict=strict)
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc

    if output:
        click.echo(f"Rendered template written to {output}")
    else:
        click.echo(rendered, nl=False)


@template_cmd.command("placeholders")
@click.argument("template_file", type=click.Path(exists=True, dir_okay=False))
def placeholders_cmd(template_file: str) -> None:
    """List all {{KEY}} placeholders found in TEMPLATE_FILE."""
    with open(template_file, "r", encoding="utf-8") as fh:
        template = fh.read()

    keys = extract_placeholders(template)
    if keys:
        for key in keys:
            click.echo(key)
    else:
        click.echo("No placeholders found.")
