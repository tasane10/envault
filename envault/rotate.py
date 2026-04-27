"""Key rotation: re-encrypt vault contents with a new password."""

from typing import Optional
from envault.storage import load_vault, save_vault
from envault.profiles import get_profile_vault_path
from envault.audit import record_event


def rotate_key(
    old_password: str,
    new_password: str,
    profile: str = "default",
    vault_path: Optional[str] = None,
) -> dict:
    """Re-encrypt the vault with a new password.

    Loads the vault using the old password, then saves it using the new
    password.  Returns a summary dict with the number of variables rotated.

    Raises ValueError if the old password is incorrect (propagated from
    load_vault / decrypt).
    """
    if vault_path is None:
        vault_path = str(get_profile_vault_path(profile))

    variables = load_vault(vault_path, old_password)
    save_vault(vault_path, new_password, variables)

    record_event(
        action="rotate_key",
        key="*",
        profile=profile,
        metadata={"variables_count": len(variables)},
    )

    return {"profile": profile, "rotated": len(variables)}


def rotate_key_all_profiles(
    old_password: str,
    new_password: str,
    base_dir: Optional[str] = None,
) -> list:
    """Rotate the encryption key for every profile found in base_dir.

    Returns a list of summary dicts (one per profile).
    """
    from envault.profiles import list_profiles

    profiles = list_profiles(base_dir=base_dir)
    results = []
    for profile in profiles:
        vault_path = str(get_profile_vault_path(profile, base_dir=base_dir))
        result = rotate_key(old_password, new_password, profile=profile, vault_path=vault_path)
        results.append(result)
    return results
