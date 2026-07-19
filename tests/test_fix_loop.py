"""Tests for the Codex fix-and-verify loop.

Codex is not installed in CI, so every test injects a fake ``run_codex_fix`` (per the plan's
"do NOT shell out to codex" mandate). The scanner itself is NOT mocked: each round scans a real
FastMCP server rebuilt from the (Codex-edited) fixture copy, so the red→green contract is genuine.
"""

from __future__ import annotations

import importlib.util
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from mccoy.codex_runner import FixOutcome
from mccoy.fix_loop import run_fix_loop

FIXTURE = Path("fixtures/vuln_server/server.py")

CLEAN_SOURCE = '''"""Cleaned fixture after a successful Codex fix round."""

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict

mcp = FastMCP("McCoy fixed fixture")


class _Input(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str


@mcp.tool(description="Return the requested record by id.")
def safe_lookup(data: _Input) -> str:
    return data.query


if __name__ == "__main__":
    mcp.run()
'''


def _load_server(work_dir: Path) -> Any:
    """Import the fixture living in *work_dir* and return its FastMCP server object."""
    target = work_dir / "server.py"
    spec = importlib.util.spec_from_file_location(f"mccoy_fix_fixture_{id(work_dir)}", target)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.mcp


@asynccontextmanager
async def _in_memory_session(work_dir: Path) -> AsyncIterator[Any]:
    """Re-build the server from *work_dir* each call so re-scan reflects Codex's edits."""
    server = _load_server(work_dir)
    async with create_connected_server_and_client_session(server) as session:
        await session.initialize()
        yield session


class _Factory:
    """session_factory that records the work_dir it was last opened against."""

    def __init__(self) -> None:
        self.work_dir: Path | None = None
        self.opened = 0

    @asynccontextmanager
    async def __call__(self, work_dir: Path) -> AsyncIterator[Any]:
        self.work_dir = work_dir
        self.opened += 1
        async with _in_memory_session(work_dir) as session:
            yield session


async def _outcome_success(_finding: Any, _project: Path, **_kw: Any) -> FixOutcome:
    return FixOutcome(success=True, thread_id="t-1", patch_applied=True)


async def _outcome_codex_missing(_finding: Any, _project: Path, **_kw: Any) -> FixOutcome:
    return FixOutcome(error="Codex CLI required; install from https://developers.openai.com/codex/")


@pytest.mark.anyio
async def test_fix_loop_red_to_green_on_three_types(tmp_path: Path) -> None:
    project = tmp_path / "proj"
    project.mkdir()
    (project / "server.py").write_text(FIXTURE.read_text())

    # First scan is red across >=3 rule types; the fake Codex rewrites the fixture copy to clean.
    rewritten = {"done": False}

    async def fixing_runner(_finding: Any, work_dir: Path, **_kw: Any) -> FixOutcome:
        if not rewritten["done"]:
            (work_dir / "server.py").write_text(CLEAN_SOURCE)
            rewritten["done"] = True
        return FixOutcome(success=True, thread_id="thread-abc", patch_applied=True)

    factory = _Factory()
    outcome = await run_fix_loop(factory, project, max_rounds=3, fix_runner=fixing_runner)

    assert outcome.final.is_clean
    assert outcome.rounds_run >= 1
    # The fake Codex rewrites the fixture on its first call in round 1, then the round-2 re-scan
    # sees a clean server — so the loop captured at least one real thread id.
    assert outcome.thread_ids, "expected at least one codex thread id"
    assert all(tid == "thread-abc" for tid in outcome.thread_ids)
    # The original fixture (the project copy) is untouched — Codex edited the loop's work_dir.
    assert (project / "server.py").read_text() == FIXTURE.read_text()
    assert (outcome.work_dir / "server.py").read_text() == CLEAN_SOURCE


@pytest.mark.anyio
async def test_fix_loop_noop_on_green(tmp_path: Path) -> None:
    project = tmp_path / "clean_proj"
    project.mkdir()
    (project / "server.py").write_text(CLEAN_SOURCE)

    invoked = {"count": 0}

    async def runner(_finding: Any, _project: Path, **_kw: Any) -> FixOutcome:
        invoked["count"] += 1
        return FixOutcome(success=True)

    outcome = await run_fix_loop(_Factory(), project, max_rounds=3, fix_runner=runner)

    assert outcome.final.is_clean
    assert outcome.rounds_run == 0  # R2: clean input never invokes Codex
    assert invoked["count"] == 0


@pytest.mark.anyio
async def test_fix_loop_graceful_on_codex_failure(tmp_path: Path) -> None:
    project = tmp_path / "proj"
    project.mkdir()
    (project / "server.py").write_text(FIXTURE.read_text())

    async def failing_runner(_finding: Any, _project: Path, **_kw: Any) -> FixOutcome:
        return FixOutcome(success=False, error="codex crashed")

    outcome = await run_fix_loop(
        _Factory(), project, max_rounds=1, fix_runner=failing_runner
    )

    assert outcome.rounds_run == 1
    assert not outcome.final.is_clean
    assert all(f.fix_attempted for f in outcome.final.findings)
    assert not any(f.resolved for f in outcome.final.findings)


@pytest.mark.anyio
async def test_fix_loop_respects_max_rounds(tmp_path: Path) -> None:
    project = tmp_path / "proj"
    project.mkdir()
    (project / "server.py").write_text(FIXTURE.read_text())

    calls = {"rounds": 0}

    async def no_progress_runner(finding: Any, _project: Path, **_kw: Any) -> FixOutcome:
        # Mark resolved on the finding object so we can count how many the loop actually tried,
        # but never edit the source — the re-scan keeps finding it red, so the cap must stop us.
        calls["rounds"] += 1
        return FixOutcome(success=True, thread_id=None, patch_applied=False)

    outcome = await run_fix_loop(
        _Factory(), project, max_rounds=2, fix_runner=no_progress_runner
    )

    # R3: the hard cap holds even when fixes "succeed" but change nothing in the source.
    assert outcome.rounds_run == 2


@pytest.mark.anyio
async def test_fix_loop_marks_fix_attempted_on_missing_codex(tmp_path: Path) -> None:
    project = tmp_path / "proj"
    project.mkdir()
    (project / "server.py").write_text(FIXTURE.read_text())

    outcome = await run_fix_loop(
        _Factory(), project, max_rounds=1, fix_runner=_outcome_codex_missing
    )

    assert not outcome.final.is_clean
    assert all(f.fix_attempted for f in outcome.final.findings)
    assert not any(f.resolved for f in outcome.final.findings)


def test_fix_loop_cli_codex_absent_exits_three(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The CLI exits 3 (infra) — not 2 — when Codex is missing and findings remain (R4/B10)."""
    from typer.testing import CliRunner

    from mccoy.cli import app

    project = tmp_path / "proj"
    project.mkdir()
    (project / "server.py").write_text(FIXTURE.read_text())

    monkeypatch.setattr("shutil.which", lambda _cmd: None)
    monkeypatch.setattr(
        "mccoy.fix_loop.run_codex_fix",
        lambda *a, **k: _outcome_codex_missing(*a, **k),
    )

    result = CliRunner().invoke(
        app,
        ["fix", str(project / "server.py"), "--project", str(project), "--max-rounds", "1"],
    )
    assert result.exit_code == 3
    assert "Codex CLI required" in result.output


def test_fix_loop_cli_exits_zero_on_green(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A clean fixture exits 0 without ever invoking Codex (R2 + R4)."""
    from typer.testing import CliRunner

    from mccoy.cli import app

    project = tmp_path / "proj"
    project.mkdir()
    (project / "server.py").write_text(CLEAN_SOURCE)

    invoked = {"n": 0}

    async def runner(*_a: Any, **_k: Any) -> FixOutcome:
        invoked["n"] += 1
        return FixOutcome(success=True)

    monkeypatch.setattr("mccoy.fix_loop.run_codex_fix", runner)
    result = CliRunner().invoke(
        app, ["fix", str(project / "server.py"), "--project", str(project)]
    )
    assert result.exit_code == 0
    assert invoked["n"] == 0
