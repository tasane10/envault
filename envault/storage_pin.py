"""Pin-aware wrappers around storage operations.

Drop-in replacements for set_variable / delete_variable that
enforce pin guards before writing to the vault.
"""

from typing import Any
from envault.storage import load_vault, save_vault, get_vault_path
from envault.pin import guard_pinned, pin_variable, unpin_variable, get_pinned


def set_variable_pinned(
    key: str,
    value: Any,
    password: str,
    profile: str = "default",
) -> None:
    """Set *key* = *value* in the vault, raising if the key is pinned."""
    vault_path = get_vault_path(profile)
    variables = load_vault(vault_path, password)
    guard_pinned(variables, key)
    variables[key] = value
    save_vault(vault_path, variables, password)


def delete_variable_pinned(
    key: str,
    password: str,
    profile: str = "default",
) -> bool:
    """Delete *key* from the vault, raising if the key is pinned.

    Returns True if the key existed, False otherwise.
    """
    vault_path = get_vault_path(profile)
    variables = load_vault(vault_path, password)
    guard_pinned(variables, key)
    if key not in variables:
        return False
    del variables[key]
    save_vault(vault_path, variables, password)
    return True


def pin_and_save(
    key: str,
    password: str,
    profile: str = "default",
) -> None:
    """Pin *key* in the vault."""
    vault_path = get_vault_path(profile)
    variables = load_vault(vault_path, password)
    updated = pin_variable(variables, key)
    save_vault(vault_path, updated, password)


def unpin_and_save(
    key: str,
    password: str,
    profile: str = "default",
) -> None:
    """Unpin *key* in the vault."""
    vault_path = get_vault_path(profile)
    variables = load_vault(vault_path, password)
    updated = unpin_variable(variables, key)
    save_vault(vault_path, updated, password)


def list_pinned(
    password: str,
    profile: str = "default",
) -> list:
    """Return the list of pinned variable names for *profile*."""
    vault_path = get_vault_path(profile)
    variables = load_vault(vault_path, password)
    return get_pinned(variables)
