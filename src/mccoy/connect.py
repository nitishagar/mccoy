"""Bounded MCP transport connections."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.streamable_http import streamablehttp_client


@asynccontextmanager
async def _session(streams: Any, timeout: float) -> AsyncIterator[ClientSession]:
    async with streams as (read_stream, write_stream, *_):
        async with ClientSession(read_stream, write_stream) as session:
            await asyncio.wait_for(session.initialize(), timeout)
            yield session


@asynccontextmanager
async def connect_stdio(
    command: str, args: list[str], env: dict[str, str] | None = None, timeout: float = 30
) -> AsyncIterator[ClientSession]:
    params = StdioServerParameters(command=command, args=args, env=env)
    async with _session(stdio_client(params), timeout) as session:
        yield session


@asynccontextmanager
async def connect_http(url: str, timeout: float = 30) -> AsyncIterator[ClientSession]:
    async with _session(streamablehttp_client(url, timeout=timeout), timeout) as session:
        yield session
