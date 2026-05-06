"""Variable dependency tracking: define and resolve ordered dependencies between env vars."""

from __future__ import annotations

from typing import Dict, List, Set

_META_KEY = "__meta__"
_DEP_KEY = "dependencies"


def get_dependencies(variables: dict) -> Dict[str, List[str]]:
    """Return the dependency map stored in vault metadata."""
    meta = variables.get(_META_KEY, {})
    return dict(meta.get(_DEP_KEY, {}))


def set_dependency(variables: dict, key: str, depends_on: List[str]) -> dict:
    """Record that *key* depends on each name in *depends_on*.

    Raises KeyError if *key* or any dependency is not present in variables.
    Raises ValueError on circular dependency.
    """
    if key not in variables:
        raise KeyError(f"Variable '{key}' not found in vault.")
    for dep in depends_on:
        if dep not in variables:
            raise KeyError(f"Dependency '{dep}' not found in vault.")

    updated = dict(variables)
    meta = dict(updated.get(_META_KEY, {}))
    deps = dict(meta.get(_DEP_KEY, {}))
    deps[key] = sorted(set(depends_on))
    meta[_DEP_KEY] = deps
    updated[_META_KEY] = meta

    # Validate no cycles after update
    _check_cycles(deps)
    return updated


def remove_dependency(variables: dict, key: str) -> dict:
    """Remove all dependency declarations for *key*."""
    updated = dict(variables)
    meta = dict(updated.get(_META_KEY, {}))
    deps = dict(meta.get(_DEP_KEY, {}))
    deps.pop(key, None)
    meta[_DEP_KEY] = deps
    updated[_META_KEY] = meta
    return updated


def resolve_order(variables: dict) -> List[str]:
    """Return variable keys in dependency-safe topological order (leaves first).

    Keys with no dependency declarations appear after their dependencies.
    Metadata keys are excluded.
    """
    deps = get_dependencies(variables)
    keys = [k for k in variables if k != _META_KEY]

    visited: Set[str] = set()
    order: List[str] = []

    def visit(node: str, ancestors: Set[str]) -> None:
        if node in ancestors:
            raise ValueError(f"Circular dependency detected at '{node}'.")
        if node in visited:
            return
        for dep in deps.get(node, []):
            visit(dep, ancestors | {node})
        visited.add(node)
        order.append(node)

    for k in keys:
        visit(k, set())

    return order


def _check_cycles(deps: Dict[str, List[str]]) -> None:
    """Raise ValueError if *deps* contains a cycle."""
    visited: Set[str] = set()

    def visit(node: str, ancestors: Set[str]) -> None:
        if node in ancestors:
            raise ValueError(f"Circular dependency detected at '{node}'.")
        if node in visited:
            return
        for dep in deps.get(node, []):
            visit(dep, ancestors | {node})
        visited.add(node)

    for k in deps:
        visit(k, set())
