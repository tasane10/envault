"""Variable rating/quality scoring for envault."""

from __future__ import annotations

META_PREFIX = "__"
VALID_RATINGS = (1, 2, 3, 4, 5)


def _is_meta(key: str) -> bool:
    return key.startswith(META_PREFIX)


def get_ratings(variables: dict) -> dict:
    """Return a copy of the ratings metadata dict."""
    meta = variables.get("__meta", {})
    return dict(meta.get("ratings", {}))


def set_rating(variables: dict, key: str, score: int) -> dict:
    """Return a new variables dict with the rating set for key."""
    if _is_meta(key):
        raise ValueError(f"Cannot rate metadata key: {key!r}")
    if key not in variables:
        raise KeyError(f"Variable {key!r} does not exist")
    if score not in VALID_RATINGS:
        raise ValueError(f"Rating must be one of {VALID_RATINGS}, got {score}")
    updated = dict(variables)
    meta = dict(updated.get("__meta", {}))
    ratings = dict(meta.get("ratings", {}))
    ratings[key] = score
    meta["ratings"] = ratings
    updated["__meta"] = meta
    return updated


def remove_rating(variables: dict, key: str) -> dict:
    """Return a new variables dict with the rating removed for key."""
    updated = dict(variables)
    meta = dict(updated.get("__meta", {}))
    ratings = dict(meta.get("ratings", {}))
    ratings.pop(key, None)
    meta["ratings"] = ratings
    updated["__meta"] = meta
    return updated


def get_rating(variables: dict, key: str) -> int | None:
    """Return the rating score for a key, or None if not rated."""
    return get_ratings(variables).get(key)


def list_rated(variables: dict) -> list[tuple[str, int]]:
    """Return list of (key, score) sorted by score descending, then key."""
    ratings = get_ratings(variables)
    return sorted(ratings.items(), key=lambda x: (-x[1], x[0]))


def filter_by_min_rating(variables: dict, min_score: int) -> dict:
    """Return only variable keys with rating >= min_score (excludes meta)."""
    ratings = get_ratings(variables)
    return {
        k: v for k, v in variables.items()
        if not _is_meta(k) and ratings.get(k, 0) >= min_score
    }
