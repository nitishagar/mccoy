"""Best-effort GPT-5.6 advisory classifications; never verdict inputs."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from openai import AsyncOpenAI

from mccoy.models import AdvisoryNote, Finding, Severity


async def classify_injection(
    tool: Any, finding: Finding, client: AsyncOpenAI | None = None
) -> AdvisoryNote:
    description = str(getattr(tool, "description", "") or "")
    api = client or AsyncOpenAI()
    response = await api.responses.create(
        model="gpt-5.6-luna",
        input=(
            "Is this MCP tool description benign documentation rather than a prompt injection?\n"
            f"{description}"
        ),
        text={
            "format": {
                "type": "json_schema",
                "name": "advisory",
                "schema": {
                    "type": "object",
                    "properties": {
                        "benign": {"type": "boolean"},
                        "confidence": {"type": "number"},
                        "message": {"type": "string"},
                    },
                    "required": ["benign", "confidence", "message"],
                    "additionalProperties": False,
                },
            }
        },
    )
    data = json.loads(response.output_text)
    return AdvisoryNote(
        severity=Severity.INFO if data["benign"] else None,
        confidence=float(data["confidence"]),
        message=str(data["message"]),
    )


async def apply_advisories(
    tools: list[Any],
    findings: list[Finding],
    max_calls: int = 50,
    client: AsyncOpenAI | None = None,
) -> str:
    injection = [item for item in findings if item.rule_id == "MCC001"][:max_calls]
    by_name = {str(getattr(tool, "name", "")): tool for tool in tools}

    async def classify(item: Finding) -> None:
        try:
            item.advisory = await classify_injection(by_name[item.tool], item, client)
        except Exception:
            item.advisory = AdvisoryNote(message="LLM unavailable — advisory pass skipped")

    await asyncio.gather(*(classify(item) for item in injection))
    return "completed" if injection else "not applicable"
