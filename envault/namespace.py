"""Namespace support for grouping environment variables under prefixes."""

from typing import Dict, List, Optional, Tuple

_META_PREFIX = "__"


def get_namespace_prefix(namespace: str) -> str:
    """Return the key prefix string for a given namespace."""
    ns = namespace.strip().upper().rstrip("_")
    if not ns:
        raise ValueError("Namespace must not be empty.")
    return f"{ns}_"


def list_namespaces(variables: Dict[str, str]) -> List[str]:
    """Return a sorted list of distinct namespaces found in variables."""
    namespaces = set()
    for key in variables:
        if key.startswith(_META_PREFIX):
            continue
        if "_" in key:
            ns = key.split("_")[0]
            if ns:
                namespaces.add(ns)
    return sorted(namespaces)


def filter_by_namespace(
    variables: Dict[str, str], namespace: str
) -> Dict[str, str]:
    """Return only variables whose keys start with the given namespace prefix."""
    prefix = get_namespace_prefix(namespace)
    return {
        k: v
        for k, v in variables.items()
        if k.startswith(prefix) and not k.startswith(_META_PREFIX)
    }


def strip_namespace(
    variables: Dict[str, str], namespace: str
) -> Dict[str, str]:
    """Return variables with the namespace prefix removed from keys."""
    prefix = get_namespace_prefix(namespace)
    return {
        k[len(prefix):]: v
        for k, v in variables.items()
        if k.startswith(prefix)
    }


def add_namespace(
    variables: Dict[str, str], namespace: str
) -> Dict[str, str]:
    """Return variables with the namespace prefix added to all keys."""
    prefix = get_namespace_prefix(namespace)
    return {f"{prefix}{k}": v for k, v in variables.items()}


def move_namespace(
    variables: Dict[str, str], src: str, dst: str
) -> Tuple[Dict[str, str], int]:
    """Rename all variables from src namespace to dst namespace.

    Returns the updated variables dict and the count of renamed keys.
    """
    src_prefix = get_namespace_prefix(src)
    dst_prefix = get_namespace_prefix(dst)
    updated = dict(variables)
    count = 0
    for key in list(variables):
        if key.startswith(src_prefix) and not key.startswith(_META_PREFIX):
            new_key = dst_prefix + key[len(src_prefix):]
            updated[new_key] = updated.pop(key)
            count += 1
    return updated, count
