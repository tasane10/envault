"""Variable annotation support: attach free-form description/notes to variables."""

from __future__ import annotations

META_KEY = "__annotations__"


def get_annotations(variables: dict) -> dict:
    """Return a copy of the annotations mapping from variables dict."""
    meta = variables.get(META_KEY, {})
    return dict(meta.get("descriptions", {}))


def set_annotation(variables: dict, key: str, description: str) -> dict:
    """Return a new variables dict with *key* annotated with *description*.

    Raises KeyError if *key* does not exist as a real variable.
    """
    if key not in variables or key.startswith("__"):
        raise KeyError(f"Variable '{key}' does not exist")
    meta = {k: v for k, v in variables.items()}
    annotations_block = dict(meta.get(META_KEY, {}))
    descriptions = dict(annotations_block.get("descriptions", {}))
    descriptions[key] = description
    annotations_block["descriptions"] = descriptions
    meta[META_KEY] = annotations_block
    return meta


def remove_annotation(variables: dict, key: str) -> dict:
    """Return a new variables dict with the annotation for *key* removed."""
    meta = {k: v for k, v in variables.items()}
    annotations_block = dict(meta.get(META_KEY, {}))
    descriptions = dict(annotations_block.get("descriptions", {}))
    descriptions.pop(key, None)
    annotations_block["descriptions"] = descriptions
    meta[META_KEY] = annotations_block
    return meta


def get_annotation(variables: dict, key: str) -> str | None:
    """Return the annotation string for *key*, or None if not annotated."""
    return get_annotations(variables).get(key)


def filter_annotated(variables: dict) -> dict:
    """Return only variable keys that have an annotation, mapped to their description."""
    return {k: v for k, v in get_annotations(variables).items() if k in variables}
