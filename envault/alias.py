"""Alias management for envault: map short names to variable keys."""

from __future__ import annotations

META_KEY = "__aliases__"


def get_aliases(variables: dict) -> dict[str, str]:
    """Return the alias map {alias: key} stored in variables metadata."""
    meta = variables.get("__meta__", {})
    return dict(meta.get(META_KEY, {}))


def set_alias(variables: dict, alias: str, key: str) -> dict:
    """Add or update an alias pointing to *key*. Returns new variables dict."""
    if key not in variables:
        raise KeyError(f"Variable '{key}' does not exist in the vault.")
    if alias == key:
        raise ValueError("Alias must differ from the target key.")

    meta = dict(variables.get("__meta__", {}))
    aliases = dict(meta.get(META_KEY, {}))
    aliases[alias] = key
    meta[META_KEY] = aliases
    return {**variables, "__meta__": meta}


def remove_alias(variables: dict, alias: str) -> dict:
    """Remove an alias. Returns new variables dict."""
    meta = dict(variables.get("__meta__", {}))
    aliases = dict(meta.get(META_KEY, {}))
    if alias not in aliases:
        raise KeyError(f"Alias '{alias}' not found.")
    del aliases[alias]
    meta[META_KEY] = aliases
    return {**variables, "__meta__": meta}


def resolve_alias(variables: dict, name: str) -> str:
    """Return the real key for *name*, resolving an alias if necessary."""
    aliases = get_aliases(variables)
    return aliases.get(name, name)


def list_aliases(variables: dict) -> list[tuple[str, str]]:
    """Return sorted list of (alias, key) pairs."""
    return sorted(get_aliases(variables).items())
