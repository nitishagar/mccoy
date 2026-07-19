"""Tests for the McCoy CLI — exit-code contract (R4) and command surface.

The scan command is the primary user surface, so its 0/2/3 exit codes are the machine-checkable
green state (R4). These drive the real CLI via CliRunner against the shipped fixtures.
"""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from mccoy.cli import app

VULN = Path("fixtures/vuln_server/server.py")
CLEAN = Path("fixtures/vuln_server/clean_server.py")


def test_help_lists_commands_and_exit_contract() -> None:
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "scan" in result.output
    assert "fix" in result.output
    assert "Exit codes" in result.output


def test_scan_cli_exits_0_on_clean_server() -> None:
    # R4: a clean server must exit 0 (the machine-checkable green state).
    result = CliRunner().invoke(app, ["scan", str(CLEAN)])

    assert result.exit_code == 0
    assert "100/100" in result.output  # clean server scores 100


def test_scan_cli_exits_2_on_findings() -> None:
    # R4: unresolved deterministic findings exit 2.
    result = CliRunner().invoke(app, ["scan", str(VULN)])

    assert result.exit_code == 2
    assert "MCC001" in result.output


def test_scan_cli_exits_3_on_infrastructure_error() -> None:
    # R4: a server that cannot start is an infrastructure error → exit 3.
    result = CliRunner().invoke(app, ["scan", "/does/not/exist/server.py"])

    assert result.exit_code == 3
    assert "Infrastructure error" in result.output


def test_scan_cli_emits_graded_report() -> None:
    # F6: the scan command renders the graded terminal report (score + findings), not raw echo.
    result = CliRunner().invoke(app, ["scan", str(VULN)])

    assert "McCoy score:" in result.output
    assert "MCC001" in result.output
