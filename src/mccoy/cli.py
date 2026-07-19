"""Command-line interface for McCoy."""

from __future__ import annotations

import asyncio
import contextlib
import shutil
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Annotated, Any

import typer

from mccoy.connect import connect_stdio
from mccoy.fix_loop import run_fix_loop
from mccoy.scanner import scan_with_advisory

CODEX_INSTALL_HINT = "Codex CLI required; install from https://developers.openai.com/codex/"

app = typer.Typer(
    help="Scan MCP servers and help fix deterministic tool-surface findings.",
    epilog="Exit codes: 0 clean, 2 unresolved findings, 3 infrastructure/tooling error.",
    no_args_is_help=True,
)


@app.command(name="scan")
def scan_server(server: Path, timeout: float = 30) -> None:
    """Scan a Python stdio MCP server and report deterministic findings."""

    async def run() -> int:
        async with connect_stdio("python", [str(server)], timeout=timeout) as session:
            result = await scan_with_advisory(session, timeout)
        for finding in result.findings:
            typer.echo(
                f"{finding.severity.upper()} {finding.rule_id} {finding.tool}: {finding.message}"
            )
        typer.echo(f"{len(result.findings)} finding(s) across {result.tools_scanned} tool(s)")
        return 0 if result.is_clean else 2

    try:
        raise typer.Exit(asyncio.run(run()))
    except typer.Exit:
        raise
    except Exception as error:
        typer.echo(f"Infrastructure error: {error}", err=True)
        raise typer.Exit(3) from error


@app.command()
def fix(
    server: Path,
    project: Annotated[
        Path | None,
        typer.Option(help="Project dir Codex edits; defaults to the server's parent."),
    ] = None,
    max_rounds: Annotated[int, typer.Option("--max-rounds")] = 3,
    timeout: Annotated[float, typer.Option("--timeout")] = 30.0,
    codex_timeout: Annotated[float, typer.Option("--codex-timeout")] = 120.0,
) -> None:
    """Scan, drive Codex to fix each open finding, and re-scan until green or capped.

    Operates on a copy of ``--project`` so the original files are never mutated. Requires the
    judge's own ``codex`` CLI (BYO install); exits 3 with an install hint when Codex is missing.
    """

    project_dir = project if project is not None else server.resolve().parent

    @contextlib.asynccontextmanager
    async def session_factory(work_dir: Path) -> AsyncIterator[Any]:
        target = _fixture_path_under(work_dir, server)
        async with connect_stdio("uv", ["run", "python", str(target)], timeout=timeout) as session:
            yield session

    async def run() -> int:
        outcome = await run_fix_loop(
            session_factory,
            project_dir,
            max_rounds=max_rounds,
            timeout=timeout,
            codex_timeout=codex_timeout,
        )
        for finding in outcome.final.findings:
            typer.echo(
                f"{'RESOLVED' if finding.resolved else 'OPEN'} {finding.rule_id} "
                f"{finding.tool}: {finding.message}"
            )
        typer.echo(
            f"{len(outcome.final.findings)} finding(s) across {outcome.final.tools_scanned} "
            f"tool(s); {outcome.rounds_run} round(s)"
        )
        if outcome.final.is_clean:
            return 0
        # R4: distinct exit codes — unresolved findings are 2; a missing Codex CLI is an
        # infra/tooling error (3) but only when there is work to do (a clean run already exited 0).
        if not shutil.which("codex"):
            typer.echo(CODEX_INSTALL_HINT, err=True)
            return 3
        return 2

    try:
        raise typer.Exit(asyncio.run(run()))
    except typer.Exit:
        raise
    except Exception as error:
        typer.echo(f"Infrastructure error: {error}", err=True)
        raise typer.Exit(3) from error


def _fixture_path_under(work_dir: Path, server: Path) -> Path:
    """Resolve the fixture inside *work_dir* that corresponds to *server*.

    McCoy runs on a copy of the project; the re-scan must launch the copy, not the original.
    Falls back to *server* itself when the copy does not contain it (e.g. project outside repo).
    """
    resolved = server.resolve()
    relative = _try_relative(resolved, _project_root(server))
    if relative is not None and (work_dir / relative).exists():
        return work_dir / relative
    return resolved


def _try_relative(path: Path, base: Path) -> Path | None:
    try:
        return path.relative_to(base)
    except ValueError:
        return None


def _project_root(server: Path) -> Path:
    """Best-effort project root for relative resolution (the fixture's nearest package dir)."""
    return server.resolve().parent


@app.callback()
def main() -> None:
    """McCoy command line."""
