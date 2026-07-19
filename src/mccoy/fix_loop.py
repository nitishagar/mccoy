"""Codex fix-and-verify loop: patch deterministic findings and re-scan until green.

The loop is the product's wedge (F5). It drives Codex against an isolated copy of the project so
the canonical fixture is never mutated, and the verdict after each round comes from the same
deterministic scanner the user would run — that is what makes re-scan idempotent (R2).
"""

from __future__ import annotations

import asyncio
import shutil
import tempfile
from collections.abc import Awaitable, Callable
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mccoy.codex_runner import FixOutcome, run_codex_fix
from mccoy.models import ScanResult
from mccoy.scanner import scan

# A session_factory yields a fresh ClientSession for the given work_dir, so the loop re-launches
# the (re-edited) server and re-connects per round. R2 (determinism) relies on this fresh connect:
# every re-scan reflects Codex's edits to the copy, not a stale server process.
# (The remediation plan wrote the factory as no-arg, but a no-arg factory cannot observe the copy
# this loop creates — re-scan would see stale tools. Passing work_dir is the minimal fix that
# satisfies the plan's own "re-scan after each round" intent. See REASONING.md.)
SessionFactory = Callable[[Path], AbstractAsyncContextManager[Any]]


@dataclass
class FixLoopResult:
    """Outcome of a fix run. ``work_dir`` is where Codex made its edits."""

    final: ScanResult
    work_dir: Path
    rounds_run: int
    thread_ids: list[str | None]


async def run_fix_loop(
    session_factory: SessionFactory,
    project_dir: Path,
    *,
    max_rounds: int = 3,
    timeout: float = 30,
    codex_timeout: float = 120,
    fix_runner: Callable[..., Awaitable[FixOutcome]] = run_codex_fix,
) -> FixLoopResult:
    """Scan, fix each still-open finding via Codex, re-scan; repeat until green or capped.

    Operates on a ``shutil.copytree`` copy of *project_dir* so the fixture is never mutated in
    place. Each round attempts only findings still present in the latest scan (R2 idempotency: a
    finding Codex already cleared will not reappear, so it is never re-patched). On a Codex
    failure the finding is marked ``fix_attempted`` and left unresolved, and the loop continues
    with the rest (R3 graceful degradation). ``max_rounds`` bounds iterations; an overall
    wall-clock guard bounds the loop at ``max_rounds * codex_timeout`` seconds (R3 cost ceiling).
    ``fix_runner`` defaults to :func:`run_codex_fix` and is overridable for tests.

    The final result's findings carry ``fix_attempted=True`` for any (rule, tool) the loop tried
    to patch, even across the fresh re-scan that produces new Finding objects — attempt history is
    keyed on ``(rule_id, tool)`` so it survives into the returned result.
    """
    work_dir = Path(shutil.copytree(project_dir, Path(tempfile.mkdtemp()) / project_dir.name))

    result = await _scan_workdir(session_factory, work_dir, timeout)
    if result.is_clean:
        return FixLoopResult(final=result, work_dir=work_dir, rounds_run=0, thread_ids=[])

    # R3 wall-clock ceiling for the whole loop, bounded by rounds * per-call timeout.
    deadline = asyncio.get_running_loop().time() + max_rounds * codex_timeout

    thread_ids: list[str | None] = []
    attempted: set[tuple[str, str]] = set()  # (rule_id, tool) pairs the loop has patched
    rounds_run = 0
    while not result.is_clean and rounds_run < max_rounds:
        if asyncio.get_running_loop().time() >= deadline:
            break
        rounds_run += 1

        for finding in result.findings:
            # R2: only attempt findings the current scan still reports; cleared ones never return.
            outcome = await fix_runner(finding, work_dir, timeout=codex_timeout)
            attempted.add((finding.rule_id, finding.tool))
            if outcome.thread_id:
                thread_ids.append(outcome.thread_id)

        # Fresh connect per round so the re-scan reflects Codex's edits to the project copy.
        result = await _scan_workdir(session_factory, work_dir, timeout)
        _restore_attempt_state(result, attempted)

    return FixLoopResult(
        final=result, work_dir=work_dir, rounds_run=rounds_run, thread_ids=thread_ids
    )


def _restore_attempt_state(result: ScanResult, attempted: set[tuple[str, str]]) -> None:
    """Re-mark ``fix_attempted`` on the freshly-scanned findings the loop has already patched.

    Each re-scan constructs new Finding objects; without this, attempt history would be lost and
    the final report could not tell the user which findings Codex actually tried to fix.
    """
    for finding in result.findings:
        if (finding.rule_id, finding.tool) in attempted:
            finding.fix_attempted = True


async def _scan_workdir(
    session_factory: SessionFactory, work_dir: Path, timeout: float
) -> ScanResult:
    async with session_factory(work_dir) as session:
        return await scan(session, timeout)


__all__ = ["FixLoopResult", "SessionFactory", "run_fix_loop"]
