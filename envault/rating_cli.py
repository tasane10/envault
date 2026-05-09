"""CLI commands for variable rating in envault."""

import click
from envault.storage import load_vault, save_vault
from envault.cli import prompt_password
from envault.rating import (
    set_rating, remove_rating, get_rating, list_rated, filter_by_min_rating
)


@click.group(name="rating")
def rating_cmd():
    """Manage variable quality ratings."""


@rating_cmd.command(name="set")
@click.argument("key")
@click.argument("score", type=int)
@click.option("--profile", default="default", show_default=True)
def set_rating_cmd(key, score, profile):
    """Set a quality rating (1-5) for a variable."""
    password = prompt_password()
    variables = load_vault(password, profile=profile)
    try:
        updated = set_rating(variables, key, score)
    except (KeyError, ValueError) as exc:
        raise click.ClickException(str(exc))
    save_vault(updated, password, profile=profile)
    click.echo(f"Rated {key!r} as {score}/5.")


@rating_cmd.command(name="remove")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def remove_rating_cmd(key, profile):
    """Remove the rating from a variable."""
    password = prompt_password()
    variables = load_vault(password, profile=profile)
    updated = remove_rating(variables, key)
    save_vault(updated, password, profile=profile)
    click.echo(f"Rating removed from {key!r}.")


@rating_cmd.command(name="show")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def show_rating_cmd(key, profile):
    """Show the rating for a variable."""
    password = prompt_password()
    variables = load_vault(password, profile=profile)
    score = get_rating(variables, key)
    if score is None:
        click.echo(f"{key}: not rated")
    else:
        click.echo(f"{key}: {score}/5")


@rating_cmd.command(name="list")
@click.option("--profile", default="default", show_default=True)
@click.option("--min", "min_score", type=int, default=1, show_default=True)
def list_ratings_cmd(profile, min_score):
    """List all rated variables, sorted by score."""
    password = prompt_password()
    variables = load_vault(password, profile=profile)
    rated = list_rated(variables)
    filtered = [(k, s) for k, s in rated if s >= min_score]
    if not filtered:
        click.echo("No rated variables found.")
        return
    for key, score in filtered:
        click.echo(f"{key}: {score}/5")
