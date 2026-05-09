"""Audited workflow execution: runs a workflow and records each step via audit log."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from envault.audit import record_event
from envault.workflow import load_workflow, run_workflow


def run_workflow_audited(
    name: str,
    variables: dict[str, Any],
    profile: str = "default",
    base: Path | None = None,
) -> list[dict[str, Any]]:
    """Run *name* workflow, persist audit events for every step, return step log."""
    wf = load_workflow(name, base=base)
    log = run_workflow(name, variables, base=base)

    for entry in log:
        record_event(
            action=f"workflow:{entry['action']}",
            key=entry.get("key") or "",
            profile=profile,
            extra={
                "workflow": name,
                "status": entry["status"],
                "value": entry.get("value"),
            },
        )

    record_event(
        action="workflow:completed",
        key=name,
        profile=profile,
        extra={"steps": len(wf["steps"]), "applied": sum(1 for e in log if e["status"] == "ok")},
    )
    return log


def workflow_audit_summary(log: list[dict[str, Any]]) -> dict[str, int]:
    """Return a summary dict with counts per status."""
    summary: dict[str, int] = {}
    for entry in log:
        status = entry.get("status", "unknown")
        summary[status] = summary.get(status, 0) + 1
    return summary
