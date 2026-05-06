"""Quota-aware storage helpers: enforce limits before writing variables."""

from __future__ import annotations

from typing import Dict, Any

from envault.storage import load_vault, save_vault, get_vault_path
from envault.quota import check_quota


class QuotaExceededError(Exception):
    """Raised when adding a variable would exceed the profile quota."""


def set_variable_quota_checked(
    key: str,
    value: str,
    password: str,
    profile: str = "default",
) -> None:
    """Set *key* = *value* in the vault, raising QuotaExceededError if over limit.

    Existing keys being updated do not count as new variables.
    """
    vault_path = get_vault_path(profile)
    variables = load_vault(vault_path, password)

    is_new = key not in variables or key.startswith("__")
    new_keys = 1 if is_new and not key.startswith("__") else 0

    if new_keys:
        status = check_quota(variables, new_keys=new_keys)
        if not status["allowed"]:
            raise QuotaExceededError(
                f"Quota exceeded for profile '{profile}': "
                f"{status['current']}/{status['limit']} variables used."
            )

    variables[key] = value
    save_vault(vault_path, variables, password)


def quota_status(
    password: str,
    profile: str = "default",
) -> Dict[str, Any]:
    """Return the quota status dict for *profile*."""
    vault_path = get_vault_path(profile)
    variables = load_vault(vault_path, password)
    return check_quota(variables)
