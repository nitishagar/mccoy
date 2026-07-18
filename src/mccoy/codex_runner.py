"""JSONL-aware Codex subprocess runner."""

from __future__ import annotations

import asyncio
import json
import shutil
from pathlib import Path

from pydantic import BaseModel

from mccoy.models import Finding


class FixOutcome(BaseModel):
    success: bool = False
    thread_id: str | None = None
    patch_applied: bool = False
    error: str | None = None


async def run_codex_fix(
    finding: Finding, project_dir: Path, thread_id: str | None = None, timeout: float = 120
) -> FixOutcome:
    if not shutil.which("codex"):
        return FixOutcome(
            error="Codex CLI required; install from https://developers.openai.com/codex/"
        )
    prompt = (
        f"Fix MCP scanner finding {finding.rule_id}: {finding.fix_hint}. "
        "Work only in the requested project."
    )
    process = await asyncio.create_subprocess_exec(
        "codex",
        "exec",
        "--sandbox",
        "workspace-write",
        "--cd",
        str(project_dir),
        "--skip-git-repo-check",
        "--json",
        prompt,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    outcome = FixOutcome(thread_id=thread_id)
    try:
        assert process.stdout is not None
        while line := await asyncio.wait_for(process.stdout.readline(), timeout):
            event = json.loads(line)
            outcome.thread_id = event.get("thread_id", outcome.thread_id)
            if event.get("type") in {"turn.failed", "error"}:
                outcome.error = str(event)
            if event.get("type") == "turn.completed":
                outcome.success = True
            if event.get("item", {}).get("type") == "file_change":
                outcome.patch_applied = True
        await process.wait()
    except TimeoutError:
        process.kill()
        await process.wait()
        outcome.error = "Codex timed out"
    return outcome
