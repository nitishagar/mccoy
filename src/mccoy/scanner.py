"""Deterministic live MCP scanning pipeline."""

from __future__ import annotations

import asyncio
from typing import Any

from mccoy.models import Finding, ScanResult, Severity
from mccoy.rules import run_rules


async def scan(session: Any, timeout: float = 30) -> ScanResult:
    result = await asyncio.wait_for(session.list_tools(), timeout)
    tools = list(getattr(result, "tools", []) or [])
    return ScanResult(
        findings=[finding for tool in tools for finding in run_rules(tool)],
        tools_scanned=len(tools),
        metadata={"advisory": "not run"},
    )


def scan_tools(tools: list[Any]) -> ScanResult:
    return ScanResult(
        findings=[finding for tool in tools for finding in run_rules(tool)],
        tools_scanned=len(tools),
        metadata={"advisory": "not run"},
    )


def infra_result(error: Exception) -> ScanResult:
    return ScanResult(
        findings=[
            Finding(
                rule_id="MCC-INFRA",
                tool="connection",
                severity=Severity.HIGH,
                message=str(error),
                fix_hint="Fix the MCP server connection before scanning.",
            )
        ],
        metadata={"infra_error": True},
    )
