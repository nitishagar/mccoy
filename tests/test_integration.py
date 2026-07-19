"""Live MCP transport integration coverage for the canonical vulnerable fixture."""

from __future__ import annotations

import asyncio
import importlib.util
import socket
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import pytest

from mccoy.connect import connect_http, connect_stdio
from mccoy.scanner import scan

FIXTURE = Path("fixtures/vuln_server/server.py")


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


async def _wait_for_port(port: int) -> None:
    for _ in range(50):
        try:
            reader, writer = await asyncio.open_connection("127.0.0.1", port)
        except OSError:
            await asyncio.sleep(0.05)
        else:
            writer.close()
            await writer.wait_closed()
            return
    raise TimeoutError("fixture HTTP server did not start")


@asynccontextmanager
async def _http_fixture() -> AsyncIterator[str]:
    spec = importlib.util.spec_from_file_location("mccoy_vuln_fixture", FIXTURE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    mcp: Any = module.mcp

    port = _free_port()
    original_settings = mcp.settings
    mcp.settings = original_settings.model_copy(update={"host": "127.0.0.1", "port": port})
    task = asyncio.create_task(mcp.run_streamable_http_async())
    try:
        await asyncio.wait_for(_wait_for_port(port), timeout=5)
        yield f"http://127.0.0.1:{port}/mcp"
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        mcp.settings = original_settings


@pytest.mark.anyio
async def test_fixture_has_at_least_five_findings_over_stdio() -> None:
    async with connect_stdio("uv", ["run", "python", str(FIXTURE)]) as session:
        result = await scan(session)

    assert len(result.findings) >= 5
    assert result.tools_scanned == 3


@pytest.mark.anyio
async def test_fixture_has_at_least_five_findings_over_http() -> None:
    async with _http_fixture() as url:
        async with connect_http(url) as session:
            result = await scan(session)

    assert len(result.findings) >= 5
    assert result.tools_scanned == 3
