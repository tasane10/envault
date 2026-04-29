"""CLI commands for creating and consuming share bundles."""

from __future__ import annotations

import json
import sys

import click

from envault.profiles import load_profile
from envault.share import (
    bundle_from_file,
    bundle_to_file,
    create_share_bundle,
    open_share_bundle,
)
from envault.storage import save_vault, set_variable


@click.group("share")
def share_cmd():
    """Create and consume encrypted share bundles."""


@share_cmd.command("create")
@click.option("--profile", default="default", show_default=True)
@click.option("--output", "-o", required=True, help="Destination .json file.")
@click.option("--ttl", default=None, type=int, help="Expiry in seconds.")
@click.option("--keys", default=None, help="Comma-separated key whitelist.")
@click.password_option("--password", prompt="Vault password")
@click.option("--share-password", prompt=True, hide_input=True,
              confirmation_prompt=True, help="Password for the share bundle.")
def create_cmd(profile, output, ttl, keys, password, share_password):
    """Export an encrypted share bundle from a vault profile."""
    try:
        variables = load_profile(profile, password)
    except Exception as exc:
        click.echo(f"Error reading vault: {exc}", err=True)
        sys.exit(1)

    key_list = [k.strip() for k in keys.split(",")] if keys else None
    bundle = create_share_bundle(variables, share_password, ttl_seconds=ttl, keys=key_list)
    bundle_to_file(bundle, output)
    click.echo(f"Share bundle written to {output}  (token: {bundle['token']})")


@share_cmd.command("import")
@click.argument("bundle_file")
@click.option("--profile", default="default", show_default=True)
@click.option("--overwrite", is_flag=True, default=False)
@click.password_option("--password", prompt="Vault password")
@click.option("--share-password", prompt=True, hide_input=True,
              help="Password protecting the share bundle.")
def import_cmd(bundle_file, profile, overwrite, password, share_password):
    """Import variables from an encrypted share bundle into a vault profile."""
    try:
        bundle = bundle_from_file(bundle_file)
    except FileNotFoundError:
        click.echo(f"Bundle file not found: {bundle_file}", err=True)
        sys.exit(1)

    try:
        incoming = open_share_bundle(bundle, share_password)
    except ValueError as exc:
        click.echo(f"Cannot open bundle: {exc}", err=True)
        sys.exit(1)

    try:
        variables = load_profile(profile, password)
    except Exception:
        variables = {}

    added = skipped = 0
    for key, value in incoming.items():
        if key in variables and not overwrite:
            skipped += 1
            continue
        variables = set_variable(variables, key, value)
        added += 1

    from envault.profiles import save_profile
    save_profile(profile, variables, password)
    click.echo(f"Imported {added} variable(s), skipped {skipped}.")


@share_cmd.command("inspect")
@click.argument("bundle_file")
def inspect_cmd(bundle_file):
    """Show metadata of a share bundle without decrypting it."""
    try:
        bundle = bundle_from_file(bundle_file)
    except FileNotFoundError:
        click.echo(f"Bundle file not found: {bundle_file}", err=True)
        sys.exit(1)

    import time
    click.echo(f"Token      : {bundle.get('token', 'n/a')}")
    created = bundle.get("created_at")
    if created:
        click.echo(f"Created at : {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(created))}")
    expires = bundle.get("expires_at")
    if expires:
        click.echo(f"Expires at : {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expires))}")
    else:
        click.echo("Expires at : never")
