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
    """Outcome of a fix run. ``work_dir`` is the temp copy where Codex made its edits.

    Call :meth:`cleanup` when done with ``work_dir`` (e.g. after rendering the diff) to remove the
    temp copy — the loop creates it but does not own its lifetime beyond the return.
    """

    final: ScanResult
    work_dir: Path
    rounds_run: int
    thread_ids: list[str | None]

    def cleanup(self) -> None:
        """Remove the temp work copy. Safe to call once; idempotent if the dir is already gone."""
        shutil.rmtree(self.work_dir, ignore_errors=True)


async def run_fix_loop(
    session_factory: SessionFactory,
    project_dir: Path,
    *,
    max_rounds: int = 3,
    timeout: float = 30,
    codex_timeout: float = 120,
    fix_runner: Callable[..., Awaitable[FixOutcome]] | None = None,
) -> FixLoopResult:
    """Scan, fix each still-open finding via Codex, re-scan; repeat until green or capped.

    Operates on a ``shutil.copytree`` copy of *project_dir* so the fixture is never mutated in
    place. Each round attempts only findings still present in the latest scan (R2 idempotency: a
    finding Codex already cleared will not reappear, so it is never re-patched). On a Codex
    failure the finding is marked ``fix_attempted`` and left unresolved, and the loop continues
    with the rest (R3 graceful degradation). ``max_rounds`` bounds iterations; the wall-clock guard
    prevents a new round from starting past ``max_rounds * codex_timeout`` seconds. Note a single
    round may take up to ``<findings in round> * codex_timeout`` since each codex call is bounded
    independently — the guard bounds *round starts*, not total wall time. ``fix_runner`` defaults
    to :func:`run_codex_fix` and is overridable for tests.

    The caller owns the temp ``work_dir`` lifetime: call ``result.cleanup()`` once the diff/report
    has been rendered. On an exception inside the loop the temp copy is removed before re-raising.

    The final result's findings carry ``fix_attempted=True`` for any (rule, tool) the loop tried
    to patch, even across the fresh re-scan that produces new Finding objects — attempt history is
    keyed on ``(rule_id, tool)`` so it survives into the returned result.
    """
    # Resolve lazily so tests that monkeypatch mccoy.fix_loop.run_codex_fix take effect (a default
    # arg would capture the original at def-time and ignore the patch).
    if fix_runner is None:
        fix_runner = run_codex_fix

    work_dir = Path(shutil.copytree(project_dir, Path(tempfile.mkdtemp()) / project_dir.name))

    try:
        result = await _scan_workdir(session_factory, work_dir, timeout)
        if result.is_clean:
            return FixLoopResult(final=result, work_dir=work_dir, rounds_run=0, thread_ids=[])

        # R3 cost ceiling: don't START a new round past max_rounds * codex_timeout. A round in
        # progress still runs to completion (each codex call has its own codex_timeout bound).
        deadline = asyncio.get_running_loop().time() + max_rounds * codex_timeout

        thread_ids: list[str | None] = []
        attempted: set[tuple[str, str]] = set()  # (rule_id, tool) pairs the loop has patched
        rounds_run = 0
        while not result.is_clean and rounds_run < max_rounds:
            if asyncio.get_running_loop().time() >= deadline:
                break
            rounds_run += 1

            for finding in result.findings:
                # R2: only attempt findings the current scan still reports; cleared stay gone.
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
    except BaseException:
        # Don't leak the temp copy if the loop itself fails; the caller still gets the exception.
        shutil.rmtree(work_dir, ignore_errors=True)
        raise


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
