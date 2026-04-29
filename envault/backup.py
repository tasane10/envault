"""Backup and restore vault files to/from an archive."""

from __future__ import annotations

import json
import shutil
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from envault.profiles import get_profile_vault_path, list_profiles

_MANIFEST_NAME = "envault_backup_manifest.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def create_backup(output_path: Path | None = None, profiles: list[str] | None = None) -> Path:
    """Create a .tar.gz archive containing the requested profile vaults.

    Args:
        output_path: Destination file path.  Defaults to ``envault_backup_<ts>.tar.gz``
                     in the current working directory.
        profiles:    List of profile names to include.  ``None`` means all profiles.

    Returns:
        Path to the created archive.
    """
    all_profiles = list_profiles()
    selected = profiles if profiles is not None else all_profiles
    unknown = set(selected) - set(all_profiles)
    if unknown:
        raise ValueError(f"Unknown profiles: {', '.join(sorted(unknown))}")

    if output_path is None:
        output_path = Path.cwd() / f"envault_backup_{_timestamp()}.tar.gz"

    manifest = {"created_at": _timestamp(), "profiles": selected}

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        manifest_file = tmp_path / _MANIFEST_NAME
        manifest_file.write_text(json.dumps(manifest, indent=2))

        with tarfile.open(output_path, "w:gz") as tar:
            tar.add(manifest_file, arcname=_MANIFEST_NAME)
            for profile in selected:
                vault_file = get_profile_vault_path(profile)
                if vault_file.exists():
                    tar.add(vault_file, arcname=f"vaults/{profile}.json")

    return output_path


def restore_backup(archive_path: Path, dest_dir: Path | None = None, overwrite: bool = False) -> dict:
    """Restore vaults from a backup archive.

    Args:
        archive_path: Path to the ``.tar.gz`` backup file.
        dest_dir:     Override base directory for restored vaults (for testing).
        overwrite:    If ``False``, skip profiles whose vault already exists.

    Returns:
        A dict with keys ``restored`` and ``skipped`` (lists of profile names).
    """
    if not archive_path.exists():
        raise FileNotFoundError(f"Backup file not found: {archive_path}")

    restored: list[str] = []
    skipped: list[str] = []

    with tarfile.open(archive_path, "r:gz") as tar:
        for member in tar.getmembers():
            if not member.name.startswith("vaults/") or not member.name.endswith(".json"):
                continue
            profile_name = Path(member.name).stem
            target = (
                dest_dir / f"{profile_name}.json"
                if dest_dir
                else get_profile_vault_path(profile_name)
            )
            if target.exists() and not overwrite:
                skipped.append(profile_name)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            file_obj = tar.extractfile(member)
            if file_obj is not None:
                target.write_bytes(file_obj.read())
            restored.append(profile_name)

    return {"restored": restored, "skipped": skipped}
