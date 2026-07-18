"""Command-line interface for McCoy."""

from __future__ import annotations

import asyncio
from pathlib import Path

import typer

from mccoy.connect import connect_stdio
from mccoy.scanner import scan

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
            result = await scan(session, timeout)
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
def fix() -> None:
    """Fix findings and re-scan (implemented in Phase 4)."""
    typer.echo("Fix loop is not configured yet.")


@app.callback()
def main() -> None:
    """McCoy command line."""
