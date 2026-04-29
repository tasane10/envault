import click
import json
from envault.schema import validate_variables, format_validation_results, FieldSchema, ValidationError
from envault.storage import load_vault, save_vault, get_vault_path
from envault.cli import prompt_password


@click.group(name="schema")
def schema_cmd():
    """Manage variable schema and validation rules."""
    pass


@schema_cmd.command(name="validate")
@click.option("--profile", default="default", show_default=True, help="Profile to validate.")
@click.option("--schema-file", required=True, type=click.Path(exists=True), help="JSON schema file.")
def validate_cmd(profile, schema_file):
    """Validate vault variables against a schema file."""
    password = prompt_password(confirm=False)
    vault_path = get_vault_path(profile)
    variables = load_vault(vault_path, password)

    with open(schema_file) as f:
        raw = json.load(f)

    schema = {k: FieldSchema(**v) for k, v in raw.items()}
    results = validate_variables(variables, schema)

    if not results:
        click.echo("All variables passed schema validation.")
        return

    click.echo(format_validation_results(results))
    raise SystemExit(1)


@schema_cmd.command(name="show")
@click.option("--schema-file", required=True, type=click.Path(exists=True), help="JSON schema file.")
def show_cmd(schema_file):
    """Display the current schema definition."""
    with open(schema_file) as f:
        raw = json.load(f)

    if not raw:
        click.echo("Schema file is empty.")
        return

    for key, field in raw.items():
        parts = [f"  {key}:"]
        if field.get("required"):
            parts.append("required")
        if field.get("pattern"):
            parts.append(f"pattern={field['pattern']}")
        if field.get("min_length") is not None:
            parts.append(f"min_length={field['min_length']}")
        if field.get("max_length") is not None:
            parts.append(f"max_length={field['max_length']}")
        if field.get("allowed_values"):
            parts.append(f"allowed={field['allowed_values']}")
        click.echo(" ".join(parts))
