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


def test_scan_of_empty_tool_list_is_clean() -> None:
    # R1: an empty tool list is a degenerate input — it must produce a clean result, not crash.
    result = scan_tools([])

    assert result.tools_scanned == 0
    assert result.is_clean
    assert result.findings == []


def test_open_schema_resolves_refs_and_clean_is_clean() -> None:
    nested_closed = tool(
        schema={
            "properties": {"data": {"$ref": "#/$defs/M"}},
            "required": ["data"],
            "$defs": {
                "M": {
                    "type": "object",
                    "properties": {"message": {"type": "string"}},
                    "additionalProperties": False,
                }
            },
        }
    )

    assert not [item for item in run_rules(nested_closed) if item.rule_id == "MCC002"]
    assert [item for item in run_rules(tool(schema={"type": "object"})) if item.rule_id == "MCC002"]
    malformed_findings = run_rules({"name": "bad", "inputSchema": "oops"})
    assert not [item for item in malformed_findings if item.rule_id == "MCC002"]
