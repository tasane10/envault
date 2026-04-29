"""Persist schema definitions alongside vault profiles."""
import json
from pathlib import Path
from typing import Dict, Any, Optional

_SCHEMA_DIR_NAME = "schemas"


def get_schema_path(profile: str = "default") -> Path:
    """Return the path to the schema file for the given profile."""
    from envault.profiles import get_profile_vault_path
    vault_path = get_profile_vault_path(profile)
    schema_dir = vault_path.parent / _SCHEMA_DIR_NAME
    return schema_dir / f"{profile}.schema.json"


def load_schema(profile: str = "default") -> Dict[str, Any]:
    """Load schema definition for a profile. Returns empty dict if not found."""
    path = get_schema_path(profile)
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def save_schema(schema: Dict[str, Any], profile: str = "default") -> None:
    """Persist schema definition for a profile."""
    path = get_schema_path(profile)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(schema, f, indent=2)


def delete_schema(profile: str = "default") -> bool:
    """Delete schema for a profile. Returns True if deleted, False if not found."""
    path = get_schema_path(profile)
    if path.exists():
        path.unlink()
        return True
    return False


def list_schemas() -> list:
    """Return a list of profile names that have associated schemas."""
    from envault.profiles import get_profile_vault_path
    vault_path = get_profile_vault_path("default")
    schema_dir = vault_path.parent / _SCHEMA_DIR_NAME
    if not schema_dir.exists():
        return []
    return [
        p.stem.replace(".schema", "")
        for p in schema_dir.glob("*.schema.json")
    ]
