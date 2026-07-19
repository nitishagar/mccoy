"""Command-line interface for McCoy."""

from __future__ import annotations

import asyncio
import contextlib
import shutil
import sys
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Annotated, Any

import typer

from mccoy.connect import connect_stdio
from mccoy.fix_loop import run_fix_loop
from mccoy.report import render_diff, render_terminal
from mccoy.scanner import scan_with_advisory

CODEX_INSTALL_HINT = "Codex CLI required; install from https://developers.openai.com/codex/"

app = typer.Typer(
    help="Scan MCP servers and help fix deterministic tool-surface findings.",
    epilog="Exit codes: 0 clean, 2 unresolved findings, 3 infrastructure/tooling error.",
    no_args_is_help=True,
)


@app.command(name="scan")
def scan_server(
    server: Path,
    timeout: Annotated[float, typer.Option("--timeout")] = 30.0,
) -> None:
    """Scan a Python stdio MCP server and report deterministic findings."""

    async def run() -> int:
        # sys.executable is the interpreter McCoy is running under — always present, no PATH
        # dependency, so the canonical judge command works on stock Linux (no bare `python`).
        async with connect_stdio(sys.executable, [str(server)], timeout=timeout) as session:
            result = await scan_with_advisory(session, timeout)
        typer.echo(render_terminal(result))
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

    Operates on a copy of ``--project`` so the original files are never mutated, then prints a
    severity-graded report and a before/after diff (F6). Requires the judge's own ``codex`` CLI
    (BYO install); exits 3 with an install hint when Codex is missing.
    """

    project_dir = project if project is not None else server.resolve().parent

    @contextlib.asynccontextmanager
    async def session_factory(work_dir: Path) -> AsyncIterator[Any]:
        target = _fixture_path_under(work_dir, server)
        async with connect_stdio(sys.executable, [str(target)], timeout=timeout) as session:
            yield session

    async def run() -> int:
        outcome = await run_fix_loop(
            session_factory,
            project_dir,
            max_rounds=max_rounds,
            timeout=timeout,
            codex_timeout=codex_timeout,
        )
        try:
            typer.echo(render_terminal(outcome.final))
            typer.echo(f"{outcome.rounds_run} round(s); edits in {outcome.work_dir}")
            # F6: before/after diff between the original server and Codex's edited copy.
            edited = _fixture_path_under(outcome.work_dir, server)
            try:
                diff = render_diff(server.resolve(), edited)
            except RuntimeError as error:
                typer.echo(f"Could not render diff: {error}", err=True)
                diff = ""
            if diff:
                typer.echo("\nBefore/after diff:")
                typer.echo(diff)
            if outcome.final.is_clean:
                return 0
            # R4: distinct exit codes — unresolved findings are 2; a missing Codex CLI is an
            # infra/tooling error (3) but only when there is work to do (clean already exited 0).
            if not shutil.which("codex"):
                typer.echo(CODEX_INSTALL_HINT, err=True)
                return 3
            return 2
        finally:
            # The loop creates the temp copy; the CLI owns its lifetime once the diff is rendered.
            outcome.cleanup()

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
    Raises ``FileNotFoundError`` if the server is not present in the copy rather than silently
    falling back to the original — a silent fallback would make the loop launch the un-edited
    fixture and never converge.
    """
    relative = _try_relative(server.resolve(), server.resolve().parent)
    candidate = work_dir / relative if relative is not None else None
    if candidate is not None and candidate.exists():
        return candidate
    raise FileNotFoundError(
        f"server {server} not found under work copy {work_dir}; pass --project as the server's "
        "parent directory so the copy includes it"
    )


def _try_relative(path: Path, base: Path) -> Path | None:
    try:
        return path.relative_to(base)
    except ValueError:
        return None


@app.callback()
def main() -> None:
    """McCoy command line."""
