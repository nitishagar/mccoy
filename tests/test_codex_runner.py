"""Tests for the Codex subprocess runner's robustness (R3 graceful degradation).

These mock the codex subprocess (codex is not installed in CI) and focus on the failure modes
that would otherwise violate R3: non-JSON output, timeouts, and subprocess cleanup.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mccoy.codex_runner import run_codex_fix
from mccoy.models import Finding, Severity


def _finding() -> Finding:
    return Finding(
        rule_id="MCC001",
        tool="demo",
        severity=Severity.HIGH,
        message="injection",
        fix_hint="remove it",
    )


def _fake_process(lines: list[bytes], *, pid: int = 99) -> MagicMock:
    """A fake asyncio subprocess whose stdout yields *lines* then EOF."""
    proc = MagicMock()
    proc.pid = pid
    proc.returncode = None

    stdout = MagicMock()

    async def readline() -> bytes:
        return lines.pop(0) if lines else b""

    stdout.readline = readline
    proc.stdout = stdout

    async def wait() -> int:
        proc.returncode = 0
        return 0

    proc.wait = wait
    proc.kill = MagicMock()
    return proc


@pytest.mark.anyio
async def test_run_codex_fix_skips_non_json_lines(tmp_path: Path) -> None:
    # R3: codex emits non-JSON lines (progress/warnings); the runner must skip them, not crash.
    lines = [
        b"starting codex...\n",  # not JSON
        b'{"type": "turn.completed", "thread_id": "t-1"}\n',
    ]
    proc = _fake_process(lines)
    with patch("mccoy.codex_runner.shutil.which", return_value="/usr/local/bin/codex"), patch(
        "asyncio.create_subprocess_exec", new=AsyncMock(return_value=proc)
    ):
        outcome = await run_codex_fix(_finding(), tmp_path)

    assert outcome.success is True
    assert outcome.thread_id == "t-1"
    assert outcome.error is None


@pytest.mark.anyio
async def test_run_codex_fix_times_out_and_kills_process(tmp_path: Path) -> None:
    # R3: a hung codex must be killed, not leaked. The timeout turns into outcome.error, no raise.
    proc = MagicMock()
    proc.returncode = None
    killed = {"yes": False}

    async def slow_readline() -> bytes:
        await asyncio.sleep(100)  # exceeds the 0.01s timeout below
        return b""

    proc.stdout = MagicMock(readline=slow_readline)

    async def wait() -> int:
        proc.returncode = -9
        return -9

    proc.wait = wait

    def kill() -> None:
        killed["yes"] = True
        proc.returncode = -9

    proc.kill = kill

    with patch("mccoy.codex_runner.shutil.which", return_value="/usr/local/bin/codex"), patch(
        "asyncio.create_subprocess_exec", new=AsyncMock(return_value=proc)
    ):
        outcome = await run_codex_fix(_finding(), tmp_path, timeout=0.01)

    assert outcome.success is False
    assert outcome.error == "Codex timed out"
    assert killed["yes"] is True  # the subprocess was reaped, not leaked


@pytest.mark.anyio
async def test_run_codex_fix_absent_codex_returns_install_hint(tmp_path: Path) -> None:
    # B10: codex missing is a clean degraded outcome, not a crash.
    with patch("mccoy.codex_runner.shutil.which", return_value=None):
        outcome = await run_codex_fix(_finding(), tmp_path)

    assert outcome.success is False
    assert "Codex CLI required" in (outcome.error or "")
