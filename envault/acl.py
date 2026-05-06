"""Access control lists for vault variables — restrict read/write by role."""

from __future__ import annotations

META_KEY = "__acl__"
VALID_ROLES = {"reader", "writer", "admin"}


def get_acl(variables: dict) -> dict:
    """Return the ACL mapping: {key: [roles]} from vault variables."""
    meta = variables.get("__meta__", {})
    return dict(meta.get(META_KEY, {}))


def set_acl(variables: dict, key: str, roles: list[str]) -> dict:
    """Return updated variables with ACL roles set for *key*."""
    invalid = set(roles) - VALID_ROLES
    if invalid:
        raise ValueError(f"Invalid roles: {', '.join(sorted(invalid))}. Valid: {', '.join(sorted(VALID_ROLES))}")
    if key not in variables:
        raise KeyError(f"Variable '{key}' does not exist in the vault.")
    variables = dict(variables)
    meta = dict(variables.get("__meta__", {}))
    acl = dict(meta.get(META_KEY, {}))
    if roles:
        acl[key] = sorted(set(roles))
    else:
        acl.pop(key, None)
    meta[META_KEY] = acl
    variables["__meta__"] = meta
    return variables


def remove_acl(variables: dict, key: str) -> dict:
    """Return updated variables with ACL entry removed for *key*."""
    variables = dict(variables)
    meta = dict(variables.get("__meta__", {}))
    acl = dict(meta.get(META_KEY, {}))
    acl.pop(key, None)
    meta[META_KEY] = acl
    variables["__meta__"] = meta
    return variables


def check_access(variables: dict, key: str, role: str) -> bool:
    """Return True if *role* is permitted to access *key*.

    If no ACL is set for *key*, access is granted to all roles.
    Admins always have access.
    """
    if role == "admin":
        return True
    acl = get_acl(variables)
    if key not in acl:
        return True
    return role in acl[key]


def list_acl(variables: dict) -> list[dict]:
    """Return a sorted list of {key, roles} dicts for display."""
    acl = get_acl(variables)
    return [{"key": k, "roles": v} for k, v in sorted(acl.items())]
