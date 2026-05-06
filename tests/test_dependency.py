"""Tests for envault.dependency."""

from __future__ import annotations

import pytest

from envault.dependency import (
    get_dependencies,
    remove_dependency,
    resolve_order,
    set_dependency,
)

_VARS = {"A": "1", "B": "2", "C": "3"}


def test_get_dependencies_empty_when_no_meta():
    assert get_dependencies({"X": "1"}) == {}


def test_set_dependency_stores_sorted_deps():
    result = set_dependency(_VARS, "C", ["B", "A"])
    deps = get_dependencies(result)
    assert deps["C"] == ["A", "B"]


def test_set_dependency_does_not_mutate_original():
    original = dict(_VARS)
    set_dependency(original, "B", ["A"])
    assert "__meta__" not in original


def test_set_dependency_raises_for_missing_key():
    with pytest.raises(KeyError, match="MISSING"):
        set_dependency(_VARS, "MISSING", ["A"])


def test_set_dependency_raises_for_missing_dependency():
    with pytest.raises(KeyError, match="Z"):
        set_dependency(_VARS, "A", ["Z"])


def test_set_dependency_raises_on_direct_cycle():
    v = set_dependency(_VARS, "B", ["A"])
    with pytest.raises(ValueError, match="Circular"):
        set_dependency(v, "A", ["B"])


def test_set_dependency_raises_on_self_cycle():
    with pytest.raises(ValueError, match="Circular"):
        set_dependency(_VARS, "A", ["A"])


def test_remove_dependency_clears_entry():
    v = set_dependency(_VARS, "C", ["A"])
    v = remove_dependency(v, "C")
    assert "C" not in get_dependencies(v)


def test_remove_dependency_noop_when_not_set():
    result = remove_dependency(_VARS, "NONEXISTENT")
    assert get_dependencies(result) == {}


def test_resolve_order_leaves_first():
    v = set_dependency(_VARS, "C", ["B"])
    v = set_dependency(v, "B", ["A"])
    order = resolve_order(v)
    assert order.index("A") < order.index("B") < order.index("C")


def test_resolve_order_excludes_meta_key():
    v = set_dependency(_VARS, "B", ["A"])
    order = resolve_order(v)
    assert "__meta__" not in order


def test_resolve_order_no_deps_returns_all_keys():
    order = resolve_order(_VARS)
    assert set(order) == {"A", "B", "C"}


def test_resolve_order_detects_cycle():
    # Manually craft a cycle in metadata to bypass set_dependency guard
    v = dict(_VARS)
    v["__meta__"] = {"dependencies": {"A": ["B"], "B": ["A"]}}
    with pytest.raises(ValueError, match="Circular"):
        resolve_order(v)
