"""Workflow support: named sequences of CLI operations applied to a profile."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

VALID_STEPS = {"set", "delete", "tag", "pin", "annotate", "group"}


def get_workflow_dir(base: Path | None = None) -> Path:
    root = base or Path.home() / ".envault" / "workflows"
    root.mkdir(parents=True, exist_ok=True)
    return root


def get_workflow_path(name: str, base: Path | None = None) -> Path:
    return get_workflow_dir(base) / f"{name}.json"


def save_workflow(name: str, steps: list[dict[str, Any]], base: Path | None = None) -> Path:
    """Persist a workflow definition to disk."""
    if not name or not name.isidentifier():
        raise ValueError(f"Invalid workflow name: {name!r}")
    for step in steps:
        if step.get("action") not in VALID_STEPS:
            raise ValueError(f"Unknown action {step.get('action')!r}")
    path = get_workflow_path(name, base)
    path.write_text(json.dumps({"name": name, "steps": steps}, indent=2))
    return path


def load_workflow(name: str, base: Path | None = None) -> dict[str, Any]:
    """Load a workflow definition; raises FileNotFoundError if absent."""
    path = get_workflow_path(name, base)
    if not path.exists():
        raise FileNotFoundError(f"Workflow {name!r} not found")
    return json.loads(path.read_text())


def list_workflows(base: Path | None = None) -> list[str]:
    """Return sorted list of workflow names."""
    return sorted(p.stem for p in get_workflow_dir(base).glob("*.json"))


def delete_workflow(name: str, base: Path | None = None) -> bool:
    path = get_workflow_path(name, base)
    if path.exists():
        path.unlink()
        return True
    return False


def run_workflow(name: str, variables: dict[str, Any], base: Path | None = None) -> list[dict[str, Any]]:
    """Apply workflow steps to a variables dict (pure); returns log of applied steps."""
    wf = load_workflow(name, base)
    log: list[dict[str, Any]] = []
    for step in wf["steps"]:
        action = step["action"]
        key = step.get("key")
        value = step.get("value")
        if action == "set" and key:
            variables[key] = value
            log.append({"action": action, "key": key, "value": value, "status": "ok"})
        elif action == "delete" and key:
            removed = variables.pop(key, None)
            log.append({"action": action, "key": key, "status": "ok" if removed is not None else "not_found"})
        else:
            log.append({"action": action, "key": key, "status": "skipped"})
    return log
