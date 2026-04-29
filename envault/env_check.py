"""Environment health check: compare vault variables against the current process environment."""

from __future__ import annotations

from typing import Dict, List, Tuple


CheckResult = Dict[str, object]


def check_variables(
    vault_vars: Dict[str, str],
    env: Dict[str, str],
) -> List[CheckResult]:
    """Compare vault variables to the given environment mapping.

    Returns a list of result dicts with keys:
      - key: variable name
      - status: 'ok' | 'missing' | 'mismatch'
      - vault_value: value stored in vault (or None)
      - env_value: value found in env (or None)
    """
    results: List[CheckResult] = []
    for key, vault_value in vault_vars.items():
        if key.startswith("_"):
            # skip internal metadata keys
            continue
        env_value = env.get(key)
        if env_value is None:
            status = "missing"
        elif env_value != vault_value:
            status = "mismatch"
        else:
            status = "ok"
        results.append(
            {
                "key": key,
                "status": status,
                "vault_value": vault_value,
                "env_value": env_value,
            }
        )
    return results


def format_check_results(results: List[CheckResult]) -> str:
    """Return a human-readable summary of check results."""
    if not results:
        return "No variables to check."

    lines: List[str] = []
    ok = [r for r in results if r["status"] == "ok"]
    missing = [r for r in results if r["status"] == "missing"]
    mismatches = [r for r in results if r["status"] == "mismatch"]

    for r in missing:
        lines.append(f"  MISSING   {r['key']}")
    for r in mismatches:
        lines.append(f"  MISMATCH  {r['key']}  (vault={r['vault_value']!r}, env={r['env_value']!r})")
    for r in ok:
        lines.append(f"  OK        {r['key']}")

    summary_parts: List[str] = []
    if ok:
        summary_parts.append(f"{len(ok)} ok")
    if missing:
        summary_parts.append(f"{len(missing)} missing")
    if mismatches:
        summary_parts.append(f"{len(mismatches)} mismatched")

    lines.append("\n" + ", ".join(summary_parts))
    return "\n".join(lines)
