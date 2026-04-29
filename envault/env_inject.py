"""Inject vault variables into a subprocess environment."""
from __future__ import annotations

import os
import subprocess
from typing import Optional

from envault.profiles import load_profile
from envault.ttl import is_expired

_META_PREFIX = "__"


def build_env(
    variables: dict,
    base_env: Optional[dict] = None,
    override: bool = True,
) -> dict:
    """Build an environment dict from vault variables.

    Args:
        variables: Decrypted vault dict (may include __meta keys).
        base_env: Base environment to merge into. Defaults to os.environ copy.
        override: If True, vault values overwrite existing env vars.

    Returns:
        New dict suitable for passing to subprocess as env.
    """
    env = dict(base_env if base_env is not None else os.environ)
    for key, value in variables.items():
        if key.startswith(_META_PREFIX):
            continue
        if is_expired(variables, key):
            continue
        if override or key not in env:
            env[key] = str(value)
    return env


def run_with_vault(
    command: list[str],
    password: str,
    profile: str = "default",
    override: bool = True,
    extra_env: Optional[dict] = None,
) -> subprocess.CompletedProcess:
    """Run a subprocess with vault variables injected into its environment.

    Args:
        command: Command and arguments list.
        password: Vault decryption password.
        profile: Profile name to load variables from.
        override: Whether vault vars override existing env vars.
        extra_env: Additional env vars to merge (applied after vault).

    Returns:
        CompletedProcess result.

    Raises:
        ValueError: If decryption fails.
    """
    variables = load_profile(profile, password)
    env = build_env(variables, override=override)
    if extra_env:
        env.update(extra_env)
    return subprocess.run(command, env=env, check=False)
