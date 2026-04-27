"""CLI commands for searching environment variables."""

import click
from envault.cli import prompt_password
from envault.search import search_variables, format_search_results


@click.group("search")
def search_cmd():
    """Search environment variables across profiles."""


@search_cmd.command("find")
@click.argument("pattern")
@click.option("--profile", "-p", default=None, help="Limit search to a specific profile.")
@click.option("--keys-only", is_flag=True, default=False, help="Match against keys only.")
@click.option("--values-only", is_flag=True, default=False, help="Match against values only.")
@click.option("--hide-values", is_flag=True, default=False, help="Do not display values in output.")
def find_cmd(pattern, profile, keys_only, values_only, hide_values):
    """Search for variables matching PATTERN (regex supported)."""
    if keys_only and values_only:
        raise click.UsageError("--keys-only and --values-only are mutually exclusive.")

    password = prompt_password(confirm=False)

    try:
        results = search_variables(
            pattern=pattern,
            password=password,
            profile=profile,
            keys_only=keys_only,
            values_only=values_only,
        )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    output = format_search_results(results, show_values=not hide_values)
    click.echo(output)

    total = sum(len(v) for v in results.values())
    click.echo(f"\n{total} match(es) across {len(results)} profile(s).")
