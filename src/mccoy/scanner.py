"""Deterministic live MCP scanning pipeline."""

from __future__ import annotations

import asyncio
import os
from typing import Any

from mccoy.llm import apply_advisories
from mccoy.models import Finding, ScanResult, Severity
from mccoy.rules import run_rules


async def scan(session: Any, timeout: float = 30) -> ScanResult:
    result = await asyncio.wait_for(session.list_tools(), timeout)
    tools = list(getattr(result, "tools", []) or [])
    return _scan_tools(tools)


async def scan_with_advisory(
    session: Any, timeout: float = 30, *, client: Any = None, max_calls: int = 50
) -> ScanResult:
    result = await asyncio.wait_for(session.list_tools(), timeout)
    tools = list(getattr(result, "tools", []) or [])
    scan_result = _scan_tools(tools)
    if not os.getenv("OPENAI_API_KEY"):
        scan_result.metadata["advisory"] = "skipped (OPENAI_API_KEY unset)"
        return scan_result

    # A1: advisories are presentation-only and must never affect the deterministic verdict.
    scan_result.metadata["advisory"] = await apply_advisories(
        tools, scan_result.findings, max_calls=max_calls, client=client
    )
    return scan_result


def _scan_tools(tools: list[Any]) -> ScanResult:
    return ScanResult(
        findings=[finding for tool in tools for finding in run_rules(tool)],
        tools_scanned=len(tools),
        metadata={"advisory": "not run"},
    )


def scan_tools(tools: list[Any]) -> ScanResult:
    return _scan_tools(tools)


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
