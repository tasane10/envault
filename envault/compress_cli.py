"""CLI commands for vault compression — pack and unpack compressed vault blobs."""

import click
import json
from envault.profiles import load_profile
from envault.storage import save_vault
from envault.compress import compress_variables, decompress_variables, compress_ratio
from envault.cli import prompt_password


@click.group("compress")
def compress_cmd():
    """Compress and decompress vault data."""


@compress_cmd.command("pack")
@click.option("--profile", default="default", show_default=True, help="Profile name.")
@click.option("--output", "-o", default=None, help="Write blob to file instead of stdout.")
def pack_cmd(profile: str, output):
    """Compress vault variables to a portable blob."""
    password = prompt_password(confirm=False)
    variables = load_profile(profile, password)
    # Strip metadata keys from export
    exportable = {k: v for k, v in variables.items() if not k.startswith("__")}
    blob = compress_variables(exportable)
    ratio = compress_ratio(exportable)
    if output:
        with open(output, "w") as fh:
            fh.write(blob)
        click.echo(f"Packed {len(exportable)} variable(s) → {output}  (ratio: {ratio:.2f})")
    else:
        click.echo(blob)


@compress_cmd.command("unpack")
@click.argument("blob_file")
@click.option("--profile", default="default", show_default=True, help="Target profile.")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys.")
def unpack_cmd(blob_file: str, profile: str, overwrite: bool):
    """Decompress a blob and import variables into a profile."""
    with open(blob_file, "r") as fh:
        blob = fh.read().strip()
    try:
        incoming = decompress_variables(blob)
    except (ValueError, json.JSONDecodeError) as exc:
        raise click.ClickException(f"Failed to decompress blob: {exc}")

    password = prompt_password(confirm=False)
    existing = load_profile(profile, password)

    added, skipped = 0, 0
    for key, value in incoming.items():
        if key in existing and not overwrite:
            skipped += 1
            continue
        existing[key] = value
        added += 1

    from envault.profiles import get_profile_vault_path
    from envault.storage import save_vault
    save_vault(get_profile_vault_path(profile), password, existing)
    click.echo(f"Imported {added} variable(s) into '{profile}' (skipped {skipped}).")
