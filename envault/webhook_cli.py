"""CLI commands for managing envault webhooks."""
from __future__ import annotations

import click

from envault.storage import load_vault, save_vault
from envault.webhook import (
    SUPPORTED_EVENTS,
    list_webhooks,
    set_webhook,
    remove_webhook,
    notify,
)


@click.group("webhook")
def webhook_cmd() -> None:
    """Manage webhook notifications for vault events."""


@webhook_cmd.command("add")
@click.argument("event", type=click.Choice(sorted(SUPPORTED_EVENTS)))
@click.argument("url")
@click.option("--profile", default="default", show_default=True)
@click.password_option("--password", prompt="Vault password")
def add_cmd(event: str, url: str, profile: str, password: str) -> None:
    """Register URL for EVENT notifications."""
    variables = load_vault(password, profile=profile)
    variables = set_webhook(variables, event, url)
    save_vault(variables, password, profile=profile)
    click.echo(f"Webhook added: [{event}] -> {url}")


@webhook_cmd.command("remove")
@click.argument("event", type=click.Choice(sorted(SUPPORTED_EVENTS)))
@click.argument("url")
@click.option("--profile", default="default", show_default=True)
@click.password_option("--password", prompt="Vault password")
def remove_cmd(event: str, url: str, profile: str, password: str) -> None:
    """Remove URL from EVENT notifications."""
    variables = load_vault(password, profile=profile)
    variables = remove_webhook(variables, event, url)
    save_vault(variables, password, profile=profile)
    click.echo(f"Webhook removed: [{event}] -> {url}")


@webhook_cmd.command("list")
@click.option("--profile", default="default", show_default=True)
@click.password_option("--password", prompt="Vault password")
def list_cmd(profile: str, password: str) -> None:
    """List all registered webhooks."""
    variables = load_vault(password, profile=profile)
    hooks = list_webhooks(variables)
    if not hooks:
        click.echo("No webhooks registered.")
        return
    for entry in hooks:
        click.echo(f"  [{entry['event']}] {entry['url']}")


@webhook_cmd.command("fire")
@click.argument("event", type=click.Choice(sorted(SUPPORTED_EVENTS)))
@click.option("--profile", default="default", show_default=True)
@click.option("--message", default="", help="Optional message to include in payload.")
@click.password_option("--password", prompt="Vault password")
def fire_cmd(event: str, profile: str, message: str, password: str) -> None:
    """Manually fire all webhooks for EVENT."""
    variables = load_vault(password, profile=profile)
    results = notify(variables, event, {"profile": profile, "message": message, "manual": True})
    if not results:
        click.echo("No webhooks registered for this event.")
        return
    for r in results:
        status = click.style("OK", fg="green") if r["success"] else click.style("FAILED", fg="red")
        click.echo(f"  {status}  {r['url']}")
