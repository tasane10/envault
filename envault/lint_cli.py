"""CLI commands for linting environment variable names and values."""

import click
from envault.profiles import get_profile_vault_path, load_profile
from envault.lint import lint_variables, format_lint_results


@click.group("lint")
def lint_cmd():
    """Lint and validate environment variable names and values."""


@lint_cmd.command("check")
@click.option("--profile", default="default", show_default=True, help="Profile to lint.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--errors-only", is_flag=True, default=False, help="Show only errors, not warnings.")
def check_cmd(profile: str, password: str, errors_only: bool):
    """Check all variables in a profile for naming and value issues."""
    try:
        variables = load_profile(profile, password)
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc

    results = lint_variables(variables)

    if errors_only:
        results = {
            name: [i for i in issues if i["level"] == "error"]
            for name, issues in results.items()
        }
        results = {name: issues for name, issues in results.items() if issues}

    total = sum(len(v) for v in results.values())
    errors = sum(1 for issues in results.values() for i in issues if i["level"] == "error")
    warnings = total - errors

    if results:
        click.echo(format_lint_results(results))
        click.echo(f"\n{total} issue(s): {errors} error(s), {warnings} warning(s).")
        raise SystemExit(1)
    else:
        click.echo("No issues found.")


@lint_cmd.command("name")
@click.argument("name")
def check_name_cmd(name: str):
    """Check a single variable name for issues."""
    from envault.lint import lint_name

    issues = lint_name(name)
    if issues:
        for issue in issues:
            level = issue["level"].upper()
            click.echo(f"[{level}] {name}: {issue['message']}")
        raise SystemExit(1)
    else:
        click.echo(f"{name}: OK")
