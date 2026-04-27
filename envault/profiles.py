"""Profile management for envault — allows grouping variables by named profiles (e.g., dev, staging, prod)."""

from typing import Optional
from envault.storage import get_vault_path, load_vault, save_vault


DEFAULT_PROFILE = "default"


def get_profile_vault_path(profile: str) -> object:
    """Return the vault path for a given profile name."""
    base = get_vault_path()
    if profile == DEFAULT_PROFILE:
        return base
    return base.parent / f".envault_{profile}.json.enc"


def list_profiles() -> list[str]:
    """Return all available profile names by scanning the vault directory."""
    base = get_vault_path()
    vault_dir = base.parent
    profiles = [DEFAULT_PROFILE]

    if not vault_dir.exists():
        return profiles

    for f in vault_dir.iterdir():
        if f.name.startswith(".envault_") and f.name.endswith(".json.enc"):
            name = f.name[len(".envault_"):-len(".json.enc")]
            if name:
                profiles.append(name)

    return sorted(set(profiles))


def load_profile(profile: str, password: str) -> dict:
    """Load variables for a given profile."""
    path = get_profile_vault_path(profile)
    return load_vault(password, vault_path=path)


def save_profile(profile: str, password: str, data: dict) -> None:
    """Save variables for a given profile."""
    path = get_profile_vault_path(profile)
    save_vault(data, password, vault_path=path)


def copy_profile(src_profile: str, dst_profile: str, password: str) -> int:
    """Copy all variables from one profile to another. Returns number of variables copied."""
    src_data = load_profile(src_profile, password)
    dst_data = load_profile(dst_profile, password)
    dst_data.update(src_data)
    save_profile(dst_profile, password, dst_data)
    return len(src_data)


def delete_profile(profile: str) -> bool:
    """Delete a profile vault file. Returns True if deleted, False if not found."""
    if profile == DEFAULT_PROFILE:
        raise ValueError("Cannot delete the default profile.")
    path = get_profile_vault_path(profile)
    if path.exists():
        path.unlink()
        return True
    return False
