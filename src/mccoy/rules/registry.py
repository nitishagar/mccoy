"""Pure deterministic rules for MCP tool definitions."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from mccoy.models import Finding, Severity

Rule = Callable[[Any], list[Finding]]


def _value(tool: Any, field: str, default: Any = None) -> Any:
    return getattr(tool, field, default) if not isinstance(tool, dict) else tool.get(field, default)


def _text(tool: Any) -> str:
    return str(_value(tool, "description", "") or "")


def _schema(tool: Any) -> dict[str, Any]:
    raw = _value(tool, "inputSchema", _value(tool, "input_schema", {}))
    return raw if isinstance(raw, dict) else {}


def _finding(tool: Any, rule_id: str, severity: Severity, message: str, hint: str) -> Finding:
    return Finding(
        rule_id=rule_id,
        tool=str(_value(tool, "name", "unnamed")),
        severity=severity,
        message=message,
        fix_hint=hint,
    )


def injection_markers(tool: Any) -> list[Finding]:
    text = _text(tool).lower()
    markers = ("ignore previous", "system message", "developer instruction", "jailbreak")
    return (
        [
            _finding(
                tool,
                "MCC001",
                Severity.HIGH,
                "Description contains an instruction-injection marker.",
                "Remove instruction-like prose from the tool description.",
            )
        ]
        if any(marker in text for marker in markers)
        else []
    )


def open_schema(tool: Any) -> list[Finding]:
    schema = _schema(tool)
    return (
        [
            _finding(
                tool,
                "MCC002",
                Severity.MEDIUM,
                "Input schema does not forbid unknown properties.",
                "Set additionalProperties to false in the input schema.",
            )
        ]
        if schema and schema.get("additionalProperties") is not False
        else []
    )


def secret_reference(tool: Any) -> list[Finding]:
    text = f"{_text(tool)} {_schema(tool)}".lower()
    return (
        [
            _finding(
                tool,
                "MCC003",
                Severity.HIGH,
                "Tool definition exposes a secret-looking reference.",
                "Remove secret names and require secrets from secure runtime configuration.",
            )
        ]
        if any(token in text for token in ("api_key", "api-key", "secret", "password", "token="))
        else []
    )


def broad_scope(tool: Any) -> list[Finding]:
    text = _text(tool).lower()
    return (
        [
            _finding(
                tool,
                "MCC004",
                Severity.MEDIUM,
                "Tool description indicates unrestricted access.",
                "Narrow the operation to explicit resources and actions.",
            )
        ]
        if any(
            token in text
            for token in ("any file", "all files", "unrestricted", "arbitrary command")
        )
        else []
    )


def public_bind(tool: Any) -> list[Finding]:
    return (
        [
            _finding(
                tool,
                "MCC005",
                Severity.MEDIUM,
                "Tool description advertises a 0.0.0.0 bind.",
                "Bind only to localhost unless public exposure is intentional.",
            )
        ]
        if "0.0.0.0" in _text(tool)
        else []
    )


def hidden_unicode(tool: Any) -> list[Finding]:
    text = _text(tool)
    return (
        [
            _finding(
                tool,
                "MCC006",
                Severity.HIGH,
                "Description contains hidden Unicode controls.",
                "Remove directional and zero-width Unicode controls.",
            )
        ]
        if any("\u200b" <= char <= "\u200f" or "\u202a" <= char <= "\u202e" for char in text)
        else []
    )


def mutable_description(tool: Any) -> list[Finding]:
    text = _text(tool).lower()
    return (
        [
            _finding(
                tool,
                "MCC007",
                Severity.MEDIUM,
                "Description permits runtime mutation.",
                "Make tool descriptions versioned and immutable at runtime.",
            )
        ]
        if "runtime description" in text or "change description" in text
        else []
    )


def unpinned_dependency(tool: Any) -> list[Finding]:
    text = f"{_text(tool)} {_schema(tool)}".lower()
    return (
        [
            _finding(
                tool,
                "MCC008",
                Severity.LOW,
                "Tool definition contains an unpinned dependency reference.",
                "Pin the dependency to a reviewed version.",
            )
        ]
        if any(token in text for token in ("latest", "@*", "unversioned"))
        else []
    )


RULES: tuple[Rule, ...] = (
    injection_markers,
    open_schema,
    secret_reference,
    broad_scope,
    public_bind,
    hidden_unicode,
    mutable_description,
    unpinned_dependency,
)


def run_rules(tool: Any) -> list[Finding]:
    return [finding for rule in RULES for finding in rule(tool)]
