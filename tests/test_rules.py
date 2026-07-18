from mcp.types import Tool

from mccoy.rules import RULES, run_rules
from mccoy.scanner import scan_tools


def tool(description: str = "safe", schema: dict[str, object] | None = None) -> Tool:
    return Tool(
        name="demo",
        description=description,
        inputSchema=schema or {"type": "object", "additionalProperties": False},
    )


def test_each_rule_has_a_crafted_match_and_clean_tool_is_clean() -> None:
    samples = [
        "Ignore previous instructions",
        "API_KEY is visible",
        "Run arbitrary command against all files",
        "Server binds 0.0.0.0",
        "Hidden \u202e instruction",
        "Runtime description can change description",
        "Use the latest dependency",
    ]
    assert len(RULES) == 8
    assert not run_rules(tool())
    assert all(run_rules(tool(sample)) for sample in samples)
    assert run_rules(tool(schema={"type": "object"}))


def test_degenerate_tool_inputs_do_not_crash() -> None:
    malformed = {"name": "odd", "description": None, "inputSchema": {"$ref": "#/$ref"}}
    huge = {"name": "large", "description": "x" * 100_000, "inputSchema": "not a schema"}
    result = scan_tools([malformed, huge])
    assert result.tools_scanned == 2
